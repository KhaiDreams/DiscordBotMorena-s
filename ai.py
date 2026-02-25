import os
import json
import datetime
import random
import openai
from typing import List, Dict, Optional
from config import (
    OPENAI_API_KEY,
    ARQUIVO_CONVERSAS,
    ARQUIVO_MEMORIA,
    MAX_CONTEXT_MESSAGES,
    COOLDOWN_SEGUNDOS,
    RESPONSE_CHANCE,
    ULTIMA_RESPOSTA_POR_CANAL,
    AI_TEMPERATURE,
    AI_MAX_TOKENS,
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

# ============ SISTEMA DE MEMÓRIA AUTOMÁTICA ============

def carregar_memoria():
    """Carrega memórias (permanentes + dinâmicas)"""
    if not os.path.exists(ARQUIVO_MEMORIA):
        # Criar memória inicial com documentação permanente
        memoria_inicial = inicializar_memoria_permanente()
        with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
            json.dump(memoria_inicial, f, ensure_ascii=False, indent=2)
        return memoria_inicial
    
    with open(ARQUIVO_MEMORIA, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_memoria(memoria):
    """Salva memórias no arquivo"""
    with open(ARQUIVO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, indent=2, ensure_ascii=False)

def inicializar_memoria_permanente():
    """Cria memória permanente com informações sobre o bot e comandos"""
    return {
        "permanente": {
            "identidade": [
                "Você é a Morena, uma bot do Discord criada por Khai (@khaiydreams no Discord)",
                "Você tem personalidade amazonense de Manaus, debochada mas carismática",
                "Você foi criada para ajudar e interagir com os membros do servidor",
                "Se alguém perguntar algo que você não sabe ou precisar de suporte, diga para entrar em contato com o criador: @khaiydreams no Discord"
            ],
            "comandos": {
                "diversao": [
                    ".oi - Te dá um salve",
                    ".rony, .khai, .morena, .gugu - Informações sobre pessoas",
                    ".eu [@alguém] - Frase carinhosa sobre alguém",
                    ".escolha [@alguém] - Escolhe mensagem aleatória da pessoa",
                    ".sherlock <nome> - Pesquisa perfis em redes sociais",
                    ".comandos - Lista completa de comandos via DM"
                ],
                "economia": [
                    ".double [valor] [v/p/b] - Jogo de apostas! v=vermelho, p=preto, b=branco",
                    ".saldo - Ver seu saldo de moedas",
                    ".transferir [valor] [@alguém] - Transferir dinheiro",
                    ".premios - Ver e resgatar prêmios disponíveis",
                    "/corrida - Corrida de cavalos com apostas!"
                ],
                "sorteios": [
                    ".sortear ou /sortear - Criar um sorteio",
                    ".sorteios - Ver todos os sorteios",
                    ".records - Ver desafios/records criados",
                    ".tentativa [nº] [valor] - Tentar bater um record",
                    ".ranking [nº] - Ver ranking de um record",
                    "/record - Criar novo record de desafio"
                ],
                "estudos": [
                    ".ponto - Iniciar sessão de estudo (precisa estar em call)",
                    "Durante estudo: botões para Pausar/Retomar/Finalizar",
                    ".tempo [@alguém] - Ver tempo estudado",
                    ".rank_estudos - Ranking de estudos do servidor"
                ],
                "tts": [
                    ".call - Bot entra na call e lê mensagens do chat",
                    ".leave - Bot sai da call"
                ],
                "ia": [
                    "Me mencione ou mande DM para conversar comigo",
                    ".limpar_conversa - Limpa histórico (só owner)",
                    ".conversa_info - Stats da conversa",
                    ".ai_stats - Stats gerais da IA (só owner)"
                ],
                "outros": [
                    "/secreto [@alguém] [msg] - Mensagem anônima",
                    "/sugestao - Enviar sugestão pro criador"
                ]
            },
            "como_usar": [
                "Comandos com . (ponto): digite no chat, ex: .oi",
                "Comandos com /: use a barra e escolha na lista, ex: /corrida",
                "Para conversar comigo: me mencione (@Morena) ou mande DM",
                "Sistema de economia: ganhe moedas participando e gaste em apostas/prêmios",
                "Estudos: entre em call e use .ponto para começar a contar tempo"
            ]
        },
        "servidores": {},  # guild_id: {memorias: [], timestamps: []}
        "usuarios": {}  # user_id: {memorias: [], timestamps: []}
    }

def adicionar_memoria_automatica(tipo: str, chave: str, nova_memoria: str, relevancia: int = 5):
    """
    Adiciona memória automaticamente gerenciando limite de 10
    tipo: 'servidores' ou 'usuarios'
    chave: guild_id ou user_id (como string)
    nova_memoria: texto da memória
    relevancia: 1-10 (quanto maior, mais importante)
    """
    memoria = carregar_memoria()
    
    if tipo not in memoria:
        memoria[tipo] = {}
    
    if chave not in memoria[tipo]:
        memoria[tipo][chave] = {
            "memorias": [],
            "relevancia": [],
            "timestamps": []
        }
    
    dados = memoria[tipo][chave]
    
    # Verificar se já existe memória similar (evitar duplicatas)
    for mem_existente in dados["memorias"]:
        if memoria_similar(nova_memoria, mem_existente):
            return  # Já existe, não adiciona
    
    # Adicionar nova memória
    dados["memorias"].append(nova_memoria)
    dados["relevancia"].append(relevancia)
    dados["timestamps"].append(datetime.datetime.now().isoformat())
    
    # Se passou de 10, remover a menos relevante (ou mais antiga se mesma relevância)
    if len(dados["memorias"]) > 10:
        # Encontrar índice da menos relevante
        min_relevancia = min(dados["relevancia"])
        indices_min = [i for i, r in enumerate(dados["relevancia"]) if r == min_relevancia]
        
        # Entre as menos relevantes, pegar a mais antiga
        if len(indices_min) > 1:
            timestamps_min = [dados["timestamps"][i] for i in indices_min]
            idx_mais_antiga = indices_min[timestamps_min.index(min(timestamps_min))]
        else:
            idx_mais_antiga = indices_min[0]
        
        # Remover
        dados["memorias"].pop(idx_mais_antiga)
        dados["relevancia"].pop(idx_mais_antiga)
        dados["timestamps"].pop(idx_mais_antiga)
    
    salvar_memoria(memoria)

def memoria_similar(mem1: str, mem2: str) -> bool:
    """Verifica se duas memórias são muito similares"""
    m1 = mem1.lower().strip()
    m2 = mem2.lower().strip()
    
    # Se uma contém a outra quase completamente
    if len(m1) > 20 and len(m2) > 20:
        if m1 in m2 or m2 in m1:
            return True
    
    # Similaridade por palavras
    palavras1 = set(m1.split())
    palavras2 = set(m2.split())
    
    if len(palavras1) == 0 or len(palavras2) == 0:
        return False
    
    intersecao = len(palavras1 & palavras2)
    uniao = len(palavras1 | palavras2)
    
    similaridade = intersecao / uniao
    return similaridade > 0.7

def obter_memorias(tipo: str, chave: str, limite: int = 10) -> List[str]:
    """Obtém memórias mais relevantes e recentes"""
    memoria = carregar_memoria()
    
    if tipo not in memoria or chave not in memoria[tipo]:
        return []
    
    dados = memoria[tipo][chave]
    if not dados["memorias"]:
        return []
    
    # Ordenar por relevância (desc) e depois por timestamp (desc)
    indices_ordenados = sorted(
        range(len(dados["memorias"])),
        key=lambda i: (dados["relevancia"][i], dados["timestamps"][i]),
        reverse=True
    )
    
    # Retornar as mais relevantes até o limite
    return [dados["memorias"][i] for i in indices_ordenados[:limite]]

async def analisar_e_salvar_memorias(contexto: List[Dict], resposta_bot: str, guild_id: Optional[int] = None, author_id: Optional[int] = None):
    """
    Analisa o contexto da conversa e extrai memórias relevantes automaticamente
    """
    try:
        # Pegar últimas 5 mensagens + resposta do bot para análise
        mensagens_recentes = contexto[-5:] if len(contexto) >= 5 else contexto
        
        # Montar contexto para análise
        contexto_texto = "\n".join([
            f"{msg['autor']}: {msg['conteudo']}" for msg in mensagens_recentes
        ])
        contexto_texto += f"\nMorena: {resposta_bot}"
        
        # Prompt otimizado para análise de memórias (mais conciso)
        prompt_analise = f"""Extraia informações relevantes desta conversa:

EXTRAIA: piadas internas, eventos importantes, relacionamentos, preferências fortes, fatos marcantes.
IGNORE: conversas triviais, mensagens sem contexto relevante.

CONVERSA:
{contexto_texto}

Formato:
SERVIDOR: [memória do grupo ou "nenhuma"]
USUARIO_{author_id}: [memória do usuário ou "nenhuma"]
RELEVANCIA_SERVIDOR: [1-10]
RELEVANCIA_USUARIO: [1-10]"""

        # Fazer análise com GPT (chamada rápida e barata)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Analisador de contexto. Extraia apenas info relevante para memória."},
                {"role": "user", "content": prompt_analise}
            ],
            max_tokens=120,
            temperature=0.3
        )
        
        analise = response.choices[0].message.content.strip()
        
        # Parsear resposta
        linhas = analise.split('\n')
        memoria_servidor = None
        memoria_usuario = None
        rel_servidor = 5
        rel_usuario = 5
        
        for linha in linhas:
            if linha.startswith("SERVIDOR:"):
                mem = linha.replace("SERVIDOR:", "").strip()
                if mem.lower() not in ["nenhuma", "nenhum", "none", ""]:
                    memoria_servidor = mem
            elif linha.startswith(f"USUARIO_{author_id}:"):
                mem = linha.replace(f"USUARIO_{author_id}:", "").strip()
                if mem.lower() not in ["nenhuma", "nenhum", "none", ""]:
                    memoria_usuario = mem
            elif linha.startswith("RELEVANCIA_SERVIDOR:"):
                try:
                    rel_servidor = int(linha.replace("RELEVANCIA_SERVIDOR:", "").strip())
                except:
                    rel_servidor = 5
            elif linha.startswith("RELEVANCIA_USUARIO:"):
                try:
                    rel_usuario = int(linha.replace("RELEVANCIA_USUARIO:", "").strip())
                except:
                    rel_usuario = 5
        
        # Salvar memórias se houver
        if memoria_servidor and guild_id:
            adicionar_memoria_automatica("servidores", f"guild_{guild_id}", memoria_servidor, rel_servidor)
        
        if memoria_usuario and author_id:
            adicionar_memoria_automatica("usuarios", str(author_id), memoria_usuario, rel_usuario)
            
    except Exception as e:
        print(f"Erro ao analisar memórias: {e}")
        # Falha silenciosa - não quebra o bot

