import dataclasses
from typing import Optional, Any

import strawberry
from sqlmodel import Field, SQLModel

from protobuf.connections import microservice_template_models
from src.crud.base import CRUDBase
from src.models.base import BaseModel


# @dataclasses.dat  aclass
class _BookAttr(SQLModel):
    title: str
    author: str
    year: int


class BookBase(BaseModel[microservice_template_models.BookBase], _BookAttr):
    __grpc_model__ = microservice_template_models.BookBase


@strawberry.type
class Book(BaseModel[microservice_template_models.Book], _BookAttr, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    __grpc_model__ = microservice_template_models.Book


class CrudBook(CRUDBase[Book, BookBase, int]):
    def __init__(self) -> None:
        super().__init__(model=Book)
