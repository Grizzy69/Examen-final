import fastapi  from FastAPI

app = FastAPI()

@app.get("/ping")
def ping():
    return "Pong"