import dataclasses
from enum import Enum
from typing import Any, Optional

import strawberry
from sqlalchemy import TEXT, Column
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlmodel import Field, SQLModel


@strawberry.federation.type(keys=["name"], extend=True)
class Category:
    name: str

    @strawberry.field()
    async def products(self) -> list["Product"]:
        from src.crud import crud

        return [
            Product.from_pydantic(obj) for obj in await crud.get_by_category(self.name)
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


fields = set(ProductModel.__annotations__.keys()) - {"ean", "nutrition"}


@strawberry.experimental.pydantic.input(model=NutritionModel, all_fields=True)
class NutritionBase: ...


@strawberry.experimental.pydantic.type(model=NutritionModel, all_fields=True)
class Nutrition: ...


@strawberry.experimental.pydantic.input(model=ProductModel, fields=list(fields))
class ProductBase:
    ean: strawberry.ID
    nutrition: NutritionBase

    def to_pydantic(self) -> ProductModel:
        data = dataclasses.asdict(self)  # type: ignore
        del data["nutrition"]
        return ProductModel(nutrition=self.nutrition.to_pydantic(), **data)


@strawberry.federation.type(keys=["ean"])
class Product:
    ean: strawberry.ID
    name: str
    generic_name: str
    nutrition: Nutrition
    nutri_score: NutriScore
    ingredients: str
    quantity: str
    unit: str
    keywords: list[str]
    images: list[str]
    brand_name: str | None = None
    category_name: str | None = None

    @strawberry.field()
    def category(self) -> Category:
        return Category(name=self.category_name)

    @staticmethod
    def from_pydantic(
        instance: ProductModel, extra: dict[str, Any] | None = None
    ) -> "Product":
        if extra is None:
            extra = {}
        data = instance.model_dump()
        data["nutrition"] = Nutrition.from_pydantic(instance.nutrition)
        return Product(**data, **extra)

    @classmethod
    async def resolve_reference(cls, ean: strawberry.ID) -> Optional["Product"]:
        from src.crud import crud

        product_model = await crud.get(ean)
        if product_model is None:
            return None

        return Product(**product_model.model_dump())
