# pip install "fastapi[standard]"
# execute below command with main.py as your file name in terminal
# fastapi dev main.py
# Interactive API docs¶
# Now go to http://127.0.0.1:8000/docs
# go to http://127.0.0.1:8000/redoc
# You can see it directly at: http://127.0.0.1:8000/openapi.json
# https://fastapi.tiangolo.com/tutorial/first-steps/#interactive-api-docs

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]

