# backend/app/services/match.py

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from typing import List
import uuid
import json

from app.models import match as match_models
from app.schemas import match as match_schemas

def get_match_by_id(db: Session, match_id: str):
    """
    Busca uma partida pelo seu match_id (o ID do log, ex: "match_123").
    """
    return db.query(match_models.Match).filter(match_models.Match.match_id == match_id).first()

def get_match_by_db_id(db: Session, match_db_id: uuid.UUID):
    """
    Busca uma partida pelo seu ID primário do banco de dados (UUID).
    """
    return db.query(match_models.Match).filter(match_models.Match.id == match_db_id).first()

def get_all_matches(db: Session, page: int, limit: int):
    """
    Busca todas as partidas com paginação.
    """
    # Primeiro, contamos o total de itens sem paginação
    total_items = db.query(match_models.Match).count()

    # Se não houver itens, retornamos uma estrutura vazia
    if total_items == 0:
        return {"total_items": 0, "items": []}
    
    # Prepara a query para buscar os itens da página
    query = db.query(match_models.Match).order_by(match_models.Match.start_time.desc())

    # A limit > 0 implies a paginated request. Otherwise, fetch all records.
    if limit > 0:
        if page < 1:
            page = 1
        # Calcula o "pulo" (offset)
        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()
        return {"total_items": total_items, "items": items}
    
    items = query.all()
    return {"total_items": total_items, "items": items}

# --- LÓGICA DE ESCRITA (POST, PUT, DELETE) ---

def create_match(db: Session, match: match_schemas.MatchCreate):
    """
    1. POST /matches (Single)
    Cria uma única nova partida no banco de dados.
    """
    # Converte o schema Pydantic para um dicionário e o usa para criar o objeto do modelo
    db_match = match_models.Match(**match.dict())
    
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def create_matches_bulk(db: Session, matches: List[match_schemas.MatchCreate]):
    """
    2. POST /matches/bulk (Bulk/Batch)
    Chama a Stored Procedure/Função 'insert_matches_bulk' no banco de dados
    para inserir múltiplos registros de uma vez.
    """
    
    # 1. Converte a lista de objetos Pydantic para uma string JSON
    #    usamos default=str para converter tipos como datetime
    matches_json = json.dumps([m.dict() for m in matches], default=str)
    
    # 2. Prepara a chamada para a função SQL
    #    Usamos :data como um parâmetro seguro (previne SQL Injection)
    sql_query = text("SELECT insert_matches_bulk(:data)")
    
    # 3. Executa a função no banco de dados, passando o JSON
    db.execute(sql_query, {"data": matches_json})
    
    # 4. Finaliza a transação
    db.commit()
    
    # Nota: Esta abordagem "dispare e esqueça" (fire-and-forget) não
    # retorna os IDs gerados pelo banco, pois a SP não os retorna.
    # Retornamos os dados de entrada para confirmar o que foi enviado.
    return matches

def update_match(db: Session, match_db_id: uuid.UUID, match_update: match_schemas.MatchUpdate):
    """
    Atualiza uma partida existente (PUT).
    """
    db_match = get_match_by_db_id(db, match_db_id)
    if not db_match:
        return None

    # Converte o schema Pydantic para um dicionário, excluindo campos não definidos
    update_data = match_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_match, key, value)
        
    db.commit()
    db.refresh(db_match)
    return db_match

def delete_match(db: Session, match_db_id: uuid.UUID):
    """
    Deleta uma partida existente (DELETE).
    """
    db_match = get_match_by_db_id(db, match_db_id)
    if not db_match:
        return None
        
    db.delete(db_match)
    db.commit()
    return db_match