# Use Python 3.10 slim como base (compatível com as dependências)
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para voz no Discord
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libopus0 \
    libopus-dev \
    libffi-dev \
    libnacl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do bot para o container
COPY . .

# Cria o diretório de dados se não existir
RUN mkdir -p data

# Define variáveis de ambiente padrão (serão sobrescritas pelo .env)
ENV PYTHONUNBUFFERED=1

# Comando para iniciar o bot
CMD ["python", "main.py"]
