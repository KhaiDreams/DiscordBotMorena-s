import random
from discord.ext import tasks
from utils import (
    obter_agora_brasil,
    formatar_data_brasil,
    carregar_sorteios,
    salvar_sorteios,
    converter_para_brasil,
)
import discord

def register_tasks(bot):
    atividades = [
        discord.Game(name="Apostando no Double 🃏"),
        discord.Streaming(name="Live Estudando 📚", url="https://www.twitch.tv/morena"),
        discord.Activity(type=discord.ActivityType.listening, name="Anjo 🎧"),
        discord.Activity(type=discord.ActivityType.watching, name="Como ganhar dinheiro 💰"),
        discord.Activity(type=discord.ActivityType.watching, name="Vlogs da Morena ❤✨"),
        discord.Activity(type=discord.ActivityType.listening, name="BlackPink 🎧"),
        discord.Activity(type=discord.ActivityType.watching, name="Saia justa 🤔"),
    ]

    @tasks.loop(minutes=10)
    async def mudar_status():
        atividade = random.choice(atividades)
        await bot.change_presence(status=discord.Status.online, activity=atividade)

    @tasks.loop(minutes=1)
    async def checar_sorteios():
        agora_brasil = obter_agora_brasil()
        sorteios = carregar_sorteios()
        atualizados = []

        for sorteio in sorteios:
            if sorteio.get("feito"):
                atualizados.append(sorteio)
                continue

            data_sorteio = converter_para_brasil(sorteio["data"])
            if agora_brasil >= data_sorteio:
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
                    embed.set_footer(text=f"Sorteio realizado em {formatar_data_brasil(agora_brasil)} (horário de Brasília)")
                    await canal.send("@everyone", embed=embed)

            atualizados.append(sorteio)

        salvar_sorteios(atualizados)

    # Exporte as tasks para serem iniciadas no on_ready
    bot.mudar_status_task = mudar_status
    bot.checar_sorteios_task = checar_sorteios
