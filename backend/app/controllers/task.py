from fastapi import APIRouter, Depends
from celery.result import AsyncResult
from ..tasks import celery_app
from pydantic import BaseModel
from typing import Optional, Any

# Imports de Segurança
from app.services.auth import get_current_user
from app.models.user import User

router = APIRouter()


class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None


@router.get("/tasks/status/{task_id}", response_model=TaskStatus)
def get_task_status(task_id: str, current_user: User = Depends(get_current_user)):
    task_result = AsyncResult(task_id, app=celery_app)

    status = task_result.state
    result = task_result.result

    if status == "FAILURE":
        result = str(result)
        return TaskStatus(task_id=task_id, status=status, result=result)

    if status == "PENDING" or status == "RECEIVED":
        return TaskStatus(task_id=task_id, status=status)

    return TaskStatus(task_id=task_id, status=status, result=result)
