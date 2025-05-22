import discord
from discord.ext import commands, tasks
from discord.ui import Modal, TextInput, View, Button
from dotenv import load_dotenv
import os
import random
import datetime
import json
import yt_dlp
import asyncio

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

ARQUIVO_SORTEIOS = "sorteios.json"

def carregar_sorteios():
    if not os.path.exists(ARQUIVO_SORTEIOS):
        with open(ARQUIVO_SORTEIOS, "w") as f:
            json.dump([], f)
    with open(ARQUIVO_SORTEIOS, "r") as f:
        return json.load(f)

def salvar_sorteios(sorteios):
    with open(ARQUIVO_SORTEIOS, "w") as f:
        json.dump(sorteios, f, indent=4)

# Variável global para guardar a mensagem com o botão
msg_com_botao = None

@tasks.loop(minutes=1)
async def checar_sorteios():
    agora = datetime.datetime.now()
    sorteios = carregar_sorteios()
    atualizados = []

    for sorteio in sorteios:
        if sorteio.get("feito"):
            atualizados.append(sorteio)
            continue

        data_sorteio = datetime.datetime.strptime(sorteio["data"], "%d/%m/%Y %H:%M")
        if agora >= data_sorteio:
            if not sorteio["participantes"]:
                sorteio["feito"] = True
                atualizados.append(sorteio)
                continue

            ganhador = random.choice(sorteio["participantes"])
            sorteio["feito"] = True
            sorteio["vencedor"] = ganhador

            canal = bot.get_channel(sorteio["canal_id"])
            if canal:
                embed = discord.Embed(
                    title=f"🎉 Resultado do Sorteio: {sorteio['titulo']}",
                    description=f"O grande ganhador é: **{ganhador}** 🎊",
                    color=discord.Color.gold()
                )
                embed.set_footer(text=f"Sorteio realizado em {agora.strftime('%d/%m/%Y %H:%M')}")
                await canal.send("@everyone", embed=embed)

        atualizados.append(sorteio)

    salvar_sorteios(atualizados)

class SorteioModal(Modal, title="🎁 Criar Novo Sorteio"):
    def __init__(self, canal_id: int):
        super().__init__(timeout=300)
        self.canal_id = canal_id

        self.titulo = TextInput(label="Título do sorteio", placeholder="Ex: Sorteio de gift card", max_length=100)
        self.participantes = TextInput(label="Participantes (1 por linha)", style=discord.TextStyle.paragraph, placeholder="Ex:\nMaria\nJoão\nCarlos")
        self.data = TextInput(label="Data (DD/MM/AAAA HH:MM)", placeholder="Ex: 28/05/2025 18:00")

        self.add_item(self.titulo)
        self.add_item(self.participantes)
        self.add_item(self.data)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            data_formatada = datetime.datetime.strptime(self.data.value.strip(), "%d/%m/%Y %H:%M")
        except ValueError:
            await interaction.response.send_message("❌ Data inválida! Use o formato DD/MM/AAAA HH:MM", ephemeral=True)
            return

        lista_participantes = [p.strip() for p in self.participantes.value.strip().split("\n") if p.strip()]
        if not lista_participantes:
            await interaction.response.send_message("❌ Adicione pelo menos um participante.", ephemeral=True)
            return

        sorteios = carregar_sorteios()
        sorteios.append({
            "titulo": self.titulo.value.strip(),
            "participantes": lista_participantes,
            "data": data_formatada.strftime("%d/%m/%Y %H:%M"),
            "feito": False,
            "canal_id": self.canal_id
        })
        salvar_sorteios(sorteios)

        embed = discord.Embed(
            title="📢 Sorteio Criado!",
            description=f"**Título:** {self.titulo.value.strip()}\n📅 Data: {data_formatada.strftime('%d/%m/%Y %H:%M')}\n👥 Participantes: {len(lista_participantes)}",
            color=discord.Color.green()
        )
        embed.set_footer(text="O resultado será postado aqui automaticamente. Boa sorte! 🍀")

        global msg_com_botao
        if msg_com_botao:
            try:
                await msg_com_botao.delete()
            except:
                pass
            msg_com_botao = None

        await interaction.response.send_message(embed=embed)

