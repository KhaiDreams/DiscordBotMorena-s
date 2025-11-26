# Use Python 3.12 slim como base
FROM python:3.12-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    git \
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
