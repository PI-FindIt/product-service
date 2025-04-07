from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.session import get_postgres_session
from src.models import ProductModel, ProductFilter, Operator


operations = {
    Operator.EQ: lambda q, k, v: q.where(getattr(ProductModel, k) == v),
    Operator.NE: lambda q, k, v: q.where(getattr(ProductModel, k) != v),
    Operator.LT: lambda q, k, v: q.where(getattr(ProductModel, k) < v),
    Operator.LE: lambda q, k, v: q.where(getattr(ProductModel, k) <= v),
    Operator.GT: lambda q, k, v: q.where(getattr(ProductModel, k) > v),
    Operator.GE: lambda q, k, v: q.where(getattr(ProductModel, k) >= v),
    Operator.LIKE: lambda q, k, v: q.where(getattr(ProductModel, k).like(v)),
    Operator.ILIKE: lambda q, k, v: q.where(getattr(ProductModel, k).ilike(v)),
    Operator.IN: lambda q, k, v: q.where(getattr(ProductModel, k).in_(v)),
    Operator.NOT_IN: lambda q, k, v: q.where(getattr(ProductModel, k).notin_(v)),
    Operator.IS: lambda q, k, v: q.where(getattr(ProductModel, k).is_(v)),
    Operator.IS_NOT: lambda q, k, v: q.where(getattr(ProductModel, k).isnot(v)),
    Operator.CONTAINS: lambda q, k, v: q.where(getattr(ProductModel, k).contains(v)),
    Operator.NOT_CONTAINS: lambda q, k, v: q.where(
        getattr(ProductModel, k).notcontains(v)
    ),
    Operator.ANY: lambda q, k, v: q.where(getattr(ProductModel, k).any(v)),
    Operator.ALL: lambda q, k, v: q.where(getattr(ProductModel, k).all(v)),
}


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

    async def get_all(
        self,
        filters: ProductFilter,
        session: AsyncSession | None = None,
    ) -> list[ProductModel]:
        async with self._get_session(session) as session:
            query = select(ProductModel)
            for key, value in [
                (column.key, getattr(filters, column.key))
                for column in ProductModel.__table__.columns
                if column.key != "nutrition"
                if getattr(filters, column.key) is not None
            ]:
                query = operations[value.op](query, key, value.value)
            result = await session.execute(query)
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
