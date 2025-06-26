import datetime
import pytz
import os
import json
from config import ARQUIVO_SORTEIOS, ARQUIVO_RECORDS, ARQUIVO_ECONOMIA

# Data e hora no fuso horário do Brasil
fuso_brasil = pytz.timezone("America/Sao_Paulo")

def obter_agora_brasil():
    return datetime.datetime.now(fuso_brasil)

def formatar_data_brasil(dt):
    if dt.tzinfo is None:
        dt = fuso_brasil.localize(dt)
    return dt.strftime("%d/%m/%Y %H:%M")

def converter_para_brasil(dt_string):
    dt_naive = datetime.datetime.strptime(dt_string, "%d/%m/%Y %H:%M")
    return fuso_brasil.localize(dt_naive)

# Sorteios
def carregar_sorteios():
    if not os.path.exists(ARQUIVO_SORTEIOS):
        with open(ARQUIVO_SORTEIOS, "w") as f:
            json.dump([], f)
    with open(ARQUIVO_SORTEIOS, "r") as f:
        return json.load(f)

def salvar_sorteios(sorteios):
    with open(ARQUIVO_SORTEIOS, "w") as f:
        json.dump(sorteios, f, indent=4)

# Records
def carregar_records():
    if not os.path.exists(ARQUIVO_RECORDS):
        with open(ARQUIVO_RECORDS, "w") as f:
            json.dump([], f)
    with open(ARQUIVO_RECORDS, "r") as f:
        return json.load(f)

def salvar_records(records):
    with open(ARQUIVO_RECORDS, "w") as f:
        json.dump(records, f, indent=4)

# Apostas
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
    dados = carregar_dados(ARQUIVO_ECONOMIA, {})
    if str(user_id) not in dados:
        dados[str(user_id)] = 1000
        salvar_dados(ARQUIVO_ECONOMIA, dados)
    return dados[str(user_id)]

def alterar_saldo(user_id, valor):
    dados = carregar_dados(ARQUIVO_ECONOMIA, {})
    dados[str(user_id)] = dados.get(str(user_id), 1000) + valor
    salvar_dados(ARQUIVO_ECONOMIA, dados)

def debitar_saldo(user_id, valor):
    alterar_saldo(user_id, -abs(valor))

def adicionar_saldo(user_id, valor):
    alterar_saldo(user_id, abs(valor))