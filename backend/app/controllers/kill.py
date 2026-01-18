from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid
from app.schemas import kill as kill_schemas
from app.services import kill as kill_service
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


@router.get("/kills", response_model=kill_schemas.PaginatedKillResponse)
def read_kills(
    page: int = 1,
    limit: int = Query(20, gt=0, le=100),
    match_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = kill_service.get_all_kills(db, page=page, limit=limit, match_id=match_id)
    total_pages = (result["total_items"] + limit - 1) // limit if limit > 0 else 1

    return {
        "total_items": result["total_items"],
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
        "items": result["items"],
    }


@router.get("/kills/{kill_id}", response_model=kill_schemas.Kill)
def read_kill_by_id(
    kill_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_kill = kill_service.get_kill_by_id(db, kill_id=kill_id)
    if db_kill is None:
        raise HTTPException(status_code=404, detail="kill not found")
    return db_kill
