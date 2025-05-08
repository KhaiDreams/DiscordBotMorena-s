import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random

# Carrega variáveis do .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configurações do bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

# Evento ao iniciar
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('Bot is ready!')
    print('------')

# .oi - dá um salve com nome
@bot.command()
async def oi(ctx: commands.Context):
    nome = ctx.author.display_name
    await ctx.reply(f"Fala tu, {nome}! 😎")

# .rony - info da Rony
@bot.command()
async def rony(ctx):
    await ctx.reply("A Rony é uma novata no Pressão, que odeia Subnautica e está começando a assistir Tartarugas Ninja. Khai ensina tudo que ela sabe!")

# .khai - info do Khai
@bot.command()
async def khai(ctx):
    await ctx.reply("Khai é o namorado da Morena, lindo e cheiroso!")

# .morena - info da Morena (corrigido)
@bot.command()
async def morena(ctx):
    await ctx.reply("Estamos falando da mais mais, a Morena! Ela é linda, cheirosa e brilha mais que tudo! ✨")

# .comandos - lista de comandos via DM
@bot.command()
async def comandos(ctx):
    try:
        await ctx.author.send(
            "**📋 Lista de Comandos Disponíveis:**\n\n"
            "`.oi` - O bot te dá um salve 😎\n"
            "`.rony` - Fala da novata Rony 🐢\n"
            "`.khai` - Elogia o Khai 😘\n"
            "`.morena` - Sobre a mais mais (brilho✨) 😘\n"
            "`.comandos` - Manda essa lista aqui no seu PV 📬\n"
            "`.escolha [@alguém]` - Escolhe uma mensagem aleatória da pessoa"
        )
        if ctx.guild:
            await ctx.reply("Te mandei no PV, confere lá! 📬")
    except discord.Forbidden:
        await ctx.reply("Não consegui te mandar DM. Tu precisa liberar as mensagens privadas do servidor. ❌")

# .escolha - agora com embed lindona e mensagem de loading
@bot.command()
async def escolha(ctx: commands.Context, membro: discord.Member = None):
    if not ctx.guild:
        await ctx.reply("Esse comando só funciona em servidor, não em DM.")
        return

    # Envia a mensagem de "loading"
    loading_msg = await ctx.reply("A Morena (mais mais) está procurando uma mensagem... Aguarde!! ⏳")

    alvo = membro or ctx.author
    mensagens = []

    # Limitar canais que serão verificados (exemplo: apenas canais de texto visíveis para o bot)
    for canal in ctx.guild.text_channels:
        if not canal.permissions_for(ctx.guild.me).read_message_history:
            continue

        try:
            # Limitar a busca para as últimas 1000 mensagens para otimizar
            async for msg in canal.history(limit=1000):  # Aqui o limite está em 1000
                if msg.author.id == alvo.id and not msg.content.startswith('.') and msg.content.strip() != '':
                    mensagens.append(msg)
        except (discord.Forbidden, discord.HTTPException):
            continue

    if not mensagens:
        await loading_msg.delete()  # Deleta a mensagem de loading
        await ctx.reply(f"Não achei nenhuma mensagem de {alvo.display_name} 😔")
        return

    msg_escolhida = random.choice(mensagens)

    embed = discord.Embed(
        title=f"Mensagem aleatória de {alvo.display_name}",
        description=msg_escolhida.content,
        color=discord.Color.blue()
    )
    embed.set_author(name=alvo.display_name, icon_url=alvo.display_avatar.url)
    embed.set_footer(text=f"Canal: #{msg_escolhida.channel.name} • {msg_escolhida.created_at.strftime('%d/%m/%Y %H:%M')}")

    # Deleta a mensagem de loading antes de enviar a mensagem final com a embed
    await loading_msg.delete()
    
    await ctx.reply(embed=embed)

# Inicia o bot
bot.run(TOKEN)
