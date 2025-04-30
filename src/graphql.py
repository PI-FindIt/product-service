import strawberry

from graphql import GraphQLError
from strawberry import Info

from src.crud import crud
from src.models import Product, ProductFilter, ProductInput, ProductModel, ProductOrder
from src.utils import get_requested_fields


@strawberry.type
class Query:
    @strawberry.field()
    async def product(self, ean: str, info: Info) -> Product | None:
        return await crud.get(ean, get_requested_fields(info))

    @strawberry.field()
    async def products(
        self,
        info: Info,
        filters: ProductFilter | None = None,
        order_by: ProductOrder | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Product]:
        return await crud.get_all(
            get_requested_fields(info), filters, order_by, limit, offset
        )


@strawberry.type
class Mutation:
    @strawberry.mutation()
    async def create_product(self, model: ProductInput, info: Info) -> Product:
        obj = await crud.create(
            ProductModel(**strawberry.asdict(model)), get_requested_fields(info)
        )
        if obj is None:
            raise GraphQLError(
                "ProductModel already exists", extensions={"code": "NOT_FOUND"}
            )
        return obj

    @strawberry.mutation()
    async def delete_product(self, name: str) -> bool:
        return await crud.delete(name)
