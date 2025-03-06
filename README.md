# service-template
Template repository to easily create microservices

## How to generate a new microservice
1. Click on the "Use this template" button on the top right of the repository
2. Fill in the repository name and description
3. Click on "Create repository"
4. Clone the repository
5. Create a virtual environment and activate it
6. Install poetry with `pip install poetry`
7. Install the dependencies with `poetry install`
8. Run `make all` to generate code regarding Docker and gRPC
9. Commit & push changes

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
