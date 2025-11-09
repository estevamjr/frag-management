# backend/app/schemas/match.py

from pydantic import BaseModel
from typing import List, Optional
import uuid

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

# --- SCHEMA PARA RESPOSTAS PAGINADAS ---
class PaginatedPlayerResponse(BaseModel):
    total_items: int
    total_pages: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
    items: List[Player]