from fastapi import FastAPI, Depends, Header, HTTPException
app = FastAPI()

# A dependency is just a function that returns something useful
def get_request_language(accept_language: str = Header(default="en")) -> str:
	"""
	This function reads the Accept-Language header from every request.
	FastAPI calls this automatically when a route declares it as a depend
	"""
	return accept_language.split(",")[0]

# e.g., "en-US,en" → "en-US"
def verify_api_key(x_api_key: str = Header(...)) -> str:
	"""
	A security dependency — checks for a valid API key header.
	Raises HTTPException if missing or wrong.
	"""
	if x_api_key != "secret-key-123":
		raise HTTPException(status_code=401, detail="Invalid API key")
	return x_api_key

@app.get("/tasks")
def get_tasks(language: str = Depends(get_request_language), api_key: str = Depends(verify_api_key)):
	"""
	FastAPI automatically:
	1. Calls get_request_language() and passes its result as `language`
	2. Calls verify_api_key() and passes its result as `api_key`
	3. If either dependency raises an exception, the route never runs
	"""
	return {"language": language, "tasks": []}
