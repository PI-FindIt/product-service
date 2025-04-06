from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.session import get_postgres_session
from src.models import ProductModel


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
        return await self._add_to_db(obj)

    async def get(
        self, id: str, session: AsyncSession | None = None
    ) -> ProductModel | None:
        async with self._get_session(session) as session:
            return await session.get(ProductModel, id)

    async def get_all(self, session: AsyncSession | None = None) -> list[ProductModel]:
        async with self._get_session(session) as session:
            result = await session.execute(select(ProductModel))
            return result.scalars().all()

    async def get_by_category(
        self, category: str, session: AsyncSession | None = None
    ) -> list[ProductModel]:
        async with self._get_session(session) as session:
            result = await session.execute(
                select(ProductModel).where(ProductModel.category_name == category)
            )
            return result.scalars().all()

    async def delete(self, id: str, session: AsyncSession | None = None) -> bool:
        obj = await self.get(id, session)
        if obj is None:
            return False

        async with self._get_session(session) as session:
            await session.delete(obj)
            await session.commit()
            return True


crud = CrudProduct()
