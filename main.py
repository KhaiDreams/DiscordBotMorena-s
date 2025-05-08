import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import datetime

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
            "`.gugu` - Avisos sobre quando o Gugu ficará Online 📅\n"
            "`.morena` - Sobre a mais mais (brilho✨) 😘\n"
            "`.comandos` - Manda essa lista aqui no seu PV 📬\n"
            "`.escolha [@alguém]` - Escolhe uma mensagem aleatória da pessoa"
        )
        if ctx.guild:
            await ctx.reply("Te mandei no PV, confere lá! 📬")
    except discord.Forbidden:
        await ctx.reply("Não consegui te mandar DM. Tu precisa liberar as mensagens privadas do servidor. ❌")

# .gugu - Calendário mostrando os dias que o Gugu estará online (1 dia sim, 1 dia não)
@bot.command()
async def gugu(ctx):
    today = datetime.date.today()
    dias_semana = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
    data_base = datetime.date(2025, 5, 8)  # Dia OFF

    # Prepara os próximos 7 dias
    calendario_linhas = []
    for i in range(7):
        dia = today + datetime.timedelta(days=i)
        delta = (dia - data_base).days
        online = delta % 2 == 1  # 1 dia após o offline = online

        dia_str = dia.strftime("%d/%m")
        semana_str = dias_semana[dia.weekday()]
        status = "🟢 Online" if online else "🔴 Offline"

        # Se for o dia atual, bota em negrito
        if dia == today:
            calendario_linhas.append(f"**{semana_str} ({dia_str}) → {status}**")
        else:
            calendario_linhas.append(f"{semana_str} ({dia_str}) → {status}")

    embed = discord.Embed(
        title="📅 Agenda Semanal do Gugu",
        description="\n".join(calendario_linhas),
        color=discord.Color.green()
    )
    embed.set_footer(text="Atualizado automaticamente com base na data de hoje.")

    await ctx.reply(embed=embed)

# Inicia o bot
bot.run(TOKEN)
