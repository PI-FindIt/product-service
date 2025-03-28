from typing import TYPE_CHECKING

import strawberry.experimental.pydantic
from pydantic import AnyHttpUrl
from sqlmodel import SQLModel, Field, Relationship, AutoString

if TYPE_CHECKING:
    from src.models.product import ProductModel


class BrandBaseModel(SQLModel):
    name: str
    logo: AnyHttpUrl | None = Field(default=None, sa_type=AutoString)


@strawberry.experimental.pydantic.input(model=BrandBaseModel, all_fields=True)
class BrandBase: ...


class BrandModel(BrandBaseModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    products: list["ProductModel"] = Relationship(back_populates="brand")


@strawberry.experimental.pydantic.type(model=BrandModel, all_fields=True)
class Brand:
    id: int  # ID is never None here
