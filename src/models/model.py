from typing import Optional

import strawberry
from pydantic import BaseModel as PydanticBaseModel
from sqlmodel import Field

from src.models.base import BaseModel
from enum import Enum


class NutriScore(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT-APPLICABLE"


class Nutrition:
    saturated_fat: str
    fat: str
    salt: str
    sugars: str


# Category
@strawberry.type
class _CategoryAttr(PydanticBaseModel):
    name: str


@strawberry.type
class CategoryBase(BaseModel, _CategoryAttr): ...


@strawberry.type
class Category(BaseModel, _CategoryAttr, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    parents: list["Category"]


# Product
@strawberry.type
class _ProductAttr(PydanticBaseModel):
    ean: str
    name: str
    generic_name: str
    nutrition: Nutrition
    nutri_score: NutriScore
    ingredients: str
    quantity: str
    unit: str
    keywords: list[str]
    brands: list[int]  # fk from another service
    supermakets: list[int]  # fk from another service
    images: dict[str, str]
    nutriments: dict[str, str]


@strawberry.input
class ProductBase(BaseModel, _ProductAttr): ...


@strawberry.type
class Product(BaseModel, _ProductAttr, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