@bot.command()
async def sortear(ctx):
    global msg_com_botao
    view = View()

    async def abrir_modal_callback(interaction: discord.Interaction):
        await interaction.response.send_modal(SorteioModal(ctx.channel.id))

    botao = Button(label="Criar Sorteio 🎁", style=discord.ButtonStyle.success)
    botao.callback = abrir_modal_callback
    view.add_item(botao)

    msg_com_botao = await ctx.send("Clique no botão abaixo para abrir o painel de criação de sorteio:", view=view)

@bot.command()
async def sorteios(ctx):
    sorteios = carregar_sorteios()
    if not sorteios:
        await ctx.send("❌ Nenhum sorteio foi criado ainda.")
        return

    embed = discord.Embed(title="📜 Lista de Sorteios", color=discord.Color.purple())

    for s in sorteios:
        status = '✅ Realizado' if s.get("feito") else '🕓 Pendente'
        ganhador = f"\n🏆 Ganhador: **{s['vencedor']}**" if s.get("vencedor") else ""
        embed.add_field(
            name=f"{status} - {s['titulo']}",
            value=f"📅 Data: {s['data']}\n👥 Participantes: {len(s['participantes'])}{ganhador}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('Bot is ready!')
    print('------')
    checar_sorteios.start()

# Fila de músicas por servidor
queues = {}

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = []
    return queues[guild_id]

# Função pra tocar música da fila
async def tocar_proxima(ctx):
    queue = get_queue(ctx.guild.id)
    if not queue:
        await ctx.voice_client.disconnect()
        return

    url, title = queue.pop(0)

    ffmpeg_opts = {'options': '-vn'}

    with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info['url']

    vc = ctx.voice_client

    def depois_tocar(err):
        fut = tocar_proxima(ctx)
        fut = asyncio.run_coroutine_threadsafe(fut, bot.loop)
        try:
            fut.result()
        except Exception as e:
            print(f"Erro na fila: {e}")

    vc.play(discord.FFmpegPCMAudio(stream_url, **ffmpeg_opts), after=depois_tocar)
    await ctx.send(f"🎶 Tocando agora: **{title}**")

@bot.command()
async def musica(ctx, url: str):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.reply("⚠️ Tu precisa tá num canal de voz primeiro.")
        return

    canal = ctx.author.voice.channel
    if ctx.voice_client is None:
        await canal.connect()
    elif ctx.voice_client.channel != canal:
        await ctx.voice_client.move_to(canal)

    # Pega info da música
    with yt_dlp.YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get("title", "Música")
        url = info.get("webpage_url", url)

    queue = get_queue(ctx.guild.id)
    queue.append((url, title))

    if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
        await tocar_proxima(ctx)
    else:
        await ctx.send(f"➕ Adicionado à fila: **{title}**")

@bot.command()
async def fila(ctx):
    queue = get_queue(ctx.guild.id)
    if not queue:
        await ctx.send("📭 Fila vazia.")
    else:
        lista = "\n".join([f"{i+1}. {title}" for i, (_, title) in enumerate(queue)])
        await ctx.send(f"🎵 Fila atual:\n{lista}")

@bot.command()
async def skip(ctx):
    vc = ctx.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("⏭️ Pulando pra próxima música.")
    else:
        await ctx.send("⚠️ Não tem nada tocando agora.")

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

@bot.command()
async def gugu(ctx):
    today = datetime.date.today()
    dias_semana = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
    data_base = datetime.date(2025, 5, 8)  # Dia OFF

    calendario_linhas = []

    for i in range(7):
        dia = today + datetime.timedelta(days=i)
        delta = (dia - data_base).days
        online = delta % 2 == 1

        dia_str = dia.strftime("%d/%m")
        semana_str = dias_semana[dia.weekday()]
        status = "🟢 Online" if online else "🔴 Offline"

        # Horários aleatórios
        if online:
            acorda = datetime.time(random.randint(5, 11), random.choice([0, 15, 30, 45]))
            dorme_hora = random.randint(22, 27)  # 27 representa 3 da manhã do dia seguinte
            dorme_min = random.choice([0, 15, 30, 45])
            dorme = datetime.time(dorme_hora % 24, dorme_min)
            dorme_str = f"{dorme.strftime('%H:%M')} {'(+1)' if dorme_hora >= 24 else ''}"

            horario_str = f"🕒 {acorda.strftime('%H:%M')} até {dorme_str}"
        else:
            horario_str = "💤 Indisponível"

        # Destaque pro dia atual
        linha = f"{semana_str} ({dia_str}) → {status} | {horario_str}"
        if dia == today:
            linha = f"**{linha}**"

        calendario_linhas.append(linha)

    embed = discord.Embed(
        title="📅 Agenda Semanal do Gugu",
        description="\n\n".join(calendario_linhas),
        color=discord.Color.green()
    )
    embed.set_footer(text="Saiba onde encontrar o Gugu! (ele não pode se esconder...)")

    await ctx.reply(embed=embed)

# Carregar frases do arquivo para o .eu
with open("frases_eu.txt", "r", encoding="utf-8") as f:
    FRASES_ZOEIRA = [linha.strip() for linha in f if linha.strip()]

# Comando .eu
@bot.command()
async def eu(ctx, membro: discord.Member = None):
    alvo = membro or ctx.author  # Se ninguém for mencionado, usa quem chamou
    frase = random.choice(FRASES_ZOEIRA)
    frase_final = frase.replace("{alvo}", alvo.mention)
    await ctx.reply(frase_final)

# .escolha - agora com embed lindona, mensagem de loading e botão pro contexto
@bot.command()
async def escolha(ctx: commands.Context, membro: discord.Member = None):
    if not ctx.guild:
        await ctx.reply("Esse comando só funciona em servidor, não em DM.")
        return

    # Envia a mensagem de "loading"
    loading_msg = await ctx.reply("A Morena está procurando uma mensagem... Aguarde!! ⏳")

    alvo = membro or ctx.author
    mensagens = []

    # Limitar canais que serão verificados (exemplo: apenas canais de texto visíveis para o bot)
    for canal in ctx.guild.text_channels:
        if not canal.permissions_for(ctx.guild.me).read_message_history:
            continue

        try:
            async for msg in canal.history(limit=1000):
                if msg.author.id == alvo.id and not msg.content.startswith('.') and msg.content.strip() != '':
                    mensagens.append(msg)
        except (discord.Forbidden, discord.HTTPException):
            continue

    if not mensagens:
        await loading_msg.delete()
        await ctx.reply(f"Não achei nenhuma mensagem de {alvo.display_name} 😔")
        return

    msg_escolhida = random.choice(mensagens)

    # Cria o link direto pra mensagem
    link_mensagem = f"https://discord.com/channels/{ctx.guild.id}/{msg_escolhida.channel.id}/{msg_escolhida.id}"

    embed = discord.Embed(
        title=f"Mensagem aleatória de {alvo.display_name}",
        description=msg_escolhida.content,
        color=discord.Color.blue()
    )
    embed.set_author(name=alvo.display_name, icon_url=alvo.display_avatar.url)
    embed.set_footer(text=f"Canal: #{msg_escolhida.channel.name} • {msg_escolhida.created_at.strftime('%d/%m/%Y %H:%M')}")

    # Cria o botão com o link
    view = View()
    view.add_item(Button(label="Ver no contexto 🔍", style=discord.ButtonStyle.link, url=link_mensagem))

    await loading_msg.delete()
    await ctx.reply(embed=embed, view=view)

# .comandos - lista de comandos via DM
@bot.command()
async def comandos(ctx):
    try:
        await ctx.author.send(
            "**📋 Lista de Comandos Disponíveis:**\n\n"
            "`.oi` - O bot te dá um salve 😎\n"
            "`.rony` - Fala da novata Rony 🐢\n"
            "`.khai` - Elogia o Khai 😘\n"
            "`.gugu` - Avisos sobre quando o Gugu ficará Online 📅\n"
            "`.morena` - Sobre a mais mais (brilho✨) 😘\n"
            "`.comandos` - Manda essa lista aqui no seu PV 📬\n"
            "`.escolha [@alguém]` - Escolhe uma mensagem aleatória da pessoa\n"
            "`.sortear` - Cria um sorteio 🎉\n"
            "`.sorteios` - Mostra a lista de sorteios criados 📜\n"
            "`.eu [@alguém]` - Vai falar algo bem carinhoso para você! 🤞\n"
            "`.musica [link]` - Tocar música 🤞\n"
            "`.play - Despause \n"
            "`.pause - Pausa a música que tá tocando. ❌\n"
            "`.skip` - Pula a música atual ⏭️\n"
            "`.fila` - Ver a fila de músicas 🎵\n"
        )
        if ctx.guild:
            await ctx.reply("Te mandei no PV, confere lá! 📬")
    except discord.Forbidden:
        await ctx.reply("Não consegui te mandar DM. Tu precisa liberar as mensagens privadas do servidor. ❌")

# Inicia o bot
bot.run(TOKEN)
