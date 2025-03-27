from src.crud.base import CRUDBase
from src.models.brand import BrandModel, BrandBaseModel


class CrudBrand(CRUDBase[BrandModel, BrandBaseModel, int]):
    def __init__(self) -> None:
        super().__init__(model=BrandModel)


crud_brand = CrudBrand()
