import json
from enum import Enum
from typing import Any, Optional

import strawberry
from sqlalchemy import ARRAY, JSON, TEXT, Dialect, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from strawberry.federation.schema_directives import Key, Shareable
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyMapper

strawberry_sqlalchemy_mapper = StrawberrySQLAlchemyMapper()
_BaSe = declarative_base()


class Operator(Enum):
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    LIKE = "like"
    ILIKE = "ilike"
    IN = "in"
    NOT_IN = "not in"
    IS = "is"
    IS_NOT = "is not"
    CONTAINS = "contains"
    NOT_CONTAINS = "not contains"
    ANY = "any"
    ALL = "all"
    LIMIT = "limit"
    OFFSET = "offset"


class Base(_BaSe):
    __abstract__ = True

    def to_dict(self) -> dict[str, Any]:
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


@strawberry.federation.type(keys=["name"], extend=True)
class Category:
    name: str

    @strawberry.field()
    async def products(self) -> list["Product"]:
        from src.crud import crud

        return [
            Product(**obj.to_dict())
            for obj in await crud.get_all(
                ProductFilter(category_name=Filter(value=self.name, op=Operator.EQ))
            )
        ]


@strawberry.federation.type(keys=["name"], extend=True)
class Brand:
    name: str

    @strawberry.field()
    async def products(self) -> list["Product"]:
        from src.crud import crud

        return [
            Product(**obj.to_dict())
            for obj in await crud.get_all(
                ProductFilter(brand_name=Filter(value=self.name, op=Operator.EQ))
            )
        ]


@strawberry.enum
class NutriScore(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT-APPLICABLE"


@strawberry.type()
class Nutrition:
    energy: float | None = None
    saturated_fat: float | None = None
    fat: float | None = None
    salt: float | None = None
    sugars: float | None = None
    proteins: float | None = None
    carbohydrates: float | None = None


class NutritionJSON(TypeDecorator):  # type: ignore
    impl = JSON

    def process_bind_param(
        self, value: Nutrition | None, dialect: Dialect
    ) -> str | None:
        if value is not None:
            return json.dumps(strawberry.asdict(value))
        return None

    def process_result_value(
        self, value: str | None, dialect: Dialect
    ) -> Nutrition | None:
        if value is not None:
            data = json.loads(value)
            return Nutrition(**data)
        return None


class ProductModel(Base):
    __tablename__ = "productmodel"
    ean: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    name_en: Mapped[str]
    generic_name: Mapped[str]
    generic_name_en: Mapped[str]
    nutrition: Mapped[Nutrition] = mapped_column(JSON)
    nutri_score: Mapped[NutriScore]
    ingredients: Mapped[str]
    quantity: Mapped[str]
    unit: Mapped[str]
    keywords: Mapped[list[str]] = mapped_column(ARRAY(TEXT))
    images: Mapped[list[str]] = mapped_column(ARRAY(TEXT))
    blurhash: Mapped[str | None] = mapped_column(default=None)
    brand_name: Mapped[str | None] = mapped_column(default=None)
    category_name: Mapped[str | None] = mapped_column(default=None)


@strawberry.input()
@strawberry_sqlalchemy_mapper.type(ProductModel)
class ProductInput: ...


@strawberry_sqlalchemy_mapper.type(
    ProductModel, use_federation=True, directives=[Key(fields="ean"), Shareable()]
)
class Product:
    @strawberry.field()
    def category(self) -> Category:
        return Category(name=self.category_name)

    @strawberry.field()
    def brand(self) -> Brand:
        return Brand(name=self.brand_name)

    @classmethod
    async def resolve_reference(cls, ean: strawberry.ID) -> Optional["Product"]:
        from src.crud import crud

        product_model = await crud.get(ean)
        if product_model is None:
            return None

        return Product(**product_model.to_dict())


@strawberry.input()
class Filter[T]:
    value: T
    op: Operator


@strawberry.input()
class ProductFilter:
    and_: Optional[list["ProductFilter"]] = strawberry.field(default=None, name="and")
    or_: Optional[list["ProductFilter"]] = strawberry.field(default=None, name="or")
    ean: Optional[Filter[str]] = None
    name: Optional[Filter[str]] = None
    name_en: Optional[Filter[str]] = None
    generic_name: Optional[Filter[str]] = None
    generic_name_en: Optional[Filter[str]] = None
    nutri_score: Optional[Filter[NutriScore]] = None
    ingredients: Optional[Filter[str]] = None
    quantity: Optional[Filter[str]] = None
    unit: Optional[Filter[str]] = None
    keywords: Optional[Filter[list[str]]] = None
    images: Optional[Filter[list[str]]] = None
    brand_name: Optional[Filter[str]] = None
    category_name: Optional[Filter[str]] = None


class Order(Enum):
    ASC = "asc"
    DESC = "desc"


@strawberry.input()
class ProductOrder:
    ean: Optional[Order] = None
    name: Optional[Order] = None
    name_en: Optional[Order] = None
    nutri_score: Optional[Order] = None
    quantity: Optional[Order] = None
    brand_name: Optional[Order] = None
    category_name: Optional[Order] = None


strawberry_sqlalchemy_mapper.finalize()
