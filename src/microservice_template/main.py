from fastapi import FastAPI
app = FastAPI(title="Microservice Template")

@app.get("/")
def read_root():
    return {"message": "Microservice is running"}
