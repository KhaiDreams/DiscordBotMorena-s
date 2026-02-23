import discord
from discord.ext import commands
import asyncio
import os
import tempfile
from gtts import gTTS
from collections import defaultdict

# Dicionário para rastrear quem chamou o bot em cada servidor
tts_callers = {}
# Dicionário para rastrear os canais de texto associados
tts_text_channels = {}

def setup_tts_commands(bot):
    """Registra comandos de TTS no bot"""
    
    @bot.command(name="call")
    async def call_tts(ctx: commands.Context):
        """Bot entra na call e lê mensagens do chat em voz alta"""
        # Verifica se o usuário está em um canal de voz
        if not ctx.author.voice:
            await ctx.send("❌ Você precisa estar em um canal de voz para usar este comando!")
            return
        
        voice_channel = ctx.author.voice.channel
        
        # Verifica se o bot já está conectado em algum canal de voz neste servidor
        if ctx.guild.voice_client:
            await ctx.send("❌ Já estou em um canal de voz! Use `.leave` para me desconectar primeiro.")
            return
        
        try:
            # Conecta ao canal de voz com configurações otimizadas
            voice_client = await voice_channel.connect(
                timeout=60.0, 
                reconnect=True,
                self_deaf=False,
                self_mute=False
            )
            print(f"[TTS] Conectado ao canal de voz '{voice_channel.name}'")
            
            # Registra quem chamou o bot e o canal de texto
            tts_callers[ctx.guild.id] = ctx.author.id
            tts_text_channels[ctx.guild.id] = ctx.channel.id
            
            await ctx.send(f"Conectado ao canal de voz **{voice_channel.name}**! Vou ler todas as mensagens deste chat em voz alta. Sairei quando você sair da call.")
            
            # Inicia o monitoramento da presença do usuário
            bot.loop.create_task(monitor_caller_presence(bot, ctx.guild.id, ctx.author.id, voice_channel.id))
            
        except discord.ClientException as e:
            print(f"[TTS] Erro ao conectar: {e}")
            await ctx.send(f"❌ Já estou conectado em outro lugar ou houve um erro de cliente: {e}")
        except asyncio.TimeoutError:
            print(f"[TTS] Timeout ao conectar")
            await ctx.send(f"❌ Timeout ao tentar conectar ao canal de voz. Tente novamente.")
        except Exception as e:
            print(f"[TTS] Erro ao conectar: {type(e).__name__} - {e}")
            await ctx.send(f"❌ Erro ao conectar ao canal de voz: {type(e).__name__}")
    
    @bot.command(name="leave")
    async def leave_voice(ctx: commands.Context):
        """Bot sai do canal de voz"""
        if not ctx.guild.voice_client:
            await ctx.send("❌ Não estou em nenhum canal de voz!")
            return
        
        # Remove registros ANTES de desconectar
        if ctx.guild.id in tts_callers:
            del tts_callers[ctx.guild.id]
        if ctx.guild.id in tts_text_channels:
            del tts_text_channels[ctx.guild.id]
        
        try:
            await ctx.guild.voice_client.disconnect(force=True)
            print("[TTS] Desconectado do canal de voz")
            await ctx.send("👋 Saí do canal de voz!")
        except Exception as e:
            print(f"[TTS] Erro ao desconectar: {e}")
            await ctx.send(f"❌ Erro ao desconectar: {e}")

async def process_tts_message(message):
    """Processa mensagem para TTS se aplicável"""
    # Ignora mensagens do próprio bot
    if message.author.bot:
        return
    
    # Ignora mensagens sem servidor (DMs)
    if not message.guild:
        return
    
    # Verifica se este servidor tem TTS ativo
    if message.guild.id in tts_callers:
        # Verifica se a mensagem é do canal de texto correto
        if message.channel.id == tts_text_channels.get(message.guild.id):
            voice_client = message.guild.voice_client
            
            # Verifica se o bot está conectado
            if voice_client and voice_client.is_connected():
                # Ignora comandos
                if not message.content.startswith('.') and not message.content.startswith('/'):
                    await speak_message(voice_client, message.author.display_name, message.content)

async def monitor_caller_presence(bot, guild_id, caller_id, voice_channel_id):
    """Monitora se a pessoa que chamou o bot ainda está no canal de voz"""
    await asyncio.sleep(2)  # Aguarda um pouco antes de começar a monitorar
    
    while guild_id in tts_callers:
        await asyncio.sleep(5)  # Verifica a cada 5 segundos
        
        guild = bot.get_guild(guild_id)
        if not guild:
            break
        
        voice_client = guild.voice_client
        if not voice_client or not voice_client.is_connected():
            # Bot foi desconectado manualmente
            if guild_id in tts_callers:
                del tts_callers[guild_id]
            if guild_id in tts_text_channels:
                del tts_text_channels[guild_id]
            break
        
        # Busca o canal de voz
        voice_channel = guild.get_channel(voice_channel_id)
        if not voice_channel:
            break
        
        # Verifica se o caller ainda está no canal
        caller = guild.get_member(caller_id)
        if not caller or not caller.voice or caller.voice.channel.id != voice_channel_id:
            # O caller saiu, desconectar o bot
            text_channel_id = tts_text_channels.get(guild_id)
            
            if guild_id in tts_callers:
                del tts_callers[guild_id]
            if guild_id in tts_text_channels:
                del tts_text_channels[guild_id]
            
            try:
                await voice_client.disconnect()
            except:
                pass
            
            # Tenta enviar mensagem no canal de texto
            if text_channel_id:
                text_channel = guild.get_channel(text_channel_id)
                if text_channel:
                    try:
                        await text_channel.send("👋 O usuário que me chamou saiu da call, então estou saindo também!")
                    except:
                        pass
            break

async def speak_message(voice_client, author_name, content):
    """Converte texto em fala e toca no canal de voz"""
    # Limita o tamanho da mensagem
    if len(content) > 200:
        content = content[:197] + "..."
    
    # Ignora mensagens vazias
    if not content.strip():
        return
    
    # Cria o texto a ser falado
    texto_fala = content
    
    temp_filename = None
    try:
        # Cria arquivo temporário para o áudio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_filename = temp_file.name
        
        # Gera o áudio com gTTS (Google Text-to-Speech)
        tts = gTTS(text=texto_fala, lang='pt', slow=False)
        tts.save(temp_filename)
        
        # Aguarda se já estiver tocando algo
        while voice_client.is_playing():
            await asyncio.sleep(0.5)
        
        # Toca o áudio
        audio_source = discord.FFmpegPCMAudio(temp_filename)
        
        def after_playing(error):
            """Callback após terminar de tocar"""
            if error:
                print(f"[TTS] Erro ao tocar áudio: {error}")
            
            try:
                if temp_filename and os.path.exists(temp_filename):
                    os.remove(temp_filename)
            except Exception as e:
                print(f"[TTS] Erro ao remover arquivo: {e}")
        
        voice_client.play(audio_source, after=after_playing)
        
    except Exception as e:
        print(f"[TTS] Erro ao gerar/tocar TTS: {e}")
        # Limpa o arquivo temporário em caso de erro
        try:
            if temp_filename and os.path.exists(temp_filename):
                os.remove(temp_filename)
        except:
            pass
