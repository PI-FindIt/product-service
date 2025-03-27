import strawberry.experimental.pydantic
from pydantic import AnyHttpUrl
from sqlmodel import SQLModel, Field


class BrandBaseModel(SQLModel):
    name: str
    logo: AnyHttpUrl | None = None


@strawberry.experimental.pydantic.input(model=BrandBaseModel, all_fields=True)
class BrandBase: ...


class BrandModel(BrandBaseModel, table=True):
    id: int | None = Field(default=None, primary_key=True)


@strawberry.experimental.pydantic.type(model=BrandModel, all_fields=True)
class Brand:
    id: int  # ID is never None here
