import discord
from discord.ext import commands
from discord.ui import View, Button
from utils import carregar_estudos, salvar_estudos, obter_agora_brasil, formatar_data_brasil
from datetime import datetime, timedelta

# Armazena sessões ativas: {user_id: {"inicio": datetime, "pausado_em": datetime|None, "tempo_pausado": int, "mensagem_id": int, "canal_id": int}}
sessoes_ativas = {}

class EstudoView(View):
    def __init__(self, user_id, pausado=False):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.pausado = pausado
        
        if pausado:
            self.clear_items()
            self.add_item(BotaoRetomar(user_id))
            self.add_item(BotaoFinalizar(user_id))
        else:
            self.clear_items()
            self.add_item(BotaoPausar(user_id))
            self.add_item(BotaoFinalizar(user_id))

class BotaoPausar(Button):
    def __init__(self, user_id):
        super().__init__(label="⏸ Pausar", style=discord.ButtonStyle.secondary, custom_id=f"pausar_{user_id}")
        self.user_id_alvo = user_id

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id_alvo):
            await interaction.response.send_message("❌ Você não pode controlar a sessão de outra pessoa!", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        if user_id not in sessoes_ativas:
            await interaction.response.send_message("❌ Você não tem uma sessão ativa.", ephemeral=True)
            return

        sessao = sessoes_ativas[user_id]
        if sessao.get("pausado_em"):
            await interaction.response.send_message("⚠️ A sessão já está pausada.", ephemeral=True)
            return

        # Pausa a sessão
        sessao["pausado_em"] = obter_agora_brasil()
        
        # Atualiza a view para mostrar botão de retomar
        nova_view = EstudoView(user_id, pausado=True)
        
        tempo_decorrido = calcular_tempo_decorrido(sessao)
        horas, minutos, segundos = formatar_segundos(tempo_decorrido)
        
        embed = discord.Embed(
            title="⏸ Sessão de Estudo Pausada",
            description=f"{interaction.user.mention} pausou a contagem de tempo.",
            color=discord.Color.orange()
        )
        embed.add_field(name="⏱ Tempo até agora", value=f"{horas}h {minutos}m {segundos}s", inline=False)
        embed.set_footer(text="Clique em ▶ Retomar para continuar estudando.")
        
        await interaction.response.edit_message(embed=embed, view=nova_view)

class BotaoRetomar(Button):
    def __init__(self, user_id):
        super().__init__(label="▶ Retomar", style=discord.ButtonStyle.success, custom_id=f"retomar_{user_id}")
        self.user_id_alvo = user_id

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id_alvo):
            await interaction.response.send_message("❌ Você não pode controlar a sessão de outra pessoa!", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        if user_id not in sessoes_ativas:
            await interaction.response.send_message("❌ Você não tem uma sessão ativa.", ephemeral=True)
            return

        sessao = sessoes_ativas[user_id]
        if not sessao.get("pausado_em"):
            await interaction.response.send_message("⚠️ A sessão não está pausada.", ephemeral=True)
            return

        # Calcula quanto tempo ficou pausado
        tempo_em_pausa = (obter_agora_brasil() - sessao["pausado_em"]).total_seconds()
        sessao["tempo_pausado"] = sessao.get("tempo_pausado", 0) + tempo_em_pausa
        sessao["pausado_em"] = None
        
        # Atualiza a view para mostrar botão de pausar
        nova_view = EstudoView(user_id, pausado=False)
        
        tempo_decorrido = calcular_tempo_decorrido(sessao)
        horas, minutos, segundos = formatar_segundos(tempo_decorrido)
        
        embed = discord.Embed(
            title="▶ Sessão de Estudo Retomada",
            description=f"{interaction.user.mention} retomou a contagem de tempo!",
            color=discord.Color.green()
        )
        embed.add_field(name="⏱ Tempo acumulado", value=f"{horas}h {minutos}m {segundos}s", inline=False)
        embed.set_footer(text="Continue firme nos estudos! 💪")
        
        await interaction.response.edit_message(embed=embed, view=nova_view)

class BotaoFinalizar(Button):
    def __init__(self, user_id):
        super().__init__(label="🛑 Finalizar", style=discord.ButtonStyle.danger, custom_id=f"finalizar_{user_id}")
        self.user_id_alvo = user_id

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id_alvo):
            await interaction.response.send_message("❌ Você não pode controlar a sessão de outra pessoa!", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        if user_id not in sessoes_ativas:
            await interaction.response.send_message("❌ Você não tem uma sessão ativa.", ephemeral=True)
            return

        await finalizar_sessao(interaction.user, interaction=interaction)

def calcular_tempo_decorrido(sessao):
    """Calcula o tempo total decorrido, descontando o tempo pausado"""
    agora = obter_agora_brasil()
    
    # Se está pausado, usa o momento da pausa
    if sessao.get("pausado_em"):
        tempo_total = (sessao["pausado_em"] - sessao["inicio"]).total_seconds()
    else:
        tempo_total = (agora - sessao["inicio"]).total_seconds()
    
    # Desconta o tempo que ficou pausado
    tempo_total -= sessao.get("tempo_pausado", 0)
    
    return max(0, int(tempo_total))

def formatar_segundos(segundos):
    """Converte segundos em horas, minutos e segundos"""
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60
    return horas, minutos, segs

async def finalizar_sessao(user, interaction=None, auto=False):
    """Finaliza a sessão de estudo e salva no histórico"""
    user_id = str(user.id)
    
    if user_id not in sessoes_ativas:
        return
    
    sessao = sessoes_ativas[user_id]
    tempo_total = calcular_tempo_decorrido(sessao)
    
    # Salva no histórico
    estudos = carregar_estudos()
    if user_id not in estudos:
        estudos[user_id] = {
            "total_segundos": 0,
            "sessoes": []
        }
    
    data_inicio = sessao["inicio"].strftime("%d/%m/%Y")
    hora_inicio = sessao["inicio"].strftime("%H:%M")
    hora_fim = obter_agora_brasil().strftime("%H:%M")
    
    estudos[user_id]["total_segundos"] += tempo_total
    estudos[user_id]["sessoes"].append({
        "data": data_inicio,
        "hora_inicio": hora_inicio,
        "hora_fim": hora_fim,
        "segundos": tempo_total
    })
    
    salvar_estudos(estudos)
    
    # Remove a sessão ativa
    del sessoes_ativas[user_id]
    
    # Formata o tempo para exibição
    horas, minutos, segundos = formatar_segundos(tempo_total)
    
    # Cria a mensagem de finalização
    if auto:
        embed = discord.Embed(
            title="🛑 Sessão Finalizada Automaticamente",
            description=f"{user.mention} saiu da call e a sessão foi encerrada.",
            color=discord.Color.red()
        )
    else:
        embed = discord.Embed(
            title="🛑 Sessão de Estudo Finalizada",
            description=f"{user.mention} finalizou a sessão de estudo!",
            color=discord.Color.blue()
        )
    
    embed.add_field(name="⏱ Tempo Total", value=f"{horas}h {minutos}m {segundos}s", inline=False)
    embed.add_field(name="📅 Período", value=f"{hora_inicio} - {hora_fim}", inline=False)
    embed.set_footer(text="Sessão registrada com sucesso! Bons estudos! 📚")
    
    if interaction:
        await interaction.response.edit_message(embed=embed, view=None)
    else:
        # Se foi automático, tenta editar a mensagem original
        try:
            canal = user.guild.get_channel(sessao["canal_id"])
            if canal:
                mensagem = await canal.fetch_message(sessao["mensagem_id"])
                await mensagem.edit(embed=embed, view=None)
        except:
            pass

def setup_study_commands(bot: commands.Bot):
    
    @bot.command(name="ponto")
    async def ponto(ctx):
        """Inicia o acompanhamento de horas de estudo"""
        user_id = str(ctx.author.id)
        
        # Verifica se o usuário está em uma call
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("❌ Você precisa estar em uma call de voz para usar este comando!")
            return
        
        # Verifica se já tem uma sessão ativa
        if user_id in sessoes_ativas:
            await ctx.reply("⚠️ Você já tem uma sessão de estudo ativa! Finalize ou pause ela antes de começar outra.")
            return
        
        # Cria a sessão
        agora = obter_agora_brasil()
        sessoes_ativas[user_id] = {
            "inicio": agora,
            "pausado_em": None,
            "tempo_pausado": 0,
            "mensagem_id": None,
            "canal_id": ctx.channel.id
        }
        
        # Cria a embed e a view
        embed = discord.Embed(
            title="⏱ Sessão de Estudo Iniciada",
            description=f"{ctx.author.mention} começou a estudar!",
            color=discord.Color.green()
        )
        embed.add_field(name="🕒 Início", value=formatar_data_brasil(agora), inline=False)
        embed.set_footer(text="Use os botões abaixo para controlar sua sessão.")
        
        view = EstudoView(user_id, pausado=False)
        mensagem = await ctx.reply(embed=embed, view=view)
        
        # Salva o ID da mensagem
        sessoes_ativas[user_id]["mensagem_id"] = mensagem.id
    
    @bot.command(name="tempo")
    async def tempo(ctx, membro: discord.Member = None):
        """Mostra quanto tempo você ou outro usuário estudou"""
        alvo = membro or ctx.author
        user_id = str(alvo.id)
        
        estudos = carregar_estudos()
        
        if user_id not in estudos or not estudos[user_id]["sessoes"]:
            await ctx.reply(f"📚 {alvo.mention} ainda não registrou nenhuma sessão de estudo.")
            return
        
        dados = estudos[user_id]
        tempo_total = dados["total_segundos"]
        
        # Se tem sessão ativa, adiciona o tempo atual
        if user_id in sessoes_ativas:
            tempo_total += calcular_tempo_decorrido(sessoes_ativas[user_id])
        
        horas_total, minutos_total, segundos_total = formatar_segundos(tempo_total)
        
        # Agrupa por data
        sessoes_por_data = {}
        for sessao in dados["sessoes"]:
            data = sessao["data"]
            if data not in sessoes_por_data:
                sessoes_por_data[data] = []
            sessoes_por_data[data].append(sessao)
        
        # Cria a embed
        embed = discord.Embed(
            title=f"📊 Tempo de Estudo - {alvo.display_name}",
            description=f"**Tempo Total:** {horas_total}h {minutos_total}m {segundos_total}s",
            color=discord.Color.blue()
        )
        
        # Adiciona os dias estudados (ordenados do mais recente)
        dias_ordenados = sorted(sessoes_por_data.keys(), key=lambda x: datetime.strptime(x, "%d/%m/%Y"), reverse=True)
        
        texto_dias = ""
        for i, data in enumerate(dias_ordenados[:10]):  # Mostra no máximo 10 dias
            sessoes_dia = sessoes_por_data[data]
            tempo_dia = sum(s["segundos"] for s in sessoes_dia)
            h, m, s = formatar_segundos(tempo_dia)
            texto_dias += f"📅 **{data}** - {h}h {m}m {s}s ({len(sessoes_dia)} sessão/sessões)\n"
        
        if texto_dias:
            embed.add_field(name="📆 Histórico de Estudos", value=texto_dias, inline=False)
        
        # Estatísticas adicionais
        total_dias = len(sessoes_por_data)
        total_sessoes = len(dados["sessoes"])
        media_por_dia = tempo_total / total_dias if total_dias > 0 else 0
        h_media, m_media, s_media = formatar_segundos(int(media_por_dia))
        
        embed.add_field(name="📈 Estatísticas", 
                       value=f"🗓 **Dias estudados:** {total_dias}\n📝 **Total de sessões:** {total_sessoes}\n⏱ **Média por dia:** {h_media}h {m_media}m {s_media}s",
                       inline=False)
        
        if user_id in sessoes_ativas:
            embed.set_footer(text="⏱ Sessão ativa! O tempo continua sendo contabilizado.")
        
        await ctx.reply(embed=embed)
    
    @bot.command(name="rank_estudos")
    async def rank_estudos(ctx):
        """Mostra o ranking de quem mais estudou no servidor"""
        estudos = carregar_estudos()
        
        if not estudos:
            await ctx.reply("📚 Ainda não há ninguém com registro de estudos.")
            return
        
        # Filtra apenas membros do servidor e calcula tempo total (incluindo sessões ativas)
        ranking = []
        for user_id, dados in estudos.items():
            try:
                membro = await ctx.guild.fetch_member(int(user_id))
                tempo_total = dados["total_segundos"]
                
                # Adiciona tempo da sessão ativa se houver
                if user_id in sessoes_ativas:
                    tempo_total += calcular_tempo_decorrido(sessoes_ativas[user_id])
                
                if tempo_total > 0:
                    ranking.append({
                        "membro": membro,
                        "tempo": tempo_total,
                        "dias": len(set(s["data"] for s in dados["sessoes"]))
                    })
            except:
                continue
        
        if not ranking:
            await ctx.reply("📚 Ainda não há ninguém com registro de estudos neste servidor.")
            return
        
        # Ordena por tempo total
        ranking.sort(key=lambda x: x["tempo"], reverse=True)
        
        # Cria a embed
        embed = discord.Embed(
            title="🏆 Ranking de Estudos Global",
            description="Os membros que mais dedicaram tempo aos estudos!",
            color=discord.Color.gold()
        )
        
        # Emojis de medalha
        medalhas = ["🥇", "🥈", "🥉"]
        
        texto_ranking = ""
        for i, item in enumerate(ranking[:10]):  # Top 10
            h, m, s = formatar_segundos(item["tempo"])
            medalha = medalhas[i] if i < 3 else f"**{i+1}º**"
            
            texto_ranking += f"{medalha} {item['membro'].mention}\n"
            texto_ranking += f"    ⏱ {h}h {m}m {s}s | 📅 {item['dias']} dias\n\n"
        
        embed.description = texto_ranking
        embed.set_footer(text=f"Total de estudantes: {len(ranking)}")
        
        await ctx.reply(embed=embed)
    
    @bot.event
    async def on_voice_state_update(member, before, after):
        """Detecta quando alguém sai da call e finaliza a sessão automaticamente"""
        user_id = str(member.id)
        
        # Verifica se o usuário tinha uma sessão ativa e saiu da call
        if user_id in sessoes_ativas:
            # Se estava em call e saiu, ou se mudou para None
            if before.channel and not after.channel:
                await finalizar_sessao(member, auto=True)
