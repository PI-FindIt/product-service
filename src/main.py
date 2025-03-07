import threading

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.api.routes import router
from src.api.service import serve_grpc

grpc_thread = threading.Thread(target=serve_grpc)
grpc_thread.start()


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return f"Hello World!"


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)


app = FastAPI(title="Microservice Template")
app.include_router(router)
app.include_router(graphql_app, prefix="/graphql")
