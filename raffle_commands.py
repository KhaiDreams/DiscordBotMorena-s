from discord.ui import View, Button
import discord
from utils import (
    carregar_sorteios,
)
from config import msg_com_botao

def register_raffle_commands(bot):
    @bot.command()
    async def sortear(ctx):
        await sortear_command(ctx)

    @bot.command()
    async def sorteios(ctx):
        """Display all raffles"""
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
                value=f"📅 Data: {s['data']} (horário de Brasília)\n👥 Participantes: {len(s['participantes'])}{ganhador}",
                inline=False
            )

        await ctx.send(embed=embed)

# Função compartilhada para uso no comando de barra (slash)
async def sortear_command(ctx_or_interaction):
    global msg_com_botao
    view = View()

    async def abrir_modal_callback(interaction: discord.Interaction):
        # SorteioModal é necessário para abrir o modal
        from modals import SorteioModal
        # Corrige para pegar o canal correto tanto em ctx quanto em interaction
        canal_id = getattr(ctx_or_interaction, "channel", None)
        if canal_id is None and hasattr(ctx_or_interaction, "channel_id"):
            canal_id = ctx_or_interaction.channel_id
        else:
            canal_id = ctx_or_interaction.channel.id
        await interaction.response.send_modal(SorteioModal(canal_id))

    bot = ctx_or_interaction.bot if hasattr(ctx_or_interaction, "bot") else ctx_or_interaction.client
    botao = Button(label="Criar Sorteio 🎁", style=discord.ButtonStyle.success)
    botao.callback = abrir_modal_callback
    view.add_item(botao)

    if hasattr(ctx_or_interaction, "send"):
        # Contexto de comando normal
        global msg_com_botao
        msg_com_botao = await ctx_or_interaction.send(
            "Clique no botão abaixo para abrir o painel de criação de sorteio:", view=view
        )
    else:
        # Contexto de slash command
        await ctx_or_interaction.response.send_message(
            "Clique no botão abaixo para abrir o painel de criação de sorteio:", view=view, ephemeral=True
        )

# Função para uso no slash command
async def sortear_command_slash(bot, interaction):
    await sortear_command(interaction)
