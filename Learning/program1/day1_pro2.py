from fastapi import FastAPI
import asyncio
import time
import threading

app = FastAPI()

# GET endpoint — used to READ data
@app.get("/tasks")
def get_all_tasks():
    current = threading.current_thread()
    main = threading.main_thread()

    print("Current thread:", current.name)
    print("Current thread ID:", threading.get_ident())
    print("Is main thread?", current == main)
    return [{"id": 1, "title": "Write tests"}]

# POST endpoint — used to CREATE data
# The URL parameter {task_id} is captured automatically
# import time
# @app.get("/tasks/{task_id}")
# def get_task(task_id: int):
    # task_id is automatically converted to int and validated
    # await asyncio.sleep(5)
    # time.sleep(5)
    # return {"id": task_id, "title": "Sample task"}

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    current = threading.current_thread()
    main = threading.main_thread()

    print("Current thread 11:", current.name)
    print("Current thread ID 11:", threading.get_ident())
    print("Is main thread? 11", current == main)
    await asyncio.sleep(5)
    # time.sleep(5)

    return {
        "id": task_id,
        "title": "Sample task",
        "thread_name": current.name,
        "thread_id": threading.get_ident(),
        "is_main_thread": current == main,
    }

# DELETE endpoint
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    return {"deleted": True, "id": task_id}

