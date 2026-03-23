from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
app = FastAPI()

# This model defines what a client MUST send when creating a task
class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Optional description")
    status: str = Field("open", description="Task status: open, in_progress,  done")
    # Pydantic validates automatically:
    # - title is required (... means required in Field)
    # - title cannot be empty string (min_length=1)
    # - status defaults to "open" if not provided

# This model defines what the API sends BACK to the client
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    # This config tells Pydantic how to read data
    # "from_attributes = True" allows reading from ORM objects (not just
    model_config = {"from_attributes": True}

# In-memory storage (no DB yet — we add that on Day 3/4)
tasks_db = []
task_counter = 0

@app.post("/tasks", response_model=TaskResponse)
def create_task(task_data: TaskCreateRequest):
    """
    response_model=TaskResponse tells FastAPI:
    1. Validate the response data against TaskResponse
    2. Strip any extra fields not in TaskResponse (security)
    3. Show TaskResponse shape in Swagger docs
    """
    global task_counter
    task_counter += 1
    new_task = {
    "id": task_counter,
    "title": task_data.title,
    "description": task_data.description,
    "status": task_data.status,
    "created_at": datetime.now(),
    }
    tasks_db.append(new_task)
    return new_task

@app.get("/tasks", response_model=list[TaskResponse])
def get_all_tasks():
    return tasks_db