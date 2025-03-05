# service-template
Template repository to easily create microservices

## Commands used to create this template

```bash
poetry new microservice-template
cd microservice-template

poetry add fastapi grpcio grpcio-tools sqlmodel alembic sqlalchemy databases pymongo odmantic
poetry add --group dev uvicorn pytest pytest-asyncio mypy black isort 

#É mandatorio correr o comando abaixo para poder usar o grpc  
python -m grpc_tools.protoc -I=src/grpc_service/protos --python_out=src/grpc_service --grpc_python_out=src/grpc_service src/grpc_service/protos/service.proto

# Para SQL
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head


```


## How to use
