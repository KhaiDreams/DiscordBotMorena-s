import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import random
import datetime
import json

# Carrega variáveis do .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configurações do bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

# Caminho para o JSON dos sorteios
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

@tasks.loop(minutes=1)
async def checar_sorteios():
    agora = datetime.datetime.now()
    sorteios = carregar_sorteios()
    atualizados = []

    for sorteio in sorteios:
        if sorteio["feito"]:
            atualizados.append(sorteio)
            continue

        data_sorteio = datetime.datetime.strptime(sorteio["data"], "%d/%m/%Y %H:%M")
        if agora >= data_sorteio:
            if not sorteio["participantes"]:
                sorteio["feito"] = True
                atualizados.append(sorteio)
                continue

            ganhador = random.choice(sorteio["participantes"])
            canal = bot.get_channel(sorteio["canal_id"])
            if canal:
                embed = discord.Embed(
                    title=f"🎉 Resultado do Sorteio: {sorteio['titulo']}",
                    description=f"O grande ganhador é: **{ganhador}** 🎊",
                    color=discord.Color.gold()
                )
                embed.set_footer(text=f"Sorteio realizado em {agora.strftime('%d/%m/%Y %H:%M')}")
                await canal.send(embed=embed)
            sorteio["feito"] = True
        atualizados.append(sorteio)

    salvar_sorteios(atualizados)

@bot.command()
async def sortear(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("📛 Envia o **título** do sorteio:")
    titulo_msg = await bot.wait_for("message", check=check, timeout=60.0)
    titulo = titulo_msg.content.strip()

    await ctx.send("✍️ Manda a lista de participantes (1 por linha):")
    participantes_msg = await bot.wait_for("message", check=check, timeout=120.0)
    participantes = [p.strip() for p in participantes_msg.content.split("\n") if p.strip()]

    await ctx.send("🕒 Agora manda a data do sorteio no formato `DD/MM/AAAA HH:MM` (ex: `28/05/2025 18:00`):")
    data_msg = await bot.wait_for("message", check=check, timeout=60.0)
    try:
        data = datetime.datetime.strptime(data_msg.content.strip(), "%d/%m/%Y %H:%M")
    except ValueError:
        await ctx.send("❌ Formato de data inválido. Tenta de novo usando `DD/MM/AAAA HH:MM`.")
        return

    sorteios = carregar_sorteios()
    sorteios.append({
        "titulo": titulo,
        "participantes": participantes,
        "data": data.strftime("%d/%m/%Y %H:%M"),
        "feito": False,
        "canal_id": ctx.channel.id
    })
    salvar_sorteios(sorteios)

    embed = discord.Embed(
        title="📢 Sorteio Criado!",
        description=f"**Título:** {titulo}\n📅 Data: {data.strftime('%d/%m/%Y %H:%M')}\n👥 Participantes: {len(participantes)}",
        color=discord.Color.green()
    )
    embed.set_footer(text="O resultado será postado aqui automaticamente. Boa sorte! 🍀")
    await ctx.send(embed=embed)

@bot.command()
async def sorteios(ctx):
    sorteios = carregar_sorteios()
    if not sorteios:
        await ctx.send("❌ Nenhum sorteio foi criado ainda.")
        return

    embed = discord.Embed(title="📜 Lista de Sorteios", color=discord.Color.purple())

    for s in sorteios:
        embed.add_field(
            name=f"{'✅' if s['feito'] else '🕓'} {s['titulo']}",
            value=f"Data: {s['data']}\nParticipantes: {len(s['participantes'])}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('Bot is readyy!')
    print('------')
    checar_sorteios.start()  # aqui inicia o loop que verifica os sorteios

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

# .escolha - agora com embed lindona e mensagem de loading
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
            "`.escolha [@alguém]` - Escolhe uma mensagem aleatória da pessoa"
            "`.sortear` - Cria um sorteio 🎉\n"
            "`.sorteios` - Mostra a lista de sorteios criados 📜\n"
        )
        if ctx.guild:
            await ctx.reply("Te mandei no PV, confere lá! 📬")
    except discord.Forbidden:
        await ctx.reply("Não consegui te mandar DM. Tu precisa liberar as mensagens privadas do servidor. ❌")

# Inicia o bot
bot.run(TOKEN)
