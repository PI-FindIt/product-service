from contextlib import asynccontextmanager
from typing import AsyncGenerator

from alembic import command, config
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy import Connection, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.config.settings import settings

postgres_engine = AsyncEngine(create_engine(settings.POSTGRES_URI, future=True))


SQLAlchemyInstrumentor().instrument(engine=postgres_engine.sync_engine)


def run_postgres_upgrade(connection: Connection, cfg: config.Config) -> None:
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


async def init_postgres_db() -> None:
    async with postgres_engine.begin() as conn:
        await conn.run_sync(run_postgres_upgrade, config.Config("alembic.ini"))


@asynccontextmanager
async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        postgres_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
