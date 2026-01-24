# FFmpeg para TTS

O sistema de TTS (Text-to-Speech) do bot requer o **FFmpeg** para processar o áudio.

**FFmpeg** é um software open-source que converte e processa áudio/vídeo. O bot usa ele para transformar os arquivos MP3 gerados pelo Google TTS em streaming de áudio para o Discord.

## 🐳 Docker (Recomendado)

**Se você roda o bot no Docker, não precisa instalar nada!** O FFmpeg já está configurado no Dockerfile e será instalado automaticamente no container.

Apenas rode:
```bash
docker-compose up --build
```

E tudo funcionará! ✅

---

## 💻 Instalação Local (apenas se não usar Docker)

### Opção 1: Chocolatey (Recomendado)
Se você tem o Chocolatey instalado, abra o PowerShell como Administrador e execute:
```powershell
choco install ffmpeg
```

### Opção 2: Download Manual
1. Acesse: https://www.gyan.dev/ffmpeg/builds/
2. Baixe a versão "ffmpeg-release-essentials.zip"
3. Extraia o conteúdo para `C:\ffmpeg`
4. Adicione `C:\ffmpeg\bin` às variáveis de ambiente:
   - Pressione Win + X e selecione "Sistema"
   - Clique em "Configurações avançadas do sistema"
   - Clique em "Variáveis de Ambiente"
   - Em "Variáveis do sistema", encontre "Path" e clique em "Editar"
   - Clique em "Novo" e adicione: `C:\ffmpeg\bin`
   - Clique em "OK" em todas as janelas
5. Reinicie o terminal/PowerShell

### Verificar Instalação
Abra um novo terminal e execute:
```bash
ffmpeg -version
```

Se aparecer a versão do FFmpeg, está instalado corretamente!

## Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

## macOS
```bash
brew install ffmpeg
```

## Teste o FFmpeg com Python
Após instalar, teste se o bot consegue acessar:
```python
import subprocess
result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
print(result.stdout.decode())
```

---

## Como usar o TTS no Bot

1. Entre em um canal de voz no Discord
2. Use o comando `.call` no chat de texto que você quer que seja lido
3. O bot entrará na call e começará a ler tudo que for escrito naquele chat
4. Formato: "Nome disse: mensagem"
5. Quando você sair da call, o bot sairá automaticamente

**Comandos:**
- `.call` - Bot entra na call e começa a ler mensagens
- `.leave` - Bot sai manualmente da call

**Observações:**
- O bot só lê mensagens do canal onde foi chamado
- Mensagens muito longas (>200 caracteres) são truncadas
- O bot não lê comandos (que começam com `.` ou `/`)
- Usa Google TTS com voz em português
