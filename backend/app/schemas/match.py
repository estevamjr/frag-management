# backend/app/schemas/match.py

from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

class BonusBase(BaseModel):
    bonus_type: str
    bonus_description: Optional[str] = None

class Bonus(BonusBase):
    id: uuid.UUID
    class Config:
        from_attributes = True

class PlayerBase(BaseModel):
    player_name: str
    frags: int = 0
    deaths: int = 0

class Player(PlayerBase):
    id: uuid.UUID
    bonuses: List[Bonus] = []
    class Config:
        from_attributes = True

class KillBase(BaseModel):
    killer_name: str
    victim_name: str
    weapon: str
    kill_time: Optional[datetime] = None

class Kill(KillBase):
    id: uuid.UUID
    class Config:
        from_attributes = True

class MatchBase(BaseModel):
    match_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class Match(MatchBase):
    id: uuid.UUID
    players: List[Player] = []
    kills: List[Kill] = []
    class Config:
        from_attributes = True

# --- SCHEMAS DE ESCRITA (PARA POST/PUT) ---
class MatchCreate(MatchBase):
    pass

class MatchUpdate(BaseModel):
    match_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

# --- SCHEMA PARA UPLOAD ASSÍNCRONO (Best Pract) ---
class MatchUploadResponse(BaseModel):
    message: str
    task_id: str        

# --- SCHEMA PARA RESPOSTAS PAGINADAS ---
class PaginatedMatchResponse(BaseModel):
    total_items: int
    total_pages: int
    page: int
    limit: int
    items: List[Match]