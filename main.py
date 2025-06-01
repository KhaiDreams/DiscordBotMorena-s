import discord
from discord.ext import commands
from utils import (
    obter_agora_brasil,
    formatar_data_brasil,
)
from config import (
    TOKEN,
)
from ai import (
    adicionar_mensagem_conversa,
    obter_contexto_conversa,
    gerar_resposta_ai,
    deve_responder_mensagem,
)
from raffle_commands import register_raffle_commands
from fun_commands import setup_fun_commands
from ai_commands import register_ai_commands
from modals import RecordModal, SugestaoModal
from tasks_module import register_tasks
from record_commands import register_record_commands
from discord import app_commands


# Bot configuration
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

# ========================================
# SLASH COMMANDS
# ========================================

@bot.tree.command(name="secreto", description="Mande uma mensagem anônima pra alguém via bot.")
@app_commands.describe(usuario="Pessoa que vai receber a mensagem", mensagem="O que você quer enviar")
async def secreto(interaction: discord.Interaction, usuario: discord.User, mensagem: str):
    try:
        # Tenta mandar a mensagem no PV do alvo
        await usuario.send(
            f"📩 **Mensagem secreta recebida:**\n>>> {mensagem}"
        )

        await interaction.response.send_message("✅ Mensagem enviada de forma anônima!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Não consegui enviar a DM. O usuário pode ter o PV fechado.", ephemeral=True)


@bot.tree.command(name="sortear", description="Criar um sorteio 🎁")
async def slash_sortear(interaction: discord.Interaction):
    from raffle_commands import sortear_command_slash
    await sortear_command_slash(bot, interaction)

@bot.tree.command(name="record", description="Criar um novo record de desafio 🏁")
async def criar_record(interaction: discord.Interaction):
    await interaction.response.send_modal(RecordModal(interaction.user.id))

@bot.tree.command(name="sugestao", description="Mande uma sugestão pro criador do bot!")
async def sugestao_command(interaction: discord.Interaction):
    await interaction.response.send_modal(SugestaoModal())

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
    # Inicie as tasks aqui, dentro do event loop
    if not getattr(bot, "tasks_started", False):
        bot.mudar_status_task.start()
        bot.checar_sorteios_task.start()
        bot.tasks_started = True
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizei {len(synced)} comandos de barra com sucesso.")
    except Exception as e:
        print(f"Erro ao sincronizar comandos de barra: {e}")

# ========================================
# BOT STARTUP
# ========================================

if __name__ == "__main__":
    # Registre todos os comandos e eventos necessários ANTES de rodar o bot
    setup_fun_commands(bot)
    register_raffle_commands(bot)
    register_record_commands(bot)
    register_ai_commands(bot)
    register_tasks(bot)
    bot.run(TOKEN)