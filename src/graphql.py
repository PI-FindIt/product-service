import strawberry

from graphql import GraphQLError
from src.crud import crud
from src.models import Product, ProductInput, ProductModel


@strawberry.type
class Query:
    @strawberry.field()
    async def product(self, ean: str) -> Product | None:
        obj = await crud.get(ean)
        if obj is None:
            return None
        return Product(**obj.to_dict())

    @strawberry.field()
    async def products(self, name: str) -> list[Product]:
        objects = await crud.find(name)
        return [Product(**obj.to_dict()) for obj in objects]


@strawberry.type
class Mutation:
    @strawberry.mutation()
    async def create_product(self, model: ProductInput) -> Product:
        obj = await crud.create(ProductModel(**strawberry.asdict(model)))
        if obj is None:
            raise GraphQLError(
                "ProductModel already exists", extensions={"code": "NOT_FOUND"}
            )
        return Product(**obj.to_dict())

    @strawberry.mutation()
    async def delete_product(self, name: str) -> bool:
        return await crud.delete(name)
