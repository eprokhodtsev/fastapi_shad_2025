import logging

from typing import AsyncGenerator, Callable, Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.models.base import BaseModel
from src.configurations.settings import settings
from src.models.sellers import Seller
from src.models.books import Book
from src.db_init_data import init_test_data

__all__ = ["global_init", "get_async_session", "create_db_and_tables"]

logger = logging.getLogger("__name__")

__async_engine: Optional[AsyncEngine] = None
__session_factory: Optional[Callable[[], AsyncSession]] = None

SQLALCHEMY_DATABASE_URL = settings.database_url


def global_init() -> None:
    global __async_engine, __session_factory

    if __session_factory:
        return

    if not __async_engine:
        __async_engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL, echo=True)

    __session_factory = async_sessionmaker(__async_engine)


async def get_async_session() -> AsyncGenerator:
    global __session_factory

    if not __session_factory:
        raise ValueError(
            {"message": "You must call global_init() before using this method"}
        )

    session: AsyncSession = __session_factory()

    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.error("Raises exception: %s", e)
        raise e
    finally:
        await session.rollback()
        await session.close()


async def create_db_and_tables():
    global __async_engine, __session_factory
    if not __async_engine:
        global_init()

    async with __async_engine.begin() as conn:
        # Проверяем, существует ли уже таблица sellers
        tables_exist = await conn.run_sync(
            lambda sync_conn: sync_conn.dialect.has_table(
                sync_conn, "sellers"
            )
        )

        if not tables_exist:
            # Создаем таблицы, если они не существуют
            await conn.run_sync(BaseModel.metadata.create_all)
            logger.info("Создание таблиц завершено.")
        else:
            logger.info("Таблицы уже существуют, пропускаем создание.")
    
    # Добавляем тестовые данные
    async with __session_factory() as session:
        try:
            await init_test_data(session)
        except Exception as e:
            logger.error(f"Ошибка при добавлении тестовых данных: {e}")
            await session.rollback()

async def delete_db_and_tables():
    global __async_engine

    if __async_engine is None:
        raise ValueError({"message": "You must call global_init() before using this method."})

    async with __async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
