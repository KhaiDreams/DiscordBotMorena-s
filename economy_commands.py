import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import asyncio
import json
import os

ECONOMIA_PATH = "data/economia.json"
PREMIOS_PATH = "data/premios.json"

def carregar_dados(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(path, dados):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def obter_saldo(user_id):
    dados = carregar_dados(ECONOMIA_PATH, {})
    if str(user_id) not in dados:
        dados[str(user_id)] = 100
        salvar_dados(ECONOMIA_PATH, dados)
    return dados[str(user_id)]

def alterar_saldo(user_id, valor):
    dados = carregar_dados(ECONOMIA_PATH, {})
    dados[str(user_id)] = dados.get(str(user_id), 100) + valor
    salvar_dados(ECONOMIA_PATH, dados)

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

        # Atualiza dados
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
        super().__init__(timeout=120)  # 2 minutos para expirar os botões
        for nome, info in premios_data.items():
            if info.get("estoque", 0) > 0:
                self.add_item(PremioButton(nome, info))

async def setup_economy_commands(bot: commands.Bot):

    @bot.command(name="double")
    async def double(ctx, aposta: int, cor_aposta: str = None):
        user_id = str(ctx.author.id)
        saldo = obter_saldo(user_id)
        if aposta <= 0:
            await ctx.send("🟥 Aposta inválida.")
            return
        if aposta > saldo:
            await ctx.send("💸 Tu não tem saldo suficiente!")
            return
        if cor_aposta is None or cor_aposta.lower() not in ("v", "p", "b"):
            await ctx.send("❌ Você precisa escolher a cor da aposta: `v` para vermelho, `p` para preto, `b` para branco.")
            return

        cores_map = {
            "v": "vermelho",
            "p": "preto",
            "b": "branco"
        }
        cor_usuario = cores_map[cor_aposta.lower()]

        slots = ["🟥", "⬛", "⬜️"]
        cores = ["vermelho", "preto", "branco"]
        pesos = [47, 47, 5]  # Branco mais raro
        resultado = random.choices(cores, weights=pesos)[0]

        def emoji_da_cor(cor):
            return {
                "vermelho": "🟥",
                "preto": "⬛",
                "branco": "⬜️"
            }.get(cor, "❓")

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
        embed = discord.Embed(
            title="🎲 DOUBLE",
            description=f"O resultado foi **{resultado.upper()}**!",
            color=cor_embed
        )
        await ctx.send(embed=embed)

        multiplicadores = {"vermelho": 2, "preto": 2, "branco": 14}
        if resultado == cor_usuario:
            ganho = aposta * (multiplicadores[resultado] - 1)
            alterar_saldo(user_id, ganho)
            await ctx.send(f"💰 Você ganhou R${ganho}! Saldo atual: R${obter_saldo(user_id)}")
        else:
            alterar_saldo(user_id, -aposta)
            await ctx.send(f"😢 Você perdeu R${aposta}. Saldo atual: R${obter_saldo(user_id)}")

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

        embed = discord.Embed(title="🎁 Prêmios disponíveis")
        for nome, info in premios_data.items():
            embed.add_field(
                name=f"{nome}",
                value=f"💵 R${info['valor']} | 📦 Estoque: {info['estoque']}",
                inline=False
            )

        view = PremiosView(premios_data)
        await ctx.send(embed=embed, view=view)
