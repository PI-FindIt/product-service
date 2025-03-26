import strawberry
from src.models.base import BaseModel

from src.models.product import Model, ModelBase


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
