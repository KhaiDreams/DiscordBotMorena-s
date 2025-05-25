import discord
from discord.ext import commands, tasks
from discord.ui import Modal, TextInput, View, Button
from dotenv import load_dotenv
import os
import random
import datetime
import json
import pytz
import openai
from typing import List, Dict

# Environment setup
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure OpenAI
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

# Bot configuration
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)
fuso_brasil = pytz.timezone("America/Sao_Paulo")

OWNER_ID = 329265386153443329   # Replace with your Discord user ID

# File constants
ARQUIVO_SORTEIOS = "sorteios.json"
ARQUIVO_RECORDS = "records.json"
ARQUIVO_CONVERSAS = "conversas.json"

# Global variables
msg_com_botao = None

# AI Configuration
MAX_CONTEXT_MESSAGES = 10  # Número máximo de mensagens para contexto
RESPONSE_CHANCE = 0.2  # 20% de chance de responder sem menção (ajuste conforme necessário)

# ========================================
# AI CONVERSATION FUNCTIONS
# ========================================

def carregar_conversas():
    """Load conversation history from JSON file"""
    if not os.path.exists(ARQUIVO_CONVERSAS):
        with open(ARQUIVO_CONVERSAS, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)
    with open(ARQUIVO_CONVERSAS, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_conversas(conversas):
    """Save conversation history to JSON file"""
    with open(ARQUIVO_CONVERSAS, "w", encoding="utf-8") as f:
        json.dump(conversas, f, indent=4, ensure_ascii=False)

def adicionar_mensagem_conversa(canal_id: int, autor: str, conteudo: str, is_bot: bool = False):
    """Add message to conversation history"""
    conversas = carregar_conversas()
    canal_str = str(canal_id)
    
    if canal_str not in conversas:
        conversas[canal_str] = []
    
    # Add new message
    mensagem = {
        "autor": autor,
        "conteudo": conteudo,
        "timestamp": datetime.datetime.now().isoformat(),
        "is_bot": is_bot
    }
    
    conversas[canal_str].append(mensagem)
    
    # Keep only last MAX_CONTEXT_MESSAGES
    if len(conversas[canal_str]) > MAX_CONTEXT_MESSAGES:
        conversas[canal_str] = conversas[canal_str][-MAX_CONTEXT_MESSAGES:]
    
    salvar_conversas(conversas)

def obter_contexto_conversa(canal_id: int) -> List[Dict]:
    """Get conversation context for a channel"""
    conversas = carregar_conversas()
    canal_str = str(canal_id)
    return conversas.get(canal_str, [])

async def gerar_resposta_ai(contexto: List[Dict], pergunta: str = None) -> str:
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é Morena, um bot do Discord. "
                    "com linguagem brasileira e gírias, respostas curtas e naturais."
                    "bem brava, e que usa emojis com moderação."
                )
            }
        ]
        
        for msg in contexto[-4:]:
            role = "assistant" if msg["is_bot"] else "user"
            content = f"{msg['autor']}: {msg['conteudo']}" if not msg["is_bot"] else msg["conteudo"]
            messages.append({"role": role, "content": content})
        
        if pergunta:
            messages.append({"role": "user", "content": pergunta})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Erro ao gerar resposta da IA: {e}")
        respostas_backup = [
            "Opa, não entendi direito 😅",
            "Pode repetir? Bugou aqui kk",
            "Eita, deu erro aqui, desculpa!",
            "Hmm, não consegui processar isso 🤔",
            "Falha na matrix! Tenta de novo?"
        ]
        return random.choice(respostas_backup)

def deve_responder_mensagem(message: discord.Message) -> bool:
    # Sempre responde se mencionado ou se a mensagem for reply à dele
    if bot.user in message.mentions:
        return True
    if message.reference and message.reference.resolved and message.reference.resolved.author == bot.user:
        return True
    
    # Não responde bots nem comandos
    if message.author.bot:
        return False
    if message.content.startswith('.') or message.content.startswith('/'):
        return False
    
    # Chance random só pra não floodar sempre
    return random.random() < RESPONSE_CHANCE

