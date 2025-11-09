# backend/app/controllers/player.py
from fastapi import (
    APIRouter, Depends, HTTPException, Query
)
from sqlalchemy.orm import Session
import uuid
from app.schemas import kill as kill_schemas
from app.services import kill as kill_service
from app.core.database import SessionLocal
# from ..tasks import process_kill_log_file_task

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS GET (Paginado) ---
@router.get("/kills", response_model=kill_schemas.PaginatedKillResponse)
def read_kills(
    page: int = 1,
    limit: int = Query(20, gt=0, le=100),
    match_id: uuid.UUID | None = None, # Filtro para buscar kills de uma partida específica
    db: Session = Depends(get_db)
):
    # Corrigido: Passando o parâmetro correto (match_id) para o serviço
    result = kill_service.get_all_kills(db, page=page, limit=limit, match_id=match_id)
    total_pages = (result["total_items"] + limit - 1) // limit if limit > 0 else 1

    return {
        "total_items": result["total_items"],
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
        "items": result["items"]
    }

@router.get("/kills/{kill_id}", response_model=kill_schemas.Kill, summary="Get a specific kill by its database UUID")
def read_kill_by_id(kill_id: uuid.UUID, db: Session = Depends(get_db)):
    # Corrigido: Usando 'kill_id' para evitar conflito com a função 'id' do Python
    db_kill = kill_service.get_kill_by_id(db, kill_id=kill_id)
    if db_kill is None:
        raise HTTPException(status_code=404, detail="kill not found")
    return db_kill