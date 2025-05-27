import discord
from config import OWNER_ID
from ai import (
    carregar_conversas,
    salvar_conversas,
    obter_contexto_conversa,
)
import datetime

def register_ai_commands(bot):
    @bot.command()
    async def limpar_conversa(ctx):
        """Clear conversation history for current channel (owner only)"""
        if ctx.author.id != OWNER_ID:
            await ctx.reply("❌ Só o dono do bot pode limpar o histórico!")
            return

        conversas = carregar_conversas()
        canal_str = str(ctx.channel.id)

        if canal_str in conversas:
            del conversas[canal_str]
            salvar_conversas(conversas)
            await ctx.reply("🧹 Histórico de conversa limpo!")
        else:
            await ctx.reply("Não há histórico para limpar neste canal.")

    @bot.command()
    async def conversa_info(ctx):
        """Show conversation stats"""
        contexto = obter_contexto_conversa(ctx.channel.id)
        if not contexto:
            await ctx.reply("Nenhuma conversa registrada neste canal ainda.")
            return

        embed = discord.Embed(
            title="📊 Info da Conversa",
            description=f"Mensagens no contexto: {len(contexto)}\nÚltima mensagem: há {(datetime.datetime.now() - datetime.datetime.fromisoformat(contexto[-1]['timestamp'])).seconds // 60} minutos",
            color=discord.Color.blue()
        )
        await ctx.reply(embed=embed)
