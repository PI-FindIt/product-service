from typing import Callable, Awaitable, Type, TypeVar

import strawberry
from google.protobuf.message import Message
from grpc.aio import AioRpcError

from protobuf.connections import (
    microservice_template_stub,
    microservice_template_models,
)
from src.models.base import BaseModel
from src.models.book import Book

ModelType = TypeVar("ModelType", bound=BaseModel)  # type: ignore


async def get_entity(
    stub_method: Callable[[Message], Awaitable[Message]],
    response_model_cls: Type[ModelType],
    *request_message: Message,
) -> ModelType | None:
    try:
        response = await stub_method(*request_message)
        return response_model_cls.from_grpc(response)
    except AioRpcError as e:
        raise Exception(e.details())


async def get_book(id: int) -> Book | None:
    return await get_entity(
        microservice_template_stub.GetBook,
        Book,
        microservice_template_models.BookId(id=id),
    )


@strawberry.type
class Query:
    get_book: Book | None = strawberry.field(resolver=get_book)
