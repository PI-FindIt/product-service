from typing import Optional

import strawberry
from pydantic import BaseModel as PydanticBaseModel
from sqlmodel import Field

from protobuf.connections import microservice_template_models
from src.crud.base import CRUDBase
from src.models.base import BaseModel


@strawberry.type
class _BookAttr(PydanticBaseModel):
    title: str
    author: str
    year: int


@strawberry.type
class BookBase(BaseModel[microservice_template_models.BookBase], _BookAttr):
    __grpc_model__ = microservice_template_models.BookBase


@strawberry.type
class Book(BaseModel[microservice_template_models.Book], _BookAttr, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    __grpc_model__ = microservice_template_models.Book


class CrudBook(CRUDBase[Book, BookBase, int]):
    def __init__(self) -> None:
        super().__init__(model=Book)