def obter_memoria_permanente() -> str:
    """Retorna documentação permanente formatada - só comandos, sem identidade no fluxo ativo"""
    memoria = carregar_memoria()
    permanente = memoria.get("permanente", {})
    
    texto = "## CONHECIMENTO SOBRE OS COMANDOS DO BOT:\n"
    texto += "(Use isso APENAS se alguém perguntar sobre comandos, funcionalidades ou como usar o bot)\n\n"
    
    if "como_usar" in permanente:
        for item in permanente["como_usar"]:
            texto += f"- {item}\n"
        texto += "\n"
    
    if "comandos" in permanente:
        for categoria, cmds in permanente["comandos"].items():
            texto += f"**{categoria.upper()}:** " + " | ".join(cmds[:3]) + "\n"
        texto += "\nPara lista completa: .comandos\n"
    
    return texto

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

def filtrar_mensagens_relevantes(mensagens: List[Dict], bot_name: str = "Morena") -> List[Dict]:
    """Filtra e prioriza mensagens mais relevantes para contexto"""
    mensagens_filtradas = []
    
    for msg in mensagens:
        conteudo = msg["conteudo"].strip()
        
        # Ignorar mensagens muito curtas ou vazias
        if len(conteudo) < 2:
            continue
            
        # Ignorar comandos
        if conteudo.startswith('.') or conteudo.startswith('/'):
            continue
        
        # Priorizar mensagens que mencionam o bot ou são do bot
        msg_copy = msg.copy()
        if bot_name.lower() in conteudo.lower() or msg["is_bot"]:
            msg_copy["prioridade"] = 2
        else:
            msg_copy["prioridade"] = 1
            
        mensagens_filtradas.append(msg_copy)
    
    # Ordenar por timestamp, mas manter as prioritárias
    # Pegar últimas 5 mensagens (reduzido de 8), mas garantir que as prioritárias entrem
    mensagens_prioritarias = [m for m in mensagens_filtradas if m.get("prioridade", 1) == 2]
    mensagens_normais = [m for m in mensagens_filtradas if m.get("prioridade", 1) == 1]
    
    # Mix inteligente: últimas prioritárias + últimas normais
    resultado = (mensagens_prioritarias[-3:] + mensagens_normais[-3:])
    resultado.sort(key=lambda x: x["timestamp"])
    
    return resultado[-5:]

