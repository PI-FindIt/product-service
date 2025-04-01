from enum import Enum
from typing import Optional

import strawberry
from sqlmodel import Field, SQLModel


@strawberry.federation.type(keys=["name"], extend=True)
class Category:
    name: str = strawberry.federation.field(external=True)

    @strawberry.field()
    async def products(self) -> list["Product"]:
        from src.crud import crud

        return [
            Product(**obj.model_dump()) for obj in await crud.get_by_category(self.name)
        ]


class NutriScore(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT-APPLICABLE"


class NutritionModel(SQLModel):
    saturated_fat: str
    fat: str
    salt: str
    sugars: str


class ProductModel(SQLModel):
    ean: strawberry.ID = Field(primary_key=True)
    name: str
    generic_name: str
    nutrition: NutritionModel
    nutri_score: NutriScore
    ingredients: str
    quantity: str
    unit: str
    keywords: list[str]
    images: tuple[str, ...]
    brand_id: int
    category_name: str


fields = set(ProductModel.__annotations__.keys()) - {"nutrition"}


@strawberry.experimental.pydantic.input(model=NutritionModel, all_fields=True)
class NutritionBase: ...


@strawberry.experimental.pydantic.type(model=NutritionModel, all_fields=True)
class Nutrition: ...


@strawberry.experimental.pydantic.input(model=ProductModel, fields=list(fields))
class ProductBase:
    nutrition: NutritionBase


@strawberry.federation.type(keys=["ean"])
@strawberry.experimental.pydantic.type(model=ProductModel, fields=list(fields))
class Product:
    nutrition: Nutrition

    @strawberry.field()
    def category(self: ProductModel) -> Category:
        return Category(name=self.category_name)

    @classmethod
    async def resolve_reference(cls, ean: strawberry.ID) -> Optional["Product"]:
        from src.crud import crud

        product_model = await crud.get(ean)
        if product_model is None:
            print("a")
            return None

        return Product(**product_model.model_dump())
