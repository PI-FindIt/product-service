import strawberry

from graphql import GraphQLError
from strawberry import Info
from strawberry.utils.str_converters import to_snake_case

from src.crud import crud
from src.models import Product, ProductFilter, ProductInput, ProductModel, ProductOrder


def _get_requested_fields(info: Info) -> set[str]:
    return {
        to_snake_case(selection.name + ("_name" if selection.selections else ""))
        for field in info.selected_fields
        for selection in field.selections
    }


@strawberry.type
class Query:
    @strawberry.field()
    async def product(self, ean: str, info: Info) -> Product | None:
        return await crud.get(ean, _get_requested_fields(info))

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
            _get_requested_fields(info), filters, order_by, limit, offset
        )


@strawberry.type
class Mutation:
    @strawberry.mutation()
    async def create_product(self, model: ProductInput, info: Info) -> Product:
        obj = await crud.create(
            ProductModel(**strawberry.asdict(model)), _get_requested_fields(info)
        )
        if obj is None:
            raise GraphQLError(
                "ProductModel already exists", extensions={"code": "NOT_FOUND"}
            )
        return obj

    @strawberry.mutation()
    async def delete_product(self, name: str) -> bool:
        return await crud.delete(name)
