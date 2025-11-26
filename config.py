import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OWNER_ID = 329265386153443329   # Substitua pelo seu ID do Discord

# Caminhos dos arquivos de dados
ARQUIVO_SORTEIOS = "data/sorteios.json"
ARQUIVO_RECORDS = "data/records.json"
ARQUIVO_CONVERSAS = "data/conversas.json"
ARQUIVO_ECONOMIA = "data/economia.json"
ARQUIVO_PREMIOS = "data/premios.json"
ARQUIVO_ESTUDOS = "data/estudos.json"

# Configurações de IA
COOLDOWN_SEGUNDOS = 60
MAX_CONTEXT_MESSAGES = 10
RESPONSE_CHANCE = 0.05

# Outras variáveis globais
msg_com_botao = None
ULTIMA_RESPOSTA_POR_CANAL = {}
