import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents e configuração do bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('Bot is ready!')
    print('------')

@bot.command()
async def oi(ctx:commands.Context):
    nome = ctx.author.display_name
    await ctx.reply(f"Fala tu {nome}! 😎")

@bot.command()
async def rony(ctx):
    await ctx.reply("A Rony é uma novata no Pressão, que odeia Subnautica e está começando a assistir Tartarugas Ninja. Khai ensina tudo que ela sabe!")

@bot.command()
async def khai(ctx):
    await ctx.reply("Khai é o namorado da Morena, lindo e cheiroso!")

@bot.command()
async def vini(ctx):
    await ctx.reply("Vini é um português safado, não gosta de jogar e só quer saber de comer!")

# Comando .comandos - manda a lista no privado
@bot.command()
async def comandos(ctx):
    try:
        await ctx.author.send(
            "**📋 Lista de Comandos Disponíveis:**\n\n"
            "`.oi` - A morena te dá um salve 😎\n"
            "`.rony` - Fala da novata Rony 🐢\n"
            "`.khai` - Elogia o Khai 😘\n"
            "`.vini` - Conta um pouco sobre o vini 😘\n"
            "`.comandos` - Manda essa lista aqui no seu PV 📬"
        )
        if ctx.guild:
            await ctx.reply("Te mandei no PV, confere lá! 📬")
    except discord.Forbidden:
        await ctx.reply("Não consegui te mandar DM. Tu precisa liberar as mensagens privadas do servidor. ❌")

bot.run(TOKEN)