def obter_contexto_conversa(canal_id: int) -> List[Dict]:
    conversas = carregar_conversas()
    canal_str = str(canal_id)
    return conversas.get(canal_str, [])

async def gerar_resposta_ai(contexto: List[Dict], pergunta: str = None, guild_name: str = None, guild_id: Optional[int] = None, user_id: Optional[int] = None) -> str:
    """Gera resposta da IA com contexto inteligente, memórias permanentes e dinâmicas"""
    try:
        # System prompt otimizado e conciso
        system_content = (
            "Você é a Morena, bot do Discord com personalidade amazonense de Manaus.\n"
            "Criada por Khai (@khaiydreams) - mencione APENAS se perguntarem.\n\n"
            "PERSONALIDADE: Debochada mas carismática. Use gírias amazonenses (massa, da hora, maneiro).\n"
            "ESTILO: Respostas curtas (1-3 frases). Max 2 emojis. Jamais fale como robô corporativo.\n"
            "Prefira: tá, pra, né, vc. Seja natural como pessoa real no Discord."
        )
        
        messages = [{"role": "system", "content": system_content}]
        
        # Detectar se pergunta é sobre comandos/funcionalidades
        pergunta_sobre_comandos = False
        if pergunta:
            palavras_comando = ['comando', 'comandos', '.', 'usar', 'funciona', 'como', 'ajuda', 'função', 'feature']
            pergunta_lower = pergunta.lower()
            pergunta_sobre_comandos = any(palavra in pergunta_lower for palavra in palavras_comando)
        
        # Adicionar memória permanente (comandos) APENAS se relevante
        if pergunta_sobre_comandos:
            memoria_permanente = obter_memoria_permanente()
            messages.append({"role": "system", "content": memoria_permanente})
        
        # Adicionar memórias dinâmicas do servidor (reduzido: 8→5)
        if guild_id:
            memorias_servidor = obter_memorias("servidores", f"guild_{guild_id}", limite=5)
            if memorias_servidor:
                servidor_info = f"Memórias sobre este servidor"
                if guild_name:
                    servidor_info += f" ({guild_name})"
                servidor_info += ":\n" + "\n".join(f"- {m}" for m in memorias_servidor)
                messages.append({"role": "system", "content": servidor_info})
        
        # Adicionar memórias do usuário (reduzido: 5→3)
        if user_id:
            memorias_usuario = obter_memorias("usuarios", str(user_id), limite=3)
            if memorias_usuario:
                usuario_info = "Memórias sobre este usuário:\n" + "\n".join(f"- {m}" for m in memorias_usuario)
                messages.append({"role": "system", "content": usuario_info})
        
        # Filtrar e adicionar contexto inteligente
        contexto_filtrado = filtrar_mensagens_relevantes(contexto)
        
        for msg in contexto_filtrado:
            role = "assistant" if msg["is_bot"] else "user"
            content = f"{msg['autor']}: {msg['conteudo']}" if not msg["is_bot"] else msg["conteudo"]
            messages.append({"role": role, "content": content})
        
        if pergunta:
            messages.append({"role": "user", "content": pergunta})
        
        # Fazer chamada à API com parâmetros otimizados
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=AI_MAX_TOKENS,
            temperature=AI_TEMPERATURE
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
    """Decide se o bot deve responder, com detecção de intenção melhorada"""
    canal_id = message.channel.id
    bot = message.guild.me if message.guild else None
    
    # Sempre responder se mencionado diretamente
    if bot and bot in message.mentions:
        return True
    
    # Sempre responder se for reply ao bot
    if message.reference and message.reference.resolved and message.reference.resolved.author == bot:
        return True
    
    # Nunca responder a bots, comandos ou mensagens vazias
    if message.author.bot or message.content.startswith('.') or message.content.startswith('/'):
        return False
    
    # Aumentar chance se mensagem contém palavras-chave relacionadas ao bot
    conteudo_lower = message.content.lower()
    palavras_chave = ['morena', 'bot', 'ia', 'ajuda', 'oi', 'olá', 'hello', 'hey']
    tem_palavra_chave = any(palavra in conteudo_lower for palavra in palavras_chave)
    
    # Aumentar chance se mensagem é pergunta
    eh_pergunta = '?' in message.content
    
    # Sistema de cooldown
    agora = datetime.datetime.now()
    ultima_resposta = ULTIMA_RESPOSTA_POR_CANAL.get(canal_id)
    if ultima_resposta:
        delta = (agora - ultima_resposta).total_seconds()
        if delta < COOLDOWN_SEGUNDOS:
            # Só ignora cooldown se for palavra-chave ou pergunta direta
            if not (tem_palavra_chave or eh_pergunta):
                return False
    
    # Chance ajustada baseada em contexto
    chance_base = RESPONSE_CHANCE
    if tem_palavra_chave:
        chance_base *= 4  # 20% se mencionar palavras-chave
    if eh_pergunta:
        chance_base *= 2  # 10% se for pergunta
    
    # Limitar máximo a 50%
    chance_base = min(chance_base, 0.5)
    
    if random.random() < chance_base:
        ULTIMA_RESPOSTA_POR_CANAL[canal_id] = agora
        return True
    
    return False
