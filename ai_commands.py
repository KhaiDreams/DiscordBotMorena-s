import discord
from config import OWNER_ID
from ai import (
    carregar_conversas,
    salvar_conversas,
    obter_contexto_conversa,
    carregar_memoria,
    obter_memorias,
)
import datetime

def register_ai_commands(bot):
    @bot.command()
    async def limpar_conversa(ctx):
        """Limpa histórico de conversa do canal atual (apenas owner)"""
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
        """Mostra estatísticas da conversa no canal"""
        contexto = obter_contexto_conversa(ctx.channel.id)
        if not contexto:
            await ctx.reply("Nenhuma conversa registrada neste canal ainda.")
            return

        minutos = (datetime.datetime.now() - datetime.datetime.fromisoformat(contexto[-1]['timestamp'])).seconds // 60
        
        embed = discord.Embed(
            title="📊 Info da Conversa",
            description=f"Mensagens no contexto: {len(contexto)}\nÚltima mensagem: há {minutos} minutos",
            color=discord.Color.blue()
        )
        await ctx.reply(embed=embed)
    
    @bot.command()
    async def ai_stats(ctx):
        """Mostra estatísticas gerais da IA (apenas owner)"""
        if ctx.author.id != OWNER_ID:
            await ctx.reply("❌ Comando apenas para o owner!")
            return
        
        conversas = carregar_conversas()
        memoria = carregar_memoria()
        
        total_mensagens = sum(len(msgs) for msgs in conversas.values())
        total_canais = len(conversas)
        
        # Contar memórias dinâmicas
        total_mem_servidores = len([k for k in memoria.get("servidores", {}).keys()])
        total_mem_usuarios = len([k for k in memoria.get("usuarios", {}).keys()])
        
        embed = discord.Embed(
            title="📈 Estatísticas da IA",
            description="IA com memória automática e documentação permanente",
            color=discord.Color.gold()
        )
        embed.add_field(name="💬 Mensagens", value=total_mensagens, inline=True)
        embed.add_field(name="📺 Canais Ativos", value=total_canais, inline=True)
        embed.add_field(name="🏰 Servidores c/ Memória", value=total_mem_servidores, inline=True)
        embed.add_field(name="👤 Usuários c/ Memória", value=total_mem_usuarios, inline=True)
        embed.add_field(name="🌡️ Temperatura", value="0.7", inline=True)
        embed.add_field(name="📝 Max Tokens", value="200", inline=True)
        embed.add_field(name="🤖 Modelo", value="gpt-4o-mini", inline=True)
        embed.add_field(name="💰 Custo/Resposta", value="~$0.0003", inline=True)
        embed.add_field(name="🧠 Análise Memória", value="A cada 10 respostas", inline=True)
        
        await ctx.reply(embed=embed)
    
    @bot.command()
    async def memorias_servidor(ctx):
        """Mostra as memórias automáticas do servidor atual"""
        if not ctx.guild:
            await ctx.reply("❌ Este comando só funciona em servidores!")
            return
        
        memorias = obter_memorias("servidores", f"guild_{ctx.guild.id}", limite=10)
        
        if not memorias:
            await ctx.reply(f"🧠 Ainda não há memórias sobre o servidor **{ctx.guild.name}**. A IA vai aprendendo com as conversas!")
            return
        
        # Dividir em páginas se necessário
        descricao = "\n".join(f"`{i+1}.` {mem}" for i, mem in enumerate(memorias[:15]))
        if len(memorias) > 15:
            descricao += f"\n\n... e mais {len(memorias) - 15} memórias"
        
        embed = discord.Embed(
            title=f"🧠 Memórias do Servidor: {ctx.guild.name}",
            description=descricao,
            color=discord.Color.purple()
        )
        embed.set_footer(text="Memórias são aprendidas automaticamente pela IA • Máx: 10")
        await ctx.reply(embed=embed)
    
    @bot.command()
    async def memorias_usuario(ctx, usuario: discord.Member = None):
        """Mostra as memórias automáticas sobre um usuário"""
        if usuario is None:
            usuario = ctx.author
        
        memorias = obter_memorias("usuarios", str(usuario.id), limite=10)
        
        if not memorias:
            await ctx.reply(f"🧠 Ainda não há memórias sobre **{usuario.display_name}**. A IA vai aprendendo com as interações!")
            return
        
        descricao = "\n".join(f"`{i+1}.` {mem}" for i, mem in enumerate(memorias[:15]))
        if len(memorias) > 15:
            descricao += f"\n\n... e mais {len(memorias) - 15} memórias"
        
        embed = discord.Embed(
            title=f"🧠 Memórias sobre {usuario.display_name}",
            description=descricao,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Memórias são aprendidas automaticamente pela IA • Máx: 10")
        await ctx.reply(embed=embed)
