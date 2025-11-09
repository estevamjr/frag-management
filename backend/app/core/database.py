# backend/app/core/database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Lê a URL de conexão ÚNICA do .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Verificação de segurança
if DATABASE_URL is None:
    raise ValueError("Erro: A variável DATABASE_URL não foi encontrada no arquivo .env")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()