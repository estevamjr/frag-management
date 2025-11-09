# backend/app/models/match.py

import uuid
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from sqlalchemy.sql import text

class Match(Base):
    __tablename__ = "matches"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    match_id = Column(String, unique=True, index=True, nullable=False)
    start_time = Column(TIMESTAMP(timezone=True))
    end_time = Column(TIMESTAMP(timezone=True))
    players = relationship("Player", back_populates="match")
    kills = relationship("Kill", back_populates="match")
    bonuses = relationship("Bonus", back_populates="match")

class Player(Base):
    __tablename__ = "players"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_name = Column(String, nullable=False)
    frags = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    match = relationship("Match", back_populates="players")
    bonuses = relationship("Bonus", back_populates="player")

class Bonus(Base):
    __tablename__ = "bonuses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bonus_type = Column(String, nullable=False)
    bonus_description = Column(String)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    player = relationship("Player", back_populates="bonuses")
    match = relationship("Match", back_populates="bonuses")

class Kill(Base):
    __tablename__ = "kills"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    killer_name = Column(String, nullable=False)
    victim_name = Column(String, nullable=False)
    weapon = Column(String, nullable=False)
    kill_time = Column(TIMESTAMP(timezone=True))
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    match = relationship("Match", back_populates="kills")

class GlobalPlayerStats(Base):
    __tablename__ = "global_player_stats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_name = Column(String, unique=True, nullable=False, index=True)
    total_frags = Column(Integer, default=0)
    total_deaths = Column(Integer, default=0)
    awards_won = Column(Integer, default=0)