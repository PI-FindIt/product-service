from typing import Optional

import strawberry

from protobuf.connections import (
    microservice_template_stub,
    microservice_template_models,
)
from src.models.book import Book


# boas praticas sao boas e por isso apliquemos
async def get_book(id: int) -> Optional[Book]:
    b = await microservice_template_stub.GetBook(
        microservice_template_models.BookBase(id=id)
    )
    return Book.from_grpc(b)


@strawberry.type
class Query:
    get_book: Book | None = strawberry.field(resolver=get_book)
