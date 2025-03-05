from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Microservice Template")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Microservice is running"}
