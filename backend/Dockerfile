# Usamos uma imagem Python slim como base
FROM python:3.11-slim

# Definimos o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copia todo o código do backend para o container
COPY . .

# Expõe a porta 8000 (onde o Uvicorn vai rodar)
EXPOSE 8000

# O comando para iniciar a API
# Rodamos o uvicorn no host 0.0.0.0 para que ele seja acessível
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]