from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


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


class ProductBase(SQLModel):
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


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
