from src.crud.base import CRUDBase
from src.models.product import Product, ProductBase


class CrudProduct(CRUDBase[Product, ProductBase, int]):
    def __init__(self) -> None:
        super().__init__(model=Product)


crud_product = CrudProduct()
