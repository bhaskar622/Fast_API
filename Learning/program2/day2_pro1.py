# uvicorn Learning.program2.day2_pro1:app --reload

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from uuid import uuid4


app = FastAPI(
    title="Task API",
    description="Simple in-memory Task API using FastAPI",
    version="1.0.0"
)


# -----------------------------
# Pydantic Models
# -----------------------------
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(default=None, max_length=1000, description="Task description")
    completed: bool = Field(default=False, description="Task completion status")


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    completed: bool
    created_at: datetime


# -----------------------------
# In-memory storage
# -----------------------------
tasks: List[TaskResponse] = []


# -----------------------------
# Routes
# -----------------------------
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Task API is running"
    }


@app.get("/tasks", response_model=List[TaskResponse])
def get_all_tasks():
    return tasks


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    new_task = TaskResponse(
        id=str(uuid4()),
        title=task.title,
        description=task.description,
        completed=task.completed,
        created_at=datetime.utcnow()
    )
    tasks.append(new_task)
    return new_task


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with id '{task_id}' not found"
    )


@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            deleted_task = tasks.pop(index)
            return {
                "message": "Task deleted successfully",
                "deleted_task": deleted_task
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with id '{task_id}' not found"
    )