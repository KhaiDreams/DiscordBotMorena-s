# Morena's Bot

Bem-vindo ao repositório do bot do Discord que traz diversão, interação e inteligência artificial para a sua comunidade!

![Imagem do Bot Original](https://i.pinimg.com/736x/4a/ed/87/4aed876443db2b9c242869505915a1df.jpg)

---

## Sobre o Bot

Este bot é um assistente multifuncional para servidores Discord, desenvolvido para facilitar a interação entre os membros com comandos divertidos, sorteios, records e funcionalidades com IA que tornam o ambiente mais dinâmico e amigável.

Ele foi criado para ajudar a organizar eventos, incentivar desafios e proporcionar momentos descontraídos entre a galera, além de contar com respostas inteligentes baseadas em IA para tornar as conversas ainda mais naturais e interessantes.

Ele acompanha o chat do seu servidor e responde de tempos em tempos com o contexto da conversa, caso queira conversar com ele basta apenas marcá-lo com @ ou responder uma mensagem dele!

(É possível conversar no privado também)

OBS: Caso queira usar o código para seu próprio bot fique à vontade! Apenas configure o código e rode.

---

## Funcionalidades Principais

- **Interação simples e divertida:** comandos que respondem com mensagens carinhosas e engraçadas.
- **Sorteios automáticos:** crie e gerencie sorteios de forma prática.
- **Sistema de Records:** desafie a galera com desafios que podem ser batidos e acompanhe o ranking.
- **Sugestões:** receba ideias para melhorar o bot diretamente da comunidade no seu privado.
- **IA integrada:** respostas inteligentes e contextuais, tornando as interações mais naturais e personalizadas.

---

## 📋 Lista de Comandos Disponíveis

| Comando                      | Descrição                                           |
|------------------------------|----------------------------------------------------|
| `.oi`                        | O bot te dá um salve 😎                             |
| `.rony`                      | Fala da novata Rony 🐢                              |
| `.khai`                      | Elogia o Khai 😘                                    |
| `.gugu`                      | Avisos sobre quando o Gugu ficará Online 📅         |
| `.morena`                    | Sobre a mais mais (brilho✨) 😘                      |
| `.comandos`                  | Manda essa lista aqui no seu PV 📬                  |
| `.escolha [@alguém]`         | Escolhe uma mensagem aleatória da pessoa            |
| `.sortear`                   | Cria um sorteio 🎉                                  |
| `.sorteios`                  | Mostra a lista de sorteios criados 📜               |
| `.eu [@alguém]`              | Vai falar algo bem carinhoso para você! 🤞          |
| `/record`                    | Cria um desafio (record) que a galera pode tentar bater 🏁 |
| `.records`                   | Mostra todos os records criados 🎯                   |
| `.tentativa [nº record] [quantidade]` | Tenta bater um record específico 💥                |
| `.ranking [nº record]`       | Mostra o ranking do record específico 🐱‍👤           |
| `.deletar_record [nº record]`| Deleta um record (só quem criou pode excluir) 🗑️    |
| `/sugestao`                  | Envia uma ideia para a caixa de sugestões do bot 💡 |

---

## Como Usar

1. Convide o bot para o seu servidor Discord.
2. Use os comandos prefixados por `.` ou os comandos slash `/` para interagir.
3. Para comandos que pedem menção de usuário, use o formato `@usuario`.
4. Aproveite a diversão, participe dos sorteios e desafios!

---

## Tecnologias Utilizadas

- Python 3.13
- APIs de IA para respostas inteligentes (OpenAI)

---

## Como Instalar e Rodar o Bot

Siga os passos abaixo para colocar o bot no ar no seu servidor:

1. Clone este repositório ou baixe o código fonte.

```bash
git clone https://github.com/seuusuario/morenas-bot.git
cd morenas-bot
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
