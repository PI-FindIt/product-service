import strawberry
from graphql import GraphQLError

from src.crud.product import crud_product, CrudProduct
from src.models.product import Product, ProductBase

crud = CrudProduct()


@strawberry.type
class Query:
    @strawberry.field()
    async def product(self, name: str) -> Product | None:
        obj = await crud_product.get(name)
        if obj is None:
            return None
        return Product(**obj.model_dump())

    @strawberry.field()
    async def products(self, name: str) -> list[Product]:
        objects = await crud_product.find(name)
        return [Product(**obj.model_dump()) for obj in objects]


@strawberry.type
class Mutation:
    @strawberry.mutation()
    async def create_product(self, model: ProductBase) -> Product:
        obj = await crud.create(model.to_pydantic())
        if obj is None:
            raise GraphQLError(
                "ProductModel already exists", extensions={"code": "NOT_FOUND"}
            )
        return Product(**obj.model_dump())

    @strawberry.mutation()
    async def update_product(self, name: str, model: ProductBase) -> Product:
        obj = await crud.update(name, model.to_pydantic())
        if obj is None:
            raise GraphQLError(
                "ProductModel not found", extensions={"code": "NOT_FOUND"}
            )
        return Product(**obj.model_dump())

    @strawberry.mutation()
    async def delete_product(self, name: str) -> bool:
        return await crud.delete(name)
