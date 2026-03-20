from fastapi import FastAPI
app = FastAPI()

# GET endpoint — used to READ data
@app.get("/tasks")
def get_all_tasks():
	return [{"id": 1, "title": "Write tests"}]

# POST endpoint — used to CREATE data
# The URL parameter {task_id} is captured automatically
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
	# task_id is automatically converted to int and validated
	return {"id": task_id, "title": "Sample task"}

# DELETE endpoint
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
	return {"deleted": True, "id": task_id}
