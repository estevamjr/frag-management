# backend/main.py

from fastapi import FastAPI
from app.controllers import match as match_controller
from app.core.database import engine
from app.controllers import task as task_controller
from app.controllers import player as player_controller
from app.controllers import kill as kill_controller
from app.models import match as match_models

# Cria as tabelas no banco de dados (se não existirem)
match_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Frag Management API")

# Inclui as rotas do controller de partidas
app.include_router(match_controller.router, prefix="/api/v1", tags=["Matches"])

app.include_router(task_controller.router, prefix="/api/v1", tags=["Taks"])

app.include_router(player_controller.router, prefix="/api/v1", tags=["Player"])

app.include_router(kill_controller.router, prefix="/api/v1", tags=["Kill"])

@app.get("/")
def read_root():
    return {"Status": "API is running"}