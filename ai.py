import os
import json
import datetime
import random
import openai
from typing import List, Dict
from config import (
    OPENAI_API_KEY,
    ARQUIVO_CONVERSAS,
    MAX_CONTEXT_MESSAGES,
    COOLDOWN_SEGUNDOS,
    RESPONSE_CHANCE,
    ULTIMA_RESPOSTA_POR_CANAL,
)

import discord

openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()

def carregar_conversas():
    if not os.path.exists(ARQUIVO_CONVERSAS):
        with open(ARQUIVO_CONVERSAS, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)
    with open(ARQUIVO_CONVERSAS, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_conversas(conversas):
    with open(ARQUIVO_CONVERSAS, "w", encoding="utf-8") as f:
        json.dump(conversas, f, indent=4, ensure_ascii=False)

def adicionar_mensagem_conversa(canal_id: int, autor: str, conteudo: str, is_bot: bool = False):
    conversas = carregar_conversas()
    canal_str = str(canal_id)
    if canal_str not in conversas:
        conversas[canal_str] = []
    mensagem = {
        "autor": autor,
        "conteudo": conteudo,
        "timestamp": datetime.datetime.now().isoformat(),
        "is_bot": is_bot
    }
    conversas[canal_str].append(mensagem)
    if len(conversas[canal_str]) > MAX_CONTEXT_MESSAGES:
        conversas[canal_str] = conversas[canal_str][-MAX_CONTEXT_MESSAGES:]
    salvar_conversas(conversas)

def obter_contexto_conversa(canal_id: int) -> List[Dict]:
    conversas = carregar_conversas()
    canal_str = str(canal_id)
    return conversas.get(canal_str, [])

async def gerar_resposta_ai(contexto: List[Dict], pergunta: str = None) -> str:
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é a Morena, uma bot do Discord com personalidade forte. "
                    "Fala como uma amazonese de manaus, com gírias, ousadia e jeito debochado. "
                    "Suas respostas são curtas, diretas, mas sempre com emoção. "
                    "Usa emojis com moderação e reage como uma pessoa de verdade. "
                    "Não fala como um robô, e não precisa ser polida demais."
                )
            }
        ]
        for msg in contexto[-6:]:
            role = "assistant" if msg["is_bot"] else "user"
            content = f"{msg['autor']}: {msg['conteudo']}" if not msg["is_bot"] else msg["conteudo"]
            messages.append({"role": role, "content": content})
        if pergunta:
            messages.append({"role": "user", "content": pergunta})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
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
    canal_id = message.channel.id
    bot = message.guild.me if message.guild else None
    if bot and bot in message.mentions:
        return True
    if message.reference and message.reference.resolved and message.reference.resolved.author == bot:
        return True
    if message.author.bot or message.content.startswith('.') or message.content.startswith('/'):
        return False
    agora = datetime.datetime.now()
    ultima_resposta = ULTIMA_RESPOSTA_POR_CANAL.get(canal_id)
    if ultima_resposta:
        delta = (agora - ultima_resposta).total_seconds()
        if delta < COOLDOWN_SEGUNDOS:
            return False
    if random.random() < RESPONSE_CHANCE:
        ULTIMA_RESPOSTA_POR_CANAL[canal_id] = agora
        return True
    return False
