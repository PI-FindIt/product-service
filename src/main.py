from fastapi import FastAPI
from src.api.routes import router
from src.api.service import serve_grpc
import threading

grpc_thread = threading.Thread(target=serve_grpc)
grpc_thread.start()

app = FastAPI(title="Microservice Template")
app.include_router(router)
