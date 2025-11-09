# import sys
# import os

# # Pega o caminho absoluto da pasta 'backend' (que é um nível 'acima' desta pasta 'tests')
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# # Adiciona o 'project_root' ao 'sys.path' (a lista de onde o Python procura por módulos)
# sys.path.insert(0, project_root)

# print(f"\n[conftest.py] Adicionado ao sys.path: {project_root}\n")

# import sys
# import os

# # O diretório 'backend' (onde este arquivo está) é o 'project_root'
# project_root = os.path.dirname(__file__) 

# # Adiciona o 'project_root' ao 'sys.path'
# sys.path.insert(0, project_root)

# print(f"\n[conftest.py ROOT] Adicionado ao sys.path: {project_root}\n")

# import sys
# import os

# # O diretório 'backend' (onde este arquivo está) é o 'project_root'
# project_root = os.path.dirname(os.path.abspath(__file__)) 

# # Adiciona o 'project_root' ao 'sys.path' (a lista de onde o Python procura por módulos)
# sys.path.insert(0, project_root)

# print(f"\n[conftest.py ROOT] Adicionado ao sys.path: {project_root}\n")

# import sys
# import os
# from dotenv import load_dotenv # <-- 1. Importa o dotenv

# # O diretório 'backend' (onde este arquivo está) é o 'project_root'
# project_root = os.path.dirname(os.path.abspath(__file__)) 

# # Adiciona o 'project_root' ao 'sys.path'
# sys.path.insert(0, project_root)

# print(f"\n[conftest.py ROOT] Adicionado ao sys.path: {project_root}\n")

# # --- A SOLUÇÃO INTELIGENTE ---
# # Carrega as variáveis de ambiente (ex: REDIS_URL) do .env
# # ANTES que o pytest tente importar o app/tasks.py
# print("[conftest.py ROOT] Carregando .env...")
# # Assume que o .env está na pasta 'backend'
# load_dotenv(os.path.join(project_root, '.env'))
# print("[conftest.py ROOT] .env carregado.")
# # -----------------------------

import sys
import os
from dotenv import load_dotenv
from unittest.mock import MagicMock # <-- 1. Importa a ferramenta de "mock"

# --- ETAPA 1: "ENGANAR" O SISTEMA DE IMPORTAÇÃO ---
# Esta é a solução para o 'collected 0 items'.
# Nós criamos módulos "falsos" para as dependências pesadas
# que o app/tasks.py tenta importar (e que falham silenciosamente).
# Isso permite que o pytest consiga carregar o app/tasks.py
# e (finalmente) "coletar" seus testes.

MOCK_MODULES = [
    'celery',
    'app.core.database',
    'app.models',
    'app.models.match',
    'app.models.player',
    'app.models.kill',
    'sqlalchemy',
    'sqlalchemy.orm',
    'sqlalchemy.dialects.postgresql',
    'sqlalchemy.sql',
    'psycopg2' # Adiciona o driver do banco, caso ele seja o culpado
]

# Cria um objeto "mágico" (mock) para cada módulo
mock_objects = {mod: MagicMock() for mod in MOCK_MODULES}

# Sobrescreve o sistema de importação do Python:
# Se algum código pedir por 'celery', o Python entregará nosso "MagicMock"
sys.modules.update(mock_objects)

print("\n[conftest.py ROOT] Módulos pesados (celery, sqlalchemy, etc.) foram 'mockados'.\n")


# --- ETAPA 2: CONFIGURAR O SYS.PATH (O que já tínhamos) ---
# O diretório 'backend' (onde este arquivo está) é o 'project_root'
project_root = os.path.dirname(os.path.abspath(__file__)) 
# Adiciona o 'project_root' ao 'sys.path'
sys.path.insert(0, project_root)

print(f"[conftest.py ROOT] Adicionado ao sys.path: {project_root}\n")

# --- ETAPA 3: CARREGAR O .ENV (O que já tínhamos) ---
print("[conftest.py ROOT] Carregando .env...")
# Assume que o .env está na pasta 'backend'
load_dotenv(os.path.join(project_root, '.env'))
print("[conftest.py ROOT] .env carregado.")
# -----------------------------