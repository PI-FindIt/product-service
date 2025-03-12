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
    print(b)
    print(type(b))
    a = Book.from_grpc(b)
    print(type(a))
    return a


@strawberry.type
class Query:
    get_book: Book | None = strawberry.field(resolver=get_book)
