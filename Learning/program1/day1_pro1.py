from fastapi import FastAPI

# FastAPI() creates the application instance.
# This is similar to how you instantiate Odoo modules.

app = FastAPI(title="Task Manager API", version="1.0.0")

@app.get("/health")
def health_check():
	"""
	The simplest possible endpoint.
	Returns a JSON response: {"status": "ok"}
	"""
	return {"status": "ok"}
