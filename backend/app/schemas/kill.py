# backend/app/schemas/match.py

from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

class KillBase(BaseModel):
    killer_name: str
    victim_name: str
    weapon: str
    kill_time: Optional[datetime] = None

class Kill(KillBase):
    id: uuid.UUID
    class Config:
        from_attributes = True

# --- SCHEMA PARA RESPOSTAS PAGINADAS ---
class PaginatedKillResponse(BaseModel):
    total_items: int
    total_pages: int
    page: int
    limit: int
    items: List[Kill]