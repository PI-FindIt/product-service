import dataclasses
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable

from sqlalchemy import select, or_, and_, ClauseList, UnaryExpression
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.session import get_postgres_session
from src.models import ProductModel, ProductFilter, Operator, ProductOrder, Order

order_map: dict[Order, Callable[[str], UnaryExpression]] = {
    Order.ASC: lambda name: getattr(ProductModel, name).asc(),
    Order.DESC: lambda name: getattr(ProductModel, name).desc(),
}


operations = {
    Operator.EQ: lambda k, v: getattr(ProductModel, k) == v,
    Operator.NE: lambda k, v: getattr(ProductModel, k) != v,
    Operator.LT: lambda k, v: getattr(ProductModel, k) < v,
    Operator.LE: lambda k, v: getattr(ProductModel, k) <= v,
    Operator.GT: lambda k, v: getattr(ProductModel, k) > v,
    Operator.GE: lambda k, v: getattr(ProductModel, k) >= v,
    Operator.LIKE: lambda k, v: getattr(ProductModel, k).like(v),
    Operator.ILIKE: lambda k, v: getattr(ProductModel, k).ilike(v),
    Operator.IN: lambda k, v: getattr(ProductModel, k).in_(v),
    Operator.NOT_IN: lambda k, v: getattr(ProductModel, k).notin_(v),
    Operator.IS: lambda k, v: getattr(ProductModel, k).is_(v),
    Operator.IS_NOT: lambda k, v: getattr(ProductModel, k).isnot(v),
    Operator.CONTAINS: lambda k, v: getattr(ProductModel, k).contains(v),
    Operator.NOT_CONTAINS: lambda k, v: getattr(ProductModel, k).notcontains(v),
    Operator.ANY: lambda k, v: getattr(ProductModel, k).any(v),
    Operator.ALL: lambda k, v: getattr(ProductModel, k).all(v),
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

    def _compose_query(self, filters: list[ProductFilter] | None) -> ClauseList:
        clauses = ClauseList()

        if filters is None:
            return clauses

        for filter_ in filters:
            for field in dataclasses.fields(filter_):
                value = getattr(filter_, field.name)
                if value is None:
                    continue

                match field.name:
                    case "and_":
                        clauses.append(and_(*self._compose_query(value)))
                    case "or_":
                        clauses.append(or_(*self._compose_query(value)))
                    case _:
                        clauses.append(operations[value.op](field.name, value.value))
        return clauses

    async def get_all(
        self,
        filters: ProductFilter | None = None,
        order_by: ProductOrder | None = None,
        session: AsyncSession | None = None,
    ) -> list[ProductModel]:
        async with self._get_session(session) as session:
            query = (
                select(ProductModel)
                .where(*self._compose_query([filters] if filters else None))
                .order_by(
                    *(
                        [
                            order_map[value](field.name)
                            for field in dataclasses.fields(order_by)
                            if (value := getattr(order_by, field.name)) is not None
                        ]
                        if order_by is not None
                        else []
                    )
                )
            )
            result = await session.execute(query)
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
