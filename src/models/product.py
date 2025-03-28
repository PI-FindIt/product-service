from enum import Enum
from typing import Optional

import strawberry
from sqlmodel import Field, SQLModel


@strawberry.federation.type(keys=["name"], extend=True)
class Category:
    name: str = strawberry.federation.field(external=True)

    @strawberry.field()
    async def products(self) -> list["Product"]:
        from src.crud.product import crud_product

        return [
            Product(**obj.model_dump())
            for obj in await crud_product.get_by_category(self.name)
        ]


class NutriScore(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT-APPLICABLE"


class Nutrition(SQLModel):
    saturated_fat: str
    fat: str
    salt: str
    sugars: str


class ProductModel(SQLModel):
    ean: strawberry.ID = Field(primary_key=True)
    name: str
    generic_name: str
    # nutrition: Nutrition
    nutri_score: NutriScore
    ingredients: str
    quantity: str
    unit: str
    keywords: list[str]
    images: tuple[str, ...]
    brand_id: int = Field(foreign_key="brandmodel.id")
    category_name: str


@strawberry.experimental.pydantic.input(model=ProductModel, all_fields=True)
class ProductBase: ...


@strawberry.federation.type(keys=["ean"])
@strawberry.experimental.pydantic.type(model=ProductModel, all_fields=True)
class Product:
    @strawberry.field()
    def category(self: ProductModel) -> Category:
        return Category(name=self.category_name)

    @classmethod
    async def resolve_reference(cls, ean: strawberry.ID) -> Optional["Product"]:
        from src.crud.product import crud_product

        product_model = await crud_product.get(ean)
        if product_model is None:
            print("a")
            return None

        return Product(**product_model.model_dump())
