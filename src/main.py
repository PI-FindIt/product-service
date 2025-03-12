import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.api.graphql import Query
from src.api.routes import router
from src.api.service import serve_grpc
from src.config.session import init_postgres_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await init_postgres_db()
    asyncio.create_task(serve_grpc())
    yield


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Microservice Template", lifespan=lifespan)
app.include_router(router)

app.include_router(graphql_app, prefix="/microservice/graphql")
