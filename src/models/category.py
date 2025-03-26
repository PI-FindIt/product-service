from typing import Optional

from sqlmodel import SQLModel, Field


class CategoryBase(SQLModel):
    name: str


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    parents: list["Category"]
