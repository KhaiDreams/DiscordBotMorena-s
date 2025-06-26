import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import datetime

from utils import obter_agora_brasil, fuso_brasil

def setup_fun_commands(bot):
    @bot.command()
    async def oi(ctx: commands.Context):
        """Greet the user"""
        nome = ctx.author.display_name
        await ctx.reply(f"Fala tu, {nome}! 😎")

    @bot.command()
    async def rony(ctx):
        """Info about Rony"""
        await ctx.reply("A Rony é uma novata no Pressão, que odeia Subnautica e está começando a assistir Tartarugas Ninja. Khai ensina tudo que ela sabe!")

    @bot.command()
    async def khai(ctx):
        """Info about Khai"""
        await ctx.reply("Khai é o namorado da Morena, lindo e cheiroso!")

    @bot.command()
    async def morena(ctx):
        """Info about Morena"""
        await ctx.reply("Estamos falando da mais mais, a Morena! Ela é linda, cheirosa e brilha mais que tudo! ✨")

    @bot.command()
    async def gugu(ctx):
        """Display Gugu's weekly schedule"""
        hoje_brasil = obter_agora_brasil().date()
        dias_semana = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]
        data_base = datetime.date(2025, 5, 8)  # Base date (OFF day)

        calendario_linhas = []

        for i in range(7):
            dia = hoje_brasil + datetime.timedelta(days=i)
            delta = (dia - data_base).days
            online = delta % 2 == 1

            dia_str = dia.strftime("%d/%m")
            semana_str = dias_semana[dia.weekday()]
            status = "🟢 Online" if online else "🔴 Offline"

            # Random schedule for online days
            if online:
                acorda = datetime.time(random.randint(5, 11), random.choice([0, 15, 30, 45]))
                dorme_hora = random.randint(22, 27)  # 27 = 3 AM next day
                dorme_min = random.choice([0, 15, 30, 45])
                dorme = datetime.time(dorme_hora % 24, dorme_min)
                dorme_str = f"{dorme.strftime('%H:%M')} {'(+1)' if dorme_hora >= 24 else ''}"
                horario_str = f"🕒 {acorda.strftime('%H:%M')} até {dorme_str}"
            else:
                horario_str = "💤 Indisponível"

            # Highlight current day
            linha = f"{semana_str} ({dia_str}) → {status} | {horario_str}"
            if dia == hoje_brasil:
                linha = f"**{linha}**"

            calendario_linhas.append(linha)

        embed = discord.Embed(
            title="📅 Agenda Semanal do Gugu",
            description="\n\n".join(calendario_linhas),
            color=discord.Color.green()
        )
        embed.set_footer(text="Saiba onde encontrar o Gugu! (horário de Brasília)")

        await ctx.reply(embed=embed)

    @bot.command()
    async def eu(ctx, membro: discord.Member = None):
        """Send a random phrase about someone"""
        with open("data/frases_eu.txt", "r", encoding="utf-8") as f:
            FRASES_ZOEIRA = [linha.strip() for linha in f if linha.strip()]
        alvo = membro or ctx.author
        frase = random.choice(FRASES_ZOEIRA)
        frase_final = frase.replace("{alvo}", alvo.mention)
        await ctx.reply(frase_final)

    @bot.command()
    async def escolha(ctx: commands.Context, membro: discord.Member = None):
        """Pick a random message from a user"""
        if not ctx.guild:
            await ctx.reply("Esse comando só funciona em servidor, não em DM.")
            return

        loading_msg = await ctx.reply("A Morena está procurando uma mensagem... Aguarde!! ⏳")

        alvo = membro or ctx.author
        mensagens = []

        for canal in ctx.guild.text_channels:
            if not canal.permissions_for(ctx.guild.me).read_message_history:
                continue
            try:
                async for msg in canal.history(limit=1000):
                    if msg.author.id == alvo.id and not msg.content.startswith('.') and msg.content.strip():
                        mensagens.append(msg)
            except (discord.Forbidden, discord.HTTPException):
                continue

        if not mensagens:
            await loading_msg.delete()
            await ctx.reply(f"Não achei nenhuma mensagem de {alvo.display_name} 😔")
            return

        msg_escolhida = random.choice(mensagens)
        link_mensagem = f"https://discord.com/channels/{ctx.guild.id}/{msg_escolhida.channel.id}/{msg_escolhida.id}"

        data_msg_brasil = msg_escolhida.created_at.astimezone(fuso_brasil)

        embed = discord.Embed(
            title=f"Mensagem aleatória de {alvo.display_name}",
            description=msg_escolhida.content,
            color=discord.Color.blue()
        )
        embed.set_author(name=alvo.display_name, icon_url=alvo.display_avatar.url)
        embed.set_footer(text=f"Canal: #{msg_escolhida.channel.name} • {data_msg_brasil.strftime('%d/%m/%Y %H:%M')} (horário de Brasília)")

        view = View()
        view.add_item(Button(label="Ver no contexto 🔍", style=discord.ButtonStyle.link, url=link_mensagem))

        await loading_msg.delete()
        await ctx.reply(embed=embed, view=view)

    @bot.command()
    async def comandos(ctx):
        """Send command list via DM"""
        comandos_texto = (
            "**📋 Lista de Comandos Disponíveis:**\n\n"
            ".oi - O bot te dá um salve 😎\n"
            ".rony - Fala da novata Rony 🐢\n"
            ".khai - Elogia o Khai 😘\n"
            ".gugu - Avisos sobre quando o Gugu ficará Online 📅\n"
            ".morena - Sobre a mais mais (brilho✨) 😘\n"
            ".comandos - Manda essa lista aqui no seu PV 📬\n"
            ".escolha [@alguém] - Escolhe uma mensagem aleatória da pessoa\n"
            ".sortear - Cria um sorteio 🎉\n"
            ".sorteios - Mostra a lista de sorteios criados 📜\n"
            ".eu [@alguém] - Vai falar algo bem carinhoso para você! 🤞\n"
            "/record - Cria um desafio (record) que a galera pode tentar bater 🏁\n"
            ".records - Mostra todos os records criados 🎯\n"
            ".tentativa [número do record] [quantidade] - Tenta bater um record específico 💥\n"
            ".ranking [número do record] mostra o raking record específico 🐱‍👤\n"
            ".deletar_record [número do record] - Deleta um record (só quem criou pode excluir) 🗑️\n"
            "/sugestao - Envia para nossa caixa de sugestões, uma ideia para ser adicionada no bot 💡\n"
            "/secreto @alguém mensagem - Envia uma mensagem anônima no PV de alguém 🔒\n"
            ".double [valor] [v/p/b] - Joga no Double, apostando na cor Vermelho (v), Preto (p) ou Branco (b) 🎲\n"
            ".saldo - Consulta seu saldo atual 💰\n"
            ".transferir [valor] [@alguém] - Transfere grana do teu saldo pra outro membro 💸\n"
            ".premios - Mostra a lista de prêmios ou resgata🎁\n"
            "/corrida - Inicia uma corrida de cavalos com apostas entre os jogadores! Use o botão/modal para apostar facilmente. 🏇\n"
        )
        corrida_explicacao = (
            "\n**Como funciona a Corrida de Cavalos:**\n"
            "- Use `/corrida` para iniciar uma corrida no canal.\n"
            "- Todos têm 30 segundos para apostar em um dos 3 cavalos, usando o modal que aparece ao clicar no comando.\n"
            "- Você escolhe o valor da aposta e o número do cavalo.\n"
            "- O saldo é debitado na hora da aposta.\n"
            "- Todos podem apostar juntos, cada um em qualquer cavalo.\n"
            "- O progresso dos cavalos é animado no chat, e todos acompanham juntos.\n"
            "- Se as apostas dos ganhadores forem equivalentes (diferença até 20%), o prêmio é o valor total apostado, dividido igualmente.\n"
            "- Se só uma pessoa apostar, ou se houver grande diferença entre os valores apostados, o prêmio é 150% do valor apostado pelo ganhador.\n"
            "- Caso contrário, o prêmio é proporcional ao valor apostado (90% do total apostado).\n"
            "- Se ninguém apostar, a corrida é cancelada.\n"
            "- O comando é fácil, rápido e divertido!\n"
        )
        try:
            await ctx.author.send(comandos_texto)
            await ctx.author.send(corrida_explicacao)
            if ctx.guild:
                await ctx.reply("Te mandei no PV, confere lá! 📬")
        except discord.Forbidden:
            await ctx.reply("Não consegui te mandar DM. Tu precisa liberar as mensagens privadas do servidor. ❌")
