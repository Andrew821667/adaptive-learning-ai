import pytest
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.db.database import Base
from app.main import app
from fastapi.testclient import TestClient

# Настройка тестовой базы данных
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_adaptive_learning")

# Создание тестового движка базы данных
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool
)

# Создание тестовой асинхронной сессии
TestAsyncSession = sessionmaker(
    test_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Фикстура для получения тестового клиента FastAPI
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

# Фикстура для настройки и очистки тестовой базы данных
@pytest.fixture(scope="function")
async def async_db_session():
    # Создание всех таблиц в тестовой базе данных
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Создание сессии
    async with TestAsyncSession() as session:
        yield session
    
    # Очистка после тестов
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Используем pytest-asyncio для поддержки асинхронного тестирования
@pytest.fixture(scope="session")
def event_loop():
    """Создает экземпляр цикла событий для каждой тестовой сессии."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
