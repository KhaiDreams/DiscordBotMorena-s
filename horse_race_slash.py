import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
from utils import debitar_saldo, adicionar_saldo, obter_saldo

CAVALOS = ["🐎", "🦄", "🐴", "🐐", "🫏"]
DISTANCIA = 20
TEMPO_APOSTA = 30
TEMPO_PASSO = 1.2

class CorridaAposta:
    def __init__(self, cavalos):
        self.apostas = {}  # {user_id: (valor, cavalo_idx)}
        self.cavalos = cavalos
        self.andamento = [0] * len(self.cavalos)
        self.terminou = False
        self.vencedor = None

    def apostar(self, user_id, valor, cavalo_idx):
        self.apostas[user_id] = (valor, cavalo_idx)

    def avancar(self):
        for i in range(len(self.cavalos)):
            self.andamento[i] += random.randint(1, 3)
        for i, pos in enumerate(self.andamento):
            if pos >= DISTANCIA:
                self.terminou = True
                self.vencedor = i
                break

    def get_animacao(self):
        linhas = []
        for idx, cavalo in enumerate(self.cavalos):
            pos = min(self.andamento[idx], DISTANCIA)
            pista = cavalo + ("-" * pos) + "|🏁|"
            linhas.append(pista)
        return "\n".join(linhas)

    def resumo_apostas(self):
        resumo = {}
        for uid, (valor, idx) in self.apostas.items():
            if idx not in resumo:
                resumo[idx] = []
            resumo[idx].append((uid, valor))
        return resumo

class CorridaModal(discord.ui.Modal, title="Aposte na Corrida de Cavalos!"):
    valor = discord.ui.TextInput(label="Valor da aposta", placeholder="Ex: 100", required=True)
    cavalo = discord.ui.TextInput(label="Número do cavalo (1, 2 ou 3)", placeholder="Ex: 2", required=True)

    def __init__(self, corrida, user_id, callback):
        super().__init__()
        self.corrida = corrida
        self.user_id = user_id
        self.callback_func = callback

    async def on_submit(self, interaction: discord.Interaction):
        try:
            valor = int(self.valor.value)
            cavalo_idx = int(self.cavalo.value) - 1
            if cavalo_idx not in range(len(self.corrida.cavalos)):
                await interaction.response.send_message("Número do cavalo inválido!", ephemeral=True)
                return
            saldo = obter_saldo(interaction.user.id)
            if valor <= 0 or valor > saldo:
                await interaction.response.send_message("Saldo insuficiente ou valor inválido!", ephemeral=True)
                return
            debitar_saldo(interaction.user.id, valor)
            self.corrida.apostar(interaction.user.id, valor, cavalo_idx)
            await self.callback_func(interaction, valor, cavalo_idx)
        except Exception as e:
            await interaction.response.send_message(f"Erro: {e}", ephemeral=True)

class ApostarButton(discord.ui.View):
    def __init__(self, corrida, aposta_callback, embed, apostas_msg):
        super().__init__(timeout=None)
        self.corrida = corrida
        self.aposta_callback = aposta_callback
        self.embed = embed
        self.apostas_msg = apostas_msg

    @discord.ui.button(label="Apostar", style=discord.ButtonStyle.green)
    async def apostar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild:
            await interaction.response.send_message("Só pode apostar em servidores!", ephemeral=True)
            return
        if interaction.user.id in self.corrida.apostas:
            await interaction.response.send_message("Você já apostou nesta corrida!", ephemeral=True)
            return
        modal = CorridaModal(self.corrida, interaction.user.id, self.aposta_callback)
        await interaction.response.send_modal(modal)

async def atualizar_apostas_embed(corrida, embed, apostas_msg, cavalos, view):
    resumo = corrida.resumo_apostas()
    texto = "**Apostas até agora:**\n"
    for idx, lista in resumo.items():
        nomes = [f"<@{uid}> ({v} moedas)" for uid, v in lista]
        texto += f"{cavalos[idx]}: " + ", ".join(nomes) + "\n"
    embed.description = texto
    await apostas_msg.edit(embed=embed, view=view)

class HorseRaceSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.corridas = {}

    @app_commands.command(name="corrida", description="Inicie uma corrida de cavalos e aposte!")
    async def corrida(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("Este comando só pode ser usado em servidores!", ephemeral=True)
            return
        if interaction.guild_id in self.corridas:
            await interaction.response.send_message("Já existe uma corrida em andamento neste servidor!", ephemeral=True)
            return
        cavalos = random.sample(CAVALOS, k=3)
        corrida = CorridaAposta(cavalos)
        self.corridas[interaction.guild_id] = corrida
        desc = "\n".join([f"{i+1}. {c}" for i, c in enumerate(cavalos)])
        embed = discord.Embed(title="🏇 Corrida de Cavalos! 🏇", description="Aposte em qual cavalo vai ganhar!", color=0xFFD700)
        embed.add_field(name="Cavalos:", value=desc, inline=False)
        embed.set_footer(text=f"Você tem {TEMPO_APOSTA} segundos para apostar!")
        apostas_msg = await interaction.response.send_message(embed=embed)
        apostas_msg = await interaction.original_response()
        # Define o callback de aposta
        view = None  # será definida logo abaixo
        async def aposta_callback(inter, valor, cavalo_idx):
            corrida.apostar(inter.user.id, valor, cavalo_idx)
            await inter.response.send_message(f"Aposta registrada: {valor} moedas no cavalo {cavalos[cavalo_idx]}", ephemeral=True)
            await atualizar_apostas_embed(corrida, embed, apostas_msg, cavalos, view)
        # Adiciona a view com botão
        view = ApostarButton(corrida, aposta_callback, embed, apostas_msg)
        await apostas_msg.edit(embed=embed, view=view)
        # Espera o tempo de apostas
        await asyncio.sleep(TEMPO_APOSTA)
        if not corrida.apostas:
            await interaction.channel.send("Ninguém apostou! Corrida cancelada.")
            del self.corridas[interaction.guild_id]
            return
        await interaction.channel.send("Corrida começando! 🏁")
        animacao = await interaction.channel.send(corrida.get_animacao())
        await asyncio.sleep(2)
        while not corrida.terminou:
            corrida.avancar()
            await animacao.edit(content=corrida.get_animacao())
            await asyncio.sleep(TEMPO_PASSO)
        idx_vencedor = corrida.vencedor
        cavalo_vencedor = corrida.cavalos[idx_vencedor]
        ganhadores = [(uid, valor) for uid, (valor, idx) in corrida.apostas.items() if idx == idx_vencedor]
        total_apostado = sum(valor for valor, _ in corrida.apostas.values())
        total_apostado_vencedor = sum(valor for uid, valor in ganhadores)
        premio_total = int(total_apostado * 0.9)
        if ganhadores:
            texto = f"🏆 O cavalo vencedor foi {cavalo_vencedor}!\n"
            for uid, valor in ganhadores:
                premio = int((valor / total_apostado_vencedor) * premio_total)
                adicionar_saldo(uid, premio)
                texto += f"<@{uid}> ganhou {premio} moedas apostando {valor}!\n"
            texto += f"\nO prêmio é proporcional ao valor apostado."
        else:
            texto = f"O cavalo vencedor foi {cavalo_vencedor}, mas ninguém apostou nele! 😢"
        await interaction.channel.send(texto)
        del self.corridas[interaction.guild_id]

def setup_horse_race_slash(bot):
    bot.tree.add_command(HorseRaceSlash(bot).corrida)