# ========================================
# UTILITY FUNCTIONS
# ========================================

def obter_agora_brasil():
    """Get current time in Brazil timezone"""
    return datetime.datetime.now(fuso_brasil)

def formatar_data_brasil(dt):
    """Format datetime to Brazilian format"""
    if dt.tzinfo is None:
        dt = fuso_brasil.localize(dt)
    return dt.strftime("%d/%m/%Y %H:%M")

def converter_para_brasil(dt_string):
    """Convert datetime string to Brazil timezone datetime object"""
    dt_naive = datetime.datetime.strptime(dt_string, "%d/%m/%Y %H:%M")
    return fuso_brasil.localize(dt_naive)

def carregar_sorteios():
    """Load raffles from JSON file"""
    if not os.path.exists(ARQUIVO_SORTEIOS):
        with open(ARQUIVO_SORTEIOS, "w") as f:
            json.dump([], f)
    with open(ARQUIVO_SORTEIOS, "r") as f:
        return json.load(f)

def salvar_sorteios(sorteios):
    """Save raffles to JSON file"""
    with open(ARQUIVO_SORTEIOS, "w") as f:
        json.dump(sorteios, f, indent=4)

def carregar_records():
    """Load records from JSON file"""
    if not os.path.exists(ARQUIVO_RECORDS):
        with open(ARQUIVO_RECORDS, "w") as f:
            json.dump([], f)
    with open(ARQUIVO_RECORDS, "r") as f:
        return json.load(f)

def salvar_records(records):
    """Save records to JSON file"""
    with open(ARQUIVO_RECORDS, "w") as f:
        json.dump(records, f, indent=4)

# ========================================
# MODAL CLASSES
# ========================================

class SorteioModal(Modal, title="🎁 Criar Novo Sorteio"):
    def __init__(self, canal_id: int):
        super().__init__(timeout=300)
        self.canal_id = canal_id

        self.titulo = TextInput(
            label="Título do sorteio", 
            placeholder="Ex: Sorteio de gift card", 
            max_length=100
        )
        self.participantes = TextInput(
            label="Participantes (1 por linha)", 
            style=discord.TextStyle.paragraph, 
            placeholder="Ex:\nMaria\nJoão\nCarlos"
        )
        self.data = TextInput(
            label="Data (DD/MM/AAAA HH:MM)", 
            placeholder="Ex: 28/05/2025 18:00"
        )

        self.add_item(self.titulo)
        self.add_item(self.participantes)
        self.add_item(self.data)

    async def on_submit(self, interaction: discord.Interaction):
        # Validate date format and convert to Brazil timezone
        try:
            data_formatada = converter_para_brasil(self.data.value.strip())
        except ValueError:
            await interaction.response.send_message("❌ Data inválida! Use o formato DD/MM/AAAA HH:MM", ephemeral=True)
            return

        # Check if date is in the future
        agora_brasil = obter_agora_brasil()
        if data_formatada <= agora_brasil:
            await interaction.response.send_message("❌ A data do sorteio deve ser no futuro!", ephemeral=True)
            return

        # Process participants
        lista_participantes = [p.strip() for p in self.participantes.value.strip().split("\n") if p.strip()]
        if not lista_participantes:
            await interaction.response.send_message("❌ Adicione pelo menos um participante.", ephemeral=True)
            return

        # Save raffle
        sorteios = carregar_sorteios()
        sorteios.append({
            "titulo": self.titulo.value.strip(),
            "participantes": lista_participantes,
            "data": formatar_data_brasil(data_formatada),
            "feito": False,
            "canal_id": self.canal_id
        })
        salvar_sorteios(sorteios)

        # Create success embed
        embed = discord.Embed(
            title="📢 Sorteio Criado!",
            description=f"**Título:** {self.titulo.value.strip()}\n📅 Data: {formatar_data_brasil(data_formatada)} (horário de Brasília)\n👥 Participantes: {len(lista_participantes)}",
            color=discord.Color.green()
        )
        embed.set_footer(text="O resultado será postado aqui automaticamente. Boa sorte! 🍀")

        # Clean up previous button message
        global msg_com_botao
        if msg_com_botao:
            try:
                await msg_com_botao.delete()
            except:
                pass
            msg_com_botao = None

        await interaction.response.send_message(embed=embed)

