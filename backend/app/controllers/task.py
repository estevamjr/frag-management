from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from ..tasks import celery_app # Importa a instância do Celery que você criou em tasks.py
from pydantic import BaseModel
from typing import Optional, Any

router = APIRouter()

# Schema de resposta para o status da tarefa
class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None

@router.get("/tasks/status/{task_id}", response_model=TaskStatus)
def get_task_status(task_id: str):
    """
    Verifica o status de uma tarefa do Celery (processamento de log)
    pelo seu ID.
    """
    # Usa o AsyncResult para buscar o estado da tarefa no backend (Redis)
    task_result = AsyncResult(task_id, app=celery_app)

    status = task_result.state
    result = task_result.result
    
    # Se a tarefa falhou, queremos retornar o erro como uma string
    if status == "FAILURE":
        result = str(result) # Converte a exceção/erro em string
        return TaskStatus(task_id=task_id, status=status, result=result)

    # Se a tarefa ainda não está pronta (PENDING) ou foi recebida (RECEIVED)
    if status == "PENDING" or status == "RECEIVED":
        return TaskStatus(task_id=task_id, status=status)

    # Se chegou aqui, o status é "SUCCESS"
    return TaskStatus(task_id=task_id, status=status, result=result)