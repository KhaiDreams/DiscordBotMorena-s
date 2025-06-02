import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import asyncio
from config import ARQUIVO_PREMIOS
from utils import carregar_dados, salvar_dados, obter_saldo, alterar_saldo

PREMIOS_PATH = ARQUIVO_PREMIOS

apostando_agora = set()

class PremioButton(Button):
    def __init__(self, nome_premio, info_premio):
        super().__init__(label=f"{nome_premio} - R${info_premio['valor']}", style=discord.ButtonStyle.primary)
        self.nome_premio = nome_premio
        self.info_premio = info_premio

    async def callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        premios_data = carregar_dados(PREMIOS_PATH, {})
        premio = premios_data.get(self.nome_premio)
        saldo = obter_saldo(user_id)

        if not premio:
            await interaction.response.send_message("❌ Prêmio não encontrado.", ephemeral=True)
            return

        if premio["estoque"] <= 0:
            await interaction.response.send_message("⚠️ Esse prêmio está esgotado.", ephemeral=True)
            return

        if saldo < premio["valor"]:
            await interaction.response.send_message("💸 Saldo insuficiente para resgatar esse prêmio.", ephemeral=True)
            return

        premio["estoque"] -= 1
        alterar_saldo(user_id, -premio["valor"])
        premio.setdefault("resgatados", []).append({
            "id": interaction.user.id,
            "nome": interaction.user.name
        })
        salvar_dados(PREMIOS_PATH, premios_data)

        await interaction.response.send_message(f"🎁 {interaction.user.mention} resgatou o prêmio: **{self.nome_premio}**!", ephemeral=True)

class PremiosView(View):
    def __init__(self, premios_data):
        super().__init__(timeout=120)
        row = 0
        for nome, info in premios_data.items():
            if info.get("estoque", 0) > 0:
                button = PremioButton(nome, info)
                button.row = row
                self.add_item(button)
                row += 1

async def setup_economy_commands(bot: commands.Bot):

    @bot.command(name="double")
    async def double(ctx, aposta: int, cor_aposta: str = None):
        user_id = str(ctx.author.id)

        if user_id in apostando_agora:
            await ctx.send("⏳ Calma aí! Tu já tá fazendo uma aposta, espera terminar.")
            return
        apostando_agora.add(user_id)

        saldo = obter_saldo(user_id)
        if aposta <= 0:
            await ctx.send("🟥 Aposta inválida.")
            apostando_agora.discard(user_id)
            return
        if aposta > saldo:
            await ctx.send("💸 Tu não tem saldo suficiente!")
            apostando_agora.discard(user_id)
            return
        if cor_aposta is None or cor_aposta.lower() not in ("v", "p", "b"):
            await ctx.send("❌ Você precisa escolher a cor da aposta: `v` para vermelho, `p` para preto, `b` para branco.")
            apostando_agora.discard(user_id)
            return

        cores_map = {"v": "vermelho", "p": "preto", "b": "branco"}
        cor_usuario = cores_map[cor_aposta.lower()]

        slots = ["🟥", "⬛", "⬜️"]
        cores = ["vermelho", "preto", "branco"]
        pesos = [47, 47, 5]
        resultado = random.choices(cores, weights=pesos)[0]

        def emoji_da_cor(cor):
            return {"vermelho": "🟥", "preto": "⬛", "branco": "⬜️"}.get(cor, "❓")

        await ctx.send(f"🎰 Apostando R${aposta} na cor **{cor_usuario.upper()}**... Girando a roleta...")
        msg = await ctx.send("🎰")

        roleta = [random.choice(slots) for _ in range(8)] + [emoji_da_cor(resultado)]
        for i in range(len(roleta)):
            visivel = " ".join(roleta[max(0, i-4):i+1])
            await msg.edit(content=f"🎰 {visivel}")
            await asyncio.sleep(0.4)

        cor_embed = (
            discord.Color.red() if resultado == "vermelho"
            else discord.Color.dark_gray() if resultado == "preto"
            else discord.Color.light_grey()
        )
        embed = discord.Embed(title="🎲 DOUBLE", description=f"O resultado foi **{resultado.upper()}**!", color=cor_embed)
        await ctx.send(embed=embed)

        multiplicadores = {"vermelho": 2, "preto": 2, "branco": 14}
        if resultado == cor_usuario:
            ganho = aposta * (multiplicadores[resultado] - 1)
            alterar_saldo(user_id, ganho)
            await ctx.send(f"💰 Você ganhou R${ganho}! Saldo atual: R${obter_saldo(user_id)}")
        else:
            alterar_saldo(user_id, -aposta)
            await ctx.send(f"😢 Você perdeu R${aposta}. Saldo atual: R${obter_saldo(user_id)}")

        apostando_agora.discard(user_id)

    @bot.command(name="saldo")
    async def saldo(ctx):
        user_id = str(ctx.author.id)
        saldo_atual = obter_saldo(user_id)
        await ctx.send(f"💰 {ctx.author.mention}, seu saldo atual é: R${saldo_atual}")

    @bot.command(name="premios")
    async def premios(ctx):
        premios_data = carregar_dados(PREMIOS_PATH, {})
        if not premios_data:
            await ctx.send("🚫 Nenhum prêmio disponível no momento.")
            return

        embed = discord.Embed(
            title="🎁 Lista de Prêmios Disponíveis",
            description="Clique no botão correspondente para resgatar o prêmio desejado.",
            color=discord.Color.gold()
        )

        for nome, info in premios_data.items():
            estoque = info.get("estoque", 0)
            valor = info.get("valor", 0)
            embed.add_field(name=f"🎉 {nome}", value=f"💵 **Valor:** R${valor}\n📦 **Estoque:** {estoque}", inline=False)

        view = PremiosView(premios_data)
        await ctx.send(embed=embed, view=view)

    @bot.command(name="transferir")
    async def transferir(ctx, valor: int, membro: discord.Member):
        remetente_id = str(ctx.author.id)
        destinatario_id = str(membro.id)

        if membro.id == ctx.author.id:
            await ctx.send("🤨 Tu não pode transferir pra tu mesmo, né?!")
            return
        if valor <= 0:
            await ctx.send("❌ O valor da transferência tem que ser maior que zero.")
            return

        saldo_remetente = obter_saldo(remetente_id)
        if saldo_remetente < valor:
            await ctx.send("💸 Tu não tem saldo suficiente pra essa transferência.")
            return

        alterar_saldo(remetente_id, -valor)
        alterar_saldo(destinatario_id, valor)
        await ctx.send(f"✅ {ctx.author.mention} transferiu R${valor} pra {membro.mention} com sucesso!")
