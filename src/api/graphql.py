import strawberry
from typing import Optional, Type, Any, Coroutine, TypeVar

from strawberry.experimental.pydantic.conversion_types import StrawberryTypeFromPydantic

from src.models.book import Book as Book, CrudBook, Book
from protobuf.connections import (
    microservice_template_stub,
    microservice_template_models,
)


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


async def get_book2(id: int) -> Optional[Book]:
    crud = CrudBook()
    b = await crud.get(id=id)
    return b


@strawberry.type
class Query:

    get_book: Book | None = strawberry.field(resolver=get_book)

    get_book_book: Book | None = strawberry.field(resolver=get_book2)
