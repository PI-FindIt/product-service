from fastapi import APIRouter


path_prefix = "/microservice"
router = APIRouter(prefix=path_prefix)


@router.get("")
def read_root() -> dict[str, str]:
    return {"message": "Microservice is running"}


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"message": "pong"}
