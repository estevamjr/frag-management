from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid
from app.schemas import player as player_schemas
from app.services import player as player_service
from app.core.database import SessionLocal

# Imports de Segurança
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/players", response_model=player_schemas.PaginatedPlayerResponse)
def read_players(
    page: int = 1,
    limit: int = Query(20, gt=0, le=100),
    match_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = player_service.get_all_players(
        db, page=page, limit=limit, match_id=match_id
    )
    total_pages = (result["total_items"] + limit - 1) // limit if limit > 0 else 1

    return {
        "total_items": result["total_items"],
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
        "items": result["items"],
    }


@router.get("/players/{player_id}", response_model=player_schemas.Player)
def read_player_by_id(
    player_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_player = player_service.get_player_by_id(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="player not found")
    return db_player
