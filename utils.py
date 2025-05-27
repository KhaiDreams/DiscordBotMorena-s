import datetime
import pytz
import os
import json

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

ARQUIVO_SORTEIOS = "data/sorteios.json"
ARQUIVO_RECORDS = "data/records.json"

def carregar_sorteios():
    if not os.path.exists(ARQUIVO_SORTEIOS):
        with open(ARQUIVO_SORTEIOS, "w") as f:
            json.dump([], f)
    with open(ARQUIVO_SORTEIOS, "r") as f:
        return json.load(f)

def salvar_sorteios(sorteios):
    with open(ARQUIVO_SORTEIOS, "w") as f:
        json.dump(sorteios, f, indent=4)

def carregar_records():
    if not os.path.exists(ARQUIVO_RECORDS):
        with open(ARQUIVO_RECORDS, "w") as f:
            json.dump([], f)
    with open(ARQUIVO_RECORDS, "r") as f:
        return json.load(f)

def salvar_records(records):
    with open(ARQUIVO_RECORDS, "w") as f:
        json.dump(records, f, indent=4)
