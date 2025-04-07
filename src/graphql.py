import strawberry

from graphql import GraphQLError
from src.crud import crud
from src.models import Product, ProductFilter, ProductInput, ProductModel


@strawberry.type
class Query:
    @strawberry.field()
    async def product(self, ean: str) -> Product | None:
        return await crud.get(ean)

    @strawberry.field()
    async def products(self, filters: ProductFilter) -> list[Product]:
        return await crud.get_all(filters)


@strawberry.type
class Mutation:
    @strawberry.mutation()
    async def create_product(self, model: ProductInput) -> Product:
        obj = await crud.create(ProductModel(**strawberry.asdict(model)))
        if obj is None:
            raise GraphQLError(
                "ProductModel already exists", extensions={"code": "NOT_FOUND"}
            )
        return obj

    @strawberry.mutation()
    async def delete_product(self, name: str) -> bool:
        return await crud.delete(name)
