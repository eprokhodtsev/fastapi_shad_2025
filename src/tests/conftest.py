""" Это модуль с фикстурами для пайтеста.
Фикстуры - это особые функции, которые не надо импортировать явно.
Сам пайтест подтягивает их по имени из файла conftest.py
"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

from src.configurations.settings import settings
from src.models import books  # noqa
from src.models.base import BaseModel
from src.models.books import Book  # noqa F401
from src.main import app

# DATABASE - Use in-memory SQLite for tests
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    DATABASE_URL, 
    poolclass=StaticPool,  # Use StaticPool for in-memory database
    echo=False,
    connect_args={"check_same_thread": False}  # Allow multiple threads for SQLite
)

async_session_maker = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=True
)

async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# Override the get_db function in src.core.db
# We have to delay the import to prevent circular imports
from src.core.db import get_db
app.dependency_overrides[get_db] = override_get_async_db


@pytest_asyncio.fixture(autouse=True, scope="function")
async def initdb():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop(request) -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture
async def async_client() -> httpx.AsyncClient:
    # Using direct client without base_url to properly handle API paths
    async with httpx.AsyncClient(app=app, base_url="") as client:
        yield client


# Переопределяем движок для запуска тестов и подключаем его к тестовой базе.
# Это решает проблему с сохранностью данных в основной базе приложения.
# Фикстуры тестов их не зачистят.
# и обеспечивает чистую среду для запуска тестов. В ней не будет лишних записей.
# NOTE: These fixtures are commented out as they duplicate functionality provided by the initdb fixture
# async_test_engine = create_async_engine(
#     settings.database_test_url,
#     echo=True,
# )

# Создаем фабрику сессий для тестового движка.
# async_test_session = sessionmaker(
#     async_test_engine, expire_on_commit=False, autoflush=False
# )


# Создаем таблицы в тестовой БД. Предварительно удаляя старые.
# NOTE: This fixture is commented out as it duplicates functionality provided by the initdb fixture
# @pytest_asyncio.fixture(scope="session", autouse=True)
# async def create_tables() -> None:
#     """Create tables in DB."""
#     async with async_test_engine.begin() as connection:
#         await connection.run_sync(BaseModel.metadata.drop_all)
#         await connection.run_sync(BaseModel.metadata.create_all)


# Коллбэк для переопределения сессии в приложении
@pytest.fixture(scope="function")
def override_get_async_session(db_session):
    async def _override_get_async_session():
        yield db_session

    return _override_get_async_session


# Мы не можем создать 2 приложения (app) - это приведет к ошибкам.
# Поэтому, на время запуска тестов мы подменяем там зависимость с сессией
@pytest.fixture(scope="function")
def test_app(override_get_async_session):
    from src.configurations.database import get_async_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    return app


# создаем асинхронного клиента для ручек
@pytest_asyncio.fixture(scope="function")
async def async_client(test_app):
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://127.0.0.1:8000"
    ) as test_client:
        yield test_client
