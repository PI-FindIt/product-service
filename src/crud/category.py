from src.crud.base import CRUDBase
from src.models.category import Category, CategoryBase


class CrudCategory(CRUDBase[Category, CategoryBase, int]):
    def __init__(self) -> None:
        super().__init__(model=Category)


crud_category = CrudCategory()
