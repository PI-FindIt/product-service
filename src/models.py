from enum import Enum
from typing import Optional

import strawberry
from sqlalchemy import TEXT, Column
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
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
    energy: float | None = None
    saturated_fat: float | None = None
    fat: float | None = None
    salt: float | None = None
    sugars: float | None = None
    proteins: float | None = None
    carbohydrates: float | None = None


class ProductModel(SQLModel, table=True):
    ean: str = Field(primary_key=True)
    name: str
    generic_name: str
    nutrition: NutritionModel = Field(sa_column=Column(JSONB))
    nutri_score: NutriScore
    ingredients: str
    quantity: str
    unit: str
    keywords: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(TEXT)))
    images: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(TEXT)))
    brand_name: str | None = None
    category_name: str | None = None


fields = set(ProductModel.__annotations__.keys()) - {"id", "nutrition"}


@strawberry.experimental.pydantic.input(model=NutritionModel, all_fields=True)
class NutritionBase: ...


@strawberry.experimental.pydantic.type(model=NutritionModel, all_fields=True)
class Nutrition: ...


@strawberry.experimental.pydantic.input(model=ProductModel, fields=list(fields))
class ProductBase:
    id: strawberry.ID
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
            return None

        return Product(**product_model.model_dump())
