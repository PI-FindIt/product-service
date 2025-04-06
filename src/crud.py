from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config.session import get_postgres_session
from src.models import NutritionModel, ProductModel


class CrudProduct:
    @staticmethod
    @asynccontextmanager
    async def _get_session(
        session: AsyncSession | None = None,
    ) -> AsyncGenerator[AsyncSession, None]:
        if session is not None:
            yield session
            return
        async with get_postgres_session() as session:
            yield session

    async def _add_to_db(
        self, obj: ProductModel, session: AsyncSession | None = None
    ) -> ProductModel:
        async with self._get_session(session) as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def create(self, obj: ProductModel) -> ProductModel:
        db_obj = ProductModel.model_validate(obj)
        return await self._add_to_db(db_obj)

    async def get(
        self, id: str, session: AsyncSession | None = None
    ) -> ProductModel | None:
        async with self._get_session(session) as session:
            a = await session.get(ProductModel, id)
            if a is None:
                return None
            a.nutrition = NutritionModel.model_validate(a.nutrition)
            return a

    async def get_all(self, session: AsyncSession | None = None) -> list[ProductModel]:
        async with self._get_session(session) as session:
            result = await session.exec(select(ProductModel))
            return list(result.all())

    async def get_by_category(
        self, category: str, session: AsyncSession | None = None
    ) -> list[ProductModel]:
        async with self._get_session(session) as session:
            result = await session.exec(
                select(ProductModel).where(ProductModel.category_name == category)
            )
            return list(result.all())

    async def update(
        self, id: str, obj: ProductModel, session: AsyncSession | None = None
    ) -> ProductModel | None:
        db_obj = await self.get(id, session)
        if db_obj is None:
            return None

        db_obj.sqlmodel_update(obj)
        return await self._add_to_db(db_obj, session)

    async def delete(self, id: str, session: AsyncSession | None = None) -> bool:
        obj = await self.get(id, session)
        if obj is None:
            return False

        async with self._get_session(session) as session:
            await session.delete(obj)
            await session.commit()
            return True


crud = CrudProduct()
