from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}

@app.get("/get_caption")
def hello_world():
    return {"message": "Hello, World!"}


