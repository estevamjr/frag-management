from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from typing import List
import uuid
import json

from app.models import match as match_models
from app.schemas import match as match_schemas


def get_match_by_id(db: Session, match_id: str):
    return (
        db.query(match_models.Match)
        .filter(match_models.Match.match_id == match_id)
        .first()
    )


def get_match_by_db_id(db: Session, match_db_id: uuid.UUID):
    return (
        db.query(match_models.Match)
        .filter(match_models.Match.id == match_db_id)
        .first()
    )


def get_all_matches(db: Session, page: int, limit: int):
    total_items = db.query(match_models.Match).count()

    if total_items == 0:
        return {"total_items": 0, "items": []}

    query = db.query(match_models.Match).order_by(match_models.Match.start_time.desc())

    if limit > 0:
        if page < 1:
            page = 1
        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()
        return {"total_items": total_items, "items": items}

    items = query.all()
    return {"total_items": total_items, "items": items}


def create_match(db: Session, match: match_schemas.MatchCreate, user_id: int):
    # Injeta user_id no modelo
    db_match = match_models.Match(**match.dict(), user_id=user_id)

    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


def create_matches_bulk(
    db: Session, matches: List[match_schemas.MatchCreate], user_id: int
):
    matches_data = []
    # Injeta user_id em cada item da lista
    for m in matches:
        match_dict = m.dict()
        match_dict["user_id"] = user_id
        matches_data.append(match_dict)

    matches_json = json.dumps(matches_data, default=str)

    sql_query = text("SELECT insert_matches_bulk(:data)")

    db.execute(sql_query, {"data": matches_json})
    db.commit()

    return matches


def update_match(
    db: Session, match_db_id: uuid.UUID, match_update: match_schemas.MatchUpdate
):
    db_match = get_match_by_db_id(db, match_db_id)
    if not db_match:
        return None

    update_data = match_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_match, key, value)

    db.commit()
    db.refresh(db_match)
    return db_match


def delete_match(db: Session, match_db_id: uuid.UUID):
    db_match = get_match_by_db_id(db, match_db_id)
    if not db_match:
        return None

    db.delete(db_match)
    db.commit()
    return db_match
