from fastapi import FastAPI
from src.api.routes import router
from src.grpc_service.service import serve
import threading
app = FastAPI(title="Microservice Template")

app.include_router(router)


def run_grpc():
    try:
        serve()
    except ModuleNotFoundError:
        print("gRPC proto code isnt generated yet")

grpc_thread = threading.Thread(target=run_grpc)
grpc_thread.start()

@app.get("/")
def read_root():
    return {"message": "Microservice is running"}