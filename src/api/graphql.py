from typing import Callable, Awaitable, Type, TypeVar

import strawberry
from src.models.model import Model, ModelBase

from src.models.base import BaseModel


@strawberry.type
class Query:
    @strawberry.field
    async def get_model(self, id: int) -> Model:
        return ...


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_model(self, model: ModelBase) -> Model:
        return ...