class RecordModal(Modal, title="🏁 Criar Record"):
    def __init__(self, autor_id: int):
        super().__init__(timeout=300)
        self.autor_id = autor_id

        self.titulo = TextInput(
            label="Título do Record", 
            placeholder="Ex: Maior número de kills em 1 partida", 
            max_length=100
        )
        self.descricao = TextInput(
            label="Quantidade do seu record", 
            style=discord.TextStyle.paragraph, 
            placeholder="Detalhes do record...", 
            max_length=500
        )

        self.add_item(self.titulo)
        self.add_item(self.descricao)

    async def on_submit(self, interaction: discord.Interaction):
        records = carregar_records()
        records.append({
            "titulo": self.titulo.value.strip(),
            "descricao": self.descricao.value.strip(),
            "autor_id": self.autor_id,
            "tentativas": [],
        })
        salvar_records(records)

        embed = discord.Embed(
            title="✅ Record criado!",
            description=f"🏁 **{self.titulo.value.strip()}**\n📝 {self.descricao.value.strip()}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

class SugestaoModal(discord.ui.Modal, title="Enviar sugestão"):
    sugestao = discord.ui.TextInput(
        label="Qual é sua sugestão?",
        style=discord.TextStyle.paragraph,
        placeholder="Escreve aqui sua ideia pro bot!",
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        dono = await bot.fetch_user(OWNER_ID)
        embed = discord.Embed(
            title="📬 Nova sugestão recebida!",
            description=self.sugestao.value,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Enviado por: {interaction.user} (ID: {interaction.user.id})")

        try:
            await dono.send(embed=embed)
            await interaction.response.send_message("Valeu! Sua sugestão foi enviada!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Não consegui mandar pro dono, tenta avisar ele direto!", ephemeral=True)

@bot.tree.command(name="sugestao", description="Mande uma sugestão pro criador do bot!")
async def sugestao_command(interaction: discord.Interaction):
    await interaction.response.send_modal(SugestaoModal())

# ========================================
# AI COMMANDS
# ========================================

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

# ========================================
# SCHEDULED TASKS
# ========================================

@tasks.loop(minutes=1)
async def checar_sorteios():
    """Check and execute pending raffles"""
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

            # Pick winner and announce
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

# ========================================
# SLASH COMMANDS
# ========================================

@bot.tree.command(name="sortear", description="Criar um sorteio 🎁")
async def slash_sortear(interaction: discord.Interaction):
    ctx = await commands.Context.from_interaction(interaction)
    await sortear(ctx)

@bot.tree.command(name="record", description="Criar um novo record de desafio 🏁")
async def criar_record(interaction: discord.Interaction):
    await interaction.response.send_modal(RecordModal(interaction.user.id))

# ========================================
# RAFFLE COMMANDS
# ========================================

@bot.command()
async def sortear(ctx):
    """Create a new raffle with interactive button"""
    global msg_com_botao
    view = View()

    async def abrir_modal_callback(interaction: discord.Interaction):
        await interaction.response.send_modal(SorteioModal(ctx.channel.id))

    botao = Button(label="Criar Sorteio 🎁", style=discord.ButtonStyle.success)
    botao.callback = abrir_modal_callback
    view.add_item(botao)

    msg_com_botao = await ctx.send("Clique no botão abaixo para abrir o painel de criação de sorteio:", view=view)

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

# ========================================
# RECORD COMMANDS
# ========================================

@bot.command()
async def records(ctx):
    """Display all records"""
    records = carregar_records()
    if not records:
        await ctx.send("❌ Nenhum record foi criado ainda.")
        return

    embed = discord.Embed(title="🏁 Lista de Records", color=discord.Color.orange())
    for i, record in enumerate(records, start=1):
        embed.add_field(
            name=f"{i}. {record['titulo']}",
            value=f"{record['descricao']}\n🎯 Tentativas: {len(record['tentativas'])}",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def tentativa(ctx, id: str = None, valor: str = None):
    """Submit an attempt for a record"""
    if id is None or valor is None:
        await ctx.send("❌ Você deve informar o número do record e a quantidade. Exemplo: `.tentativa 1 50`")
        return

    try:
        id_int = int(id)
    except ValueError:
        await ctx.send("❌ O número do record deve ser um número inteiro válido.")
        return

    try:
        valor_float = float(valor)
    except ValueError:
        await ctx.send("❌ A quantidade deve ser um número válido. Exemplo: 50 ou 3.14")
        return

    records = carregar_records()
    if id_int < 1 or id_int > len(records):
        await ctx.send("❌ Record não encontrado.")
        return

    record = records[id_int - 1]

    # Procura tentativa antiga do usuário
    tentativa_antiga = None
    for t in record["tentativas"]:
        if t["user"] == ctx.author.name:
            tentativa_antiga = t
            break

    agora_brasil = obter_agora_brasil()
    nova_tentativa = {
        "user": ctx.author.name,
        "valor": valor_float,
        "data": formatar_data_brasil(agora_brasil)
    }

    if tentativa_antiga:
        # Substitui tentativa antiga
        record["tentativas"].remove(tentativa_antiga)
        record["tentativas"].append(nova_tentativa)
        await ctx.send(f"✅ Tentativa atualizada para o record **{record['titulo']}** com valor {valor_float}!")
    else:
        # Adiciona nova tentativa
        record["tentativas"].append(nova_tentativa)
        await ctx.send(f"✅ Tentativa adicionada ao record **{record['titulo']}** com valor {valor_float}!")

    salvar_records(records)

@bot.command()
async def ranking(ctx, id: int = None):
    """Display ranking for a specific record by its number"""

    records = carregar_records()
    if not records:
        await ctx.send("❌ Nenhum record foi criado ainda.")
        return

    if id is None:
        await ctx.send("❌ Você precisa informar o número do record. Exemplo: `.ranking 1`")
        return

    if id < 1 or id > len(records):
        await ctx.send("❌ Record não encontrado.")
        return

    record = records[id - 1]
    tentativas = record.get("tentativas", [])

    if not tentativas:
        await ctx.send(f"❌ Nenhuma tentativa registrada para o record **{record['titulo']}**.")
        return

    # Ordena tentativas pelo valor (desc) e depois pela data (asc)
    tentativas_ordenadas = sorted(
        tentativas,
        key=lambda t: (-t["valor"], converter_para_brasil(t["data"]))
    )

    # Construir ranking com medalhas e participantes
    ranking_str = ""
    medalhas = {1: "🥇 Ouro", 2: "🥈 Prata", 3: "🥉 Bronze"}

    for pos, t in enumerate(tentativas_ordenadas, start=1):
        medalha = medalhas.get(pos, f"**{pos}.**")
        ranking_str += f"{medalha} {t['user']} - `{t['valor']}` em {t['data']}\n"

    embed = discord.Embed(
        title=f"🏆 Ranking do Record: {record['titulo']}",
        description=f"📝 {record['descricao']}\n\n{ranking_str}",
        color=discord.Color.gold()
    )
    embed.set_footer(text="Horários em fuso de Brasília")

    await ctx.send(embed=embed)

@bot.command()
async def deletar_record(ctx, id: int):
    """Delete a record (only creator can delete)"""
    records = carregar_records()
    if id < 1 or id > len(records):
        await ctx.send("❌ Record não encontrado.")
        return

    record = records[id - 1]
    if record["autor_id"] != ctx.author.id:
        await ctx.send("❌ Só o criador desse record pode deletar.")
        return

    titulo = record["titulo"]
    del records[id - 1]
    salvar_records(records)

    await ctx.send(f"🗑️ Record **{titulo}** foi deletado com sucesso.")

# ========================================
# FUN COMMANDS
# ========================================

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
    # Load phrases from file
    with open("frases_eu.txt", "r", encoding="utf-8") as f:
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

    # Search through accessible text channels
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

    # Convert message time to Brazil timezone
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
    try:
        await ctx.author.send(
            "**📋 Lista de Comandos Disponíveis:**\n\n"
            "`.oi` - O bot te dá um salve 😎\n"
            "`.rony` - Fala da novata Rony 🐢\n"
            "`.khai` - Elogia o Khai 😘\n"
            "`.gugu` - Avisos sobre quando o Gugu ficará Online 📅\n"
            "`.morena` - Sobre a mais mais (brilho✨) 😘\n"
            "`.comandos` - Manda essa lista aqui no seu PV 📬\n"
            "`.escolha [@alguém]` - Escolhe uma mensagem aleatória da pessoa\n"
            "`.sortear` - Cria um sorteio 🎉\n"
            "`.sorteios` - Mostra a lista de sorteios criados 📜\n"
            "`.eu [@alguém]` - Vai falar algo bem carinhoso para você! 🤞\n"
            "`/record` - Cria um desafio (record) que a galera pode tentar bater 🏁\n"
            "`.records` - Mostra todos os records criados 🎯\n"
            "`.tentativa [número do record] [quantidade]` - Tenta bater um record específico 💥\n"
            "`.ranking [número do record]` mostra o raking record específico 🐱‍👤\n"
            "`.deletar_record [número do record]` - Deleta um record (só quem criou pode excluir) 🗑️\n"
            "`/sugestao` - Envia para nossa caixa de sugestões, uma ideia para ser adicionada no bot 💡\n"
        )
        if ctx.guild:
            await ctx.reply("Te mandei no PV, confere lá! 📬")
    except discord.Forbidden:
        await ctx.reply("Não consegui te mandar DM. Tu precisa liberar as mensagens privadas do servidor. ❌")

# ========================================
# BOT EVENTS
# ========================================

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Processa comandos normalmente
    if message.content.startswith('.') or message.content.startswith('/'):
        await bot.process_commands(message)
        return
    
    # Salva mensagem no histórico
    adicionar_mensagem_conversa(
        canal_id=message.channel.id,
        autor=str(message.author.display_name),
        conteudo=message.content,
        is_bot=False
    )
    
    # Verifica se deve responder (incluindo DM)
    if deve_responder_mensagem(message) or isinstance(message.channel, discord.DMChannel):
        contexto = obter_contexto_conversa(message.channel.id)
        resposta = await gerar_resposta_ai(contexto, pergunta=message.content)
        
        adicionar_mensagem_conversa(
            canal_id=message.channel.id,
            autor="morena",
            conteudo=resposta,
            is_bot=True
        )
        
        await message.channel.send(resposta)
    
    await bot.process_commands(message)

@bot.event
async def on_ready():
    """Bot startup event"""
    agora_brasil = obter_agora_brasil()
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print(f'Bot is ready! Horário atual do Brasil: {formatar_data_brasil(agora_brasil)}')
    print('------')
    
    # Start scheduled tasks
    checar_sorteios.start()

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizei {len(synced)} comandos de barra com sucesso.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos de barra: {e}")

# ========================================
# BOT STARTUP
# ========================================

if __name__ == "__main__":
    bot.run(TOKEN)