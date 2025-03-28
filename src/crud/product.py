from sqlmodel import select

from src.config.session import get_postgres_session
from src.crud.base import CRUDBase
from src.models.product import ProductModel


class CrudProduct(CRUDBase[ProductModel, ProductModel, str]):
    def __init__(self) -> None:
        super().__init__(model=ProductModel)

    async def get_by_category(self, category: str) -> list[ProductModel]:
        async with get_postgres_session() as session:
            result = await session.exec(
                select(self.model).where(ProductModel.category_name == category)
            )
            return list(result.all())


crud_product = CrudProduct()
