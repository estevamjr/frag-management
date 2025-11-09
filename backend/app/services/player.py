# backend/app/services/match.py

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
import uuid
from typing import Optional

from app.models import match as match_models
from app.schemas import player as player_schemas

def get_player_by_id(db: Session, player_id: uuid.UUID):
    """
    Busca um jogador pelo seu ID primário do banco de dados (UUID).
    """
    return db.query(match_models.Player).filter(match_models.Player.id == player_id).first()

def get_player_by_db_id(db: Session, match_db_id: uuid.UUID):
    """
    Busca um jogador pelo seu ID primário do banco de dados (UUID).
    """
    return db.query(match_models.Player).filter(match_models.Player.id == match_db_id).first()

def get_all_players(db: Session, page: int, limit: int, match_id: Optional[uuid.UUID] = None):
    """
    Busca todos os jogadores com paginação, opcionalmente filtrando por partida.
    """
    # Prepara a query base para buscar os jogadores
    query = db.query(match_models.Player).options(joinedload(match_models.Player.bonuses))

    # Adiciona o filtro por match_id, se fornecido
    if match_id:
        query = query.filter(match_models.Player.match_id == match_id)

    # Primeiro, contamos o total de itens sem paginação
    total_items = query.count()

    # Se não houver itens, retornamos uma estrutura vazia
    if total_items == 0:
        return {"total_items": 0, "items": []}
    
    # Ordena os resultados
    query = query.order_by(match_models.Player.deaths.desc())

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