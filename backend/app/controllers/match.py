# backend/app/controllers/match.py
from typing import List
from fastapi import (
    APIRouter, Depends, HTTPException, Query,
    File, UploadFile
)
from sqlalchemy.orm import Session
import tempfile
import os
import shutil
import uuid
from app.schemas import match as match_schemas
from app.services import match as match_service
from app.core.database import SessionLocal
from ..tasks import process_match_log_file_task

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS GET (Paginado) ---
@router.get("/matches", response_model=match_schemas.PaginatedMatchResponse)
def read_matches(
    page: int = 1,
    limit: int = Query(20, gt=0, le=100),
    db: Session = Depends(get_db)
):
    result = match_service.get_all_matches(db, page=page, limit=limit)
    total_pages = (result["total_items"] + limit - 1) // limit if limit > 0 else 1

    return {
        "total_items": result["total_items"],
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
        "items": result["items"]
    }

@router.get("/matches/{match_id}", response_model=match_schemas.Match)
def read_match_by_match_id(match_id: str, db: Session = Depends(get_db)):
    db_match = match_service.get_match_by_id(db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match

# --- ENDPOINT 1: POST /matches (Single) ---
@router.post("/matches", response_model=match_schemas.Match, status_code=201)
def create_new_match(
    match: match_schemas.MatchCreate, 
    db: Session = Depends(get_db)
):
    existing_match = match_service.get_match_by_id(db, match_id=match.match_id)
    if existing_match:
        raise HTTPException(status_code=400, detail="Match ID already registered")
    return match_service.create_match(db=db, match=match)

# --- ENDPOINT 2: POST /matches/bulk (Bulk/Batch) ---
@router.post("/matches/bulk", response_model=List[match_schemas.Match], status_code=201)
def create_new_matches_bulk(
    matches: List[match_schemas.MatchCreate], 
    db: Session = Depends(get_db)
):
    return match_service.create_matches_bulk(db=db, matches=matches)

# --- ENDPOINT 3: POST /matches/upload (Padrão Ouro) ---
@router.post("/matches/upload", response_model=match_schemas.MatchUploadResponse, status_code=202)
def upload_match_log(
    file: UploadFile = File(...),
):
    task_id = str(uuid.uuid4())
    temp_dir = tempfile.gettempdir()
    temp_file_path = os.path.join(temp_dir, f"{task_id}_{file.filename}")    
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()
    
    # Envia a tarefa para o Celery (Redis)
    process_match_log_file_task.delay(temp_file_path, task_id)
    
    return {
        "message": "Arquivo recebido. O processamento foi iniciado em segundo plano.",
        "task_id": task_id
    }

# --- ENDPOINTS PUT E DELETE ---
@router.put("/matches/{match_db_id}", response_model=match_schemas.Match)
def update_existing_match(
    match_db_id: uuid.UUID, 
    match_update: match_schemas.MatchUpdate, 
    db: Session = Depends(get_db)
):
    # VERIFICAÇÃO DE SEGURANÇA: Impede a alteração do match_id
    if match_update.match_id is not None:
        raise HTTPException(status_code=400, detail="Updating 'match_id' is not allowed.")

    db_match = match_service.update_match(db, match_db_id, match_update)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match

@router.delete("/matches/{match_db_id}", response_model=match_schemas.Match)
def delete_existing_match(
    match_db_id: uuid.UUID, 
    db: Session = Depends(get_db)
):
    db_match = match_service.delete_match(db, match_db_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return db_match