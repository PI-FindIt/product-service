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
from src.models.book import CrudBook, BookBase


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await init_postgres_db()
    asyncio.create_task(serve_grpc())
    yield


async def inserter() -> None:
    crud_book = CrudBook()
    # insert 4 books
    print(BookBase(title="The Great Gatsby", author="F. Scott Fitzgerald", year=1925))

    await crud_book.create(
        BookBase(title="The Great Gatsby", author="F. Scott Fitzgerald", year=1925)
    )
    await crud_book.create(
        BookBase(title="To Kill a Mockingbird", author="Harper Lee", year=1960)
    )
    await crud_book.create(BookBase(title="1984", author="George Orwell", year=1949))
    await crud_book.create(
        BookBase(title="The Catcher in the Rye", author="J.D. Salinger", year=1951)
    )

    print("FINITOOO")


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
# threading.Thread(target=lambda: asyncio.run(inserter())).start()

app = FastAPI(title="Microservice Template", lifespan=lifespan)
app.include_router(router)

app.include_router(graphql_app, prefix="/microservice/graphql")
