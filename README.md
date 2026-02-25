# Morena's Bot

Bem-vindo ao repositório do bot do Discord que traz diversão, interação, inteligência artificial e produtividade para a sua comunidade!

![Imagem do Bot Original](https://i.pinimg.com/736x/4a/ed/87/4aed876443db2b9c242869505915a1df.jpg)

---

## Sobre o Bot

Este bot é um assistente multifuncional para servidores Discord, desenvolvido para facilitar a interação entre os membros com comandos divertidos, sorteios, records, sistema de economia, apostas e funcionalidades com IA que tornam o ambiente mais dinâmico e amigável.

Ele foi criado para ajudar a organizar eventos, incentivar desafios, acompanhar horas de estudo, proporcionar momentos descontraídos entre a galera, além de contar com respostas inteligentes baseadas em IA para tornar as conversas ainda mais naturais e interessantes.

Ele acompanha o chat do seu servidor e responde de tempos em tempos com o contexto da conversa. Caso queira conversar com ele, basta apenas marcá-lo com @ ou responder uma mensagem dele!

*É possível conversar no privado também!*

**OBS:** Caso queira usar o código para seu próprio bot, fique à vontade! Apenas configure o código e rode.

---

## Funcionalidades Principais

- **Interação simples e divertida:** comandos que respondem com mensagens carinhosas e engraçadas.
- **Sorteios automáticos:** crie e gerencie sorteios de forma prática com sistema de agendamento e notificação automática.
- **Sistema de Records:** desafie a galera com desafios que podem ser batidos e acompanhe o ranking de cada record.
- **Economia e Apostas:** sistema completo de saldo, transferências, double (roleta) e corrida de cavalos com apostas multiplayer.
- **Acompanhamento de Estudos:** registre sessões de estudo com controle de tempo, pausas, e acompanhe estatísticas e rankings de dedicação.
- **Sistema de Prêmios:** resgate prêmios usando o saldo virtual acumulado.
- **Sugestões:** receba ideias para melhorar o bot diretamente da comunidade.
- **IA integrada:** respostas inteligentes e contextuais usando OpenAI, o bot aprende com o histórico de conversas.
- **Mensagens anônimas:** envie mensagens secretas para outros membros do servidor.
- **Sistema de tasks automatizadas:** o bot muda status automaticamente, verifica sorteios agendados e gerencia economia.

---

## Lista de Comandos Disponíveis

### Comandos Gerais

| Comando | Descrição |
|---------|-----------|
| `.oi` | O bot te dá um salve |
| `.rony` | Fala da novata Rony |
| `.khai` | Elogia o Khai |
| `.gugu` | Avisos sobre quando o Gugu ficará Online |
| `.morena` | Sobre a mais mais (brilho) |
| `.comandos` | Manda a lista completa de comandos no seu PV |
| `.escolha [@alguém]` | Escolhe uma mensagem aleatória da pessoa |
| `.eu [@alguém]` | Vai falar algo bem carinhoso para você |

### Sorteios e Desafios

| Comando | Descrição |
|---------|-----------|
| `.sortear` | Cria um sorteio com data e hora programada |
| `.sorteios` | Mostra a lista de sorteios criados |
| `/record` | Cria um desafio (record) que a galera pode tentar bater |
| `.records` | Mostra todos os records criados |
| `.tentativa [nº] [quantidade]` | Tenta bater um record específico |
| `.ranking [nº]` | Mostra o ranking do record específico |
| `.deletar_record [nº]` | Deleta um record (só quem criou pode) |

### Economia e Apostas

| Comando | Descrição |
|---------|-----------|
| `.saldo` | Consulta seu saldo atual |
| `.double [valor] [v/p/b]` | Aposta no Double (Vermelho, Preto ou Branco) |
| `.transferir [valor] [@alguém]` | Transfere dinheiro para outro membro |
| `.premios` | Mostra a lista de prêmios disponíveis para resgate |
| `/corrida` | Inicia uma corrida de cavalos com apostas |

### Sistema de Estudos

| Comando | Descrição |
|---------|-----------|
| `.ponto` | Inicia o acompanhamento de horas de estudo (precisa estar em call) |
| `.tempo [@alguém]` | Mostra quanto tempo você ou outra pessoa estudou |
| `.rank_estudos` | Mostra o ranking de quem mais estudou no servidor |

### TTS (Text-to-Speech)

| Comando | Descrição |
|---------|-----------|
| `.call` | Bot entra na call e lê todas as mensagens do chat em voz alta |
| `.leave` | Bot sai do canal de voz |

### Outros

| Comando | Descrição |
|---------|-----------|
| `/sugestao` | Envia uma ideia para a caixa de sugestões do bot |
| `/secreto @alguém <msg>` | Envia uma mensagem anônima no PV de alguém |
| `.limpar_conversa` | Limpa o histórico de conversa da IA no canal (apenas dono do bot) |
| `.conversa_info` | Mostra estatísticas da conversa com a IA |

---

## Destaques dos Sistemas

### Inteligência Artificial Conversacional
O bot possui integração completa com OpenAI GPT para conversas naturais!

- **Respostas contextuais:** O bot mantém histórico das últimas mensagens e responde de forma coerente
- **Menções automáticas:** Basta mencionar o bot ou responder uma mensagem dele
- **Conversas privadas:** Funciona também em DM
- **Chance aleatória:** O bot pode responder espontaneamente em conversas (5% de chance)
- **Cooldown inteligente:** Sistema de cooldown para evitar spam
- **Gerenciamento de contexto:** Limite de mensagens no histórico para otimizar respostas

### Sistema de Estudos
Acompanhe e incentive os estudos no seu servidor!

- **Iniciar sessão:** Use `.ponto` enquanto estiver em uma call de voz
- **Controles interativos:** Botões para pausar, retomar e finalizar a sessão
- **Finalização automática:** Sair da call encerra a sessão automaticamente
- **Estatísticas completas:** Veja tempo total, histórico por dia, média e ranking do servidor
- **Múltiplos usuários:** Várias pessoas podem estudar simultaneamente

### Corrida de Cavalos
Sistema de apostas em grupo para corridas emocionantes!

- **Apostas em tempo real:** 30 segundos para todos apostarem nos cavalos
- **Sistema de prêmios dinâmico:** Distribuição justa baseada nas apostas
- **Animação da corrida:** Acompanhe o progresso em tempo real
- **Multiplayer:** Todos podem apostar juntos em diferentes cavalos

### Sistema Double
Aposte em vermelho, preto ou branco!

- **Multiplicadores:** 2x para vermelho/preto, 14x para branco
- **Animação de roleta:** Experiência visual imersiva com rolagem dos slots
- **Sistema de saldo integrado:** Ganhe ou perca dinheiro virtual
- **Probabilidades realistas:** 47% vermelho, 47% preto, 5% branco
- **Proteção contra spam:** Sistema anti-apostas simultâneas

### Sistema de Sorteios
Organize sorteios completos com agendamento automático!

- **Criação fácil:** Interface com modal para preencher informações
- **Agendamento:** Defina data e hora exata para o sorteio
- **Participação simples:** Botão de participar na mensagem do sorteio
- **Sorteio automático:** O bot realiza o sorteio automaticamente na hora marcada
- **Histórico completo:** Comando `.sorteios` mostra todos os sorteios (pendentes e realizados)
- **Notificações:** Anúncio automático do vencedor no canal do sorteio

### Sistema de Records (Desafios)
Crie desafios competitivos para a comunidade!

- **Criação via modal:** Use `/record` para criar um novo desafio
- **Tipos de record:** Escolha entre "maior valor" ou "menor valor"
- **Sistema de tentativas:** Membros fazem tentativas com `.tentativa [nº] [valor]`
- **Ranking dinâmico:** Veja o top 10 de cada record com `.ranking [nº]`
- **Gestão completa:** Liste todos os records e delete os seus próprios
- **Histórico de tentativas:** Cada record mantém registro de todas as tentativas

### Sistema de Economia Completo
Gerencie a economia virtual do servidor!

- **Saldo inicial:** Todo novo membro recebe 1000 de saldo
- **Transferências:** Envie dinheiro para outros membros
- **Sistema de prêmios:** Configure prêmios resgatáveis com estoque
- **Múltiplas formas de ganhar:** Double, corrida de cavalos, e futuros eventos
- **Persistência:** Todos os saldos são salvos automaticamente

---

## Como Usar

1. **Convide o bot** para o seu servidor Discord.
2. Use os **comandos prefixados** por `.` ou os **comandos slash** `/` para interagir.
3. Para comandos que pedem menção de usuário, use o formato `@usuario`.
4. **Para conversar com o bot:** mencione-o com `@` ou responda uma mensagem dele.
5. **Sistema de estudos:** Entre em uma call de voz e use `.ponto` para começar.
6. **Apostas e jogos:** Use `.saldo` para verificar seu dinheiro e começar a jogar!
7. **Sorteios:** Use `.sortear`, preencha o modal e compartilhe com a galera.
8. Aproveite a diversão, participe dos sorteios e desafios!

---

## Funcionalidades Automáticas

O bot possui diversas funcionalidades que funcionam automaticamente em segundo plano:

- **Status dinâmico:** O bot alterna entre diferentes status automaticamente
- **Verificação de sorteios:** Verifica a cada 30 segundos se há sorteios para realizar
- **Finalização automática de estudos:** Se você sair da call, a sessão é encerrada automaticamente
- **Reset de economia:** Sistema de reset de valores mínimos (se configurado)
- **Salvamento automático:** Todos os dados são salvos automaticamente após cada ação

---

## Tecnologias Utilizadas

- **Python 3.13** - Linguagem principal
- **discord.py** - Biblioteca para interação com Discord API
- **OpenAI API** - Integração com GPT para respostas inteligentes
- **pytz** - Gerenciamento de fusos horários (horário de Brasília)
- **asyncio** - Programação assíncrona para melhor performance
- **JSON** - Armazenamento persistente de dados

---

## Estrutura do Projeto

```
MorenaBot/
├── main.py                 # Arquivo principal do bot
├── config.py              # Configurações e variáveis de ambiente
├── utils.py               # Funções utilitárias (data, economia, etc)
├── ai.py                  # Sistema de IA e conversas
├── ai_commands.py         # Comandos relacionados à IA
├── economy_commands.py    # Comandos de economia (double, saldo, etc)
├── study_commands.py      # Sistema de acompanhamento de estudos
├── raffle_commands.py     # Sistema de sorteios
├── record_commands.py     # Sistema de records/desafios
├── fun_commands.py        # Comandos divertidos e interativos
├── horse_race_slash.py    # Corrida de cavalos
├── modals.py              # Modais do Discord (formulários)
├── tasks_module.py        # Tasks automatizadas (sorteios, status)
├── requirements.txt       # Dependências do projeto
├── Dockerfile             # Configuração do container Docker
├── docker-compose.yml     # Orquestração do Docker
├── .dockerignore          # Arquivos ignorados pelo Docker
├── .env                   # Variáveis de ambiente (não versionado)
└── data/                  # Pasta de dados persistentes
    ├── conversas.json     # Histórico de conversas da IA
    ├── economia.json      # Saldos dos usuários
    ├── estudos.json       # Sessões e estatísticas de estudo
    ├── premios.json       # Prêmios disponíveis
    ├── records.json       # Records criados
    ├── sorteios.json      # Sorteios criados
    └── frases_eu.txt      # Frases para o comando .eu
```

---

## Como Instalar e Rodar o Bot

### Opção 1: Instalação Tradicional (Python)

Siga os passos abaixo para colocar o bot no ar no seu servidor:

1. Clone este repositório ou baixe o código fonte.

```bash
git clone https://github.com/KhaiDreams/DiscordBotMorena-s.git
cd DiscordBotMorena-s
```

2. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Instale as dependências listadas no arquivo requirements.txt:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente necessárias, como o token do Discord e as chaves da API de IA (exemplo do .env):
```bash
DISCORD_TOKEN=seu_token_aqui
OPENAI_API_KEY=sua_chave_openai_aqui
```

5. Inicie o Bot:
```bash
python main.py
```

O bot irá:
- Carregar todos os módulos e comandos
- Conectar ao Discord
- Sincronizar os comandos slash
- Iniciar as tasks automatizadas
- Exibir "Bot is ready!" quando estiver online

### Opção 2: Usando Docker (Recomendado para Produção)

O Docker facilita a execução do bot em qualquer ambiente sem se preocupar com dependências.

**Pré-requisitos:**
- Docker instalado ([Download](https://www.docker.com/get-started))
- Docker Compose instalado (geralmente já vem com o Docker Desktop)

**Passos:**

1. Clone o repositório:
```bash
git clone https://github.com/KhaiDreams/DiscordBotMorena-s.git
cd DiscordBotMorena-s
```

2. Crie o arquivo `.env` na raiz do projeto com suas credenciais:
```bash
DISCORD_TOKEN=seu_token_aqui
OPENAI_API_KEY=sua_chave_openai_aqui
```

3. Construa e inicie o container:
```bash
docker-compose up -d
```

O bot estará rodando em segundo plano!

**Comandos úteis do Docker:**

```bash
# Ver logs do bot
docker-compose logs -f

# Parar o bot
docker-compose down

# Reiniciar o bot
docker-compose restart

# Ver status do container
docker-compose ps

# Reconstruir a imagem após mudanças no código
docker-compose up -d --build
```

**Vantagens do Docker:**
- Ambiente isolado e consistente
- Fácil de fazer backup (apenas a pasta `data/`)
- Reinício automático em caso de falhas
- Fácil de migrar para outro servidor
- Não precisa instalar Python ou dependências manualmente

**Persistência de Dados:**

Os dados do bot (economia, sorteios, estudos, etc.) são salvos na pasta `data/` e são automaticamente persistidos através de volumes do Docker. Mesmo que você reconstrua o container, os dados permanecerão intactos.

---

## Contribuindo

Sinta-se livre para fazer fork do projeto e contribuir com melhorias! 

Sugestões de contribuição:
- Novos comandos divertidos
- Melhorias no sistema de economia
- Novos jogos de apostas
- Otimizações de performance
- Correções de bugs

---

## Licença

Este projeto é de código aberto. Sinta-se livre para usar, modificar e distribuir conforme necessário.

---

## Contato e Suporte

Para sugestões, bugs ou dúvidas, use o comando `/sugestao` dentro do bot ou abra uma issue neste repositório.

**Desenvolvido com dedicação para a comunidade Discord!**
