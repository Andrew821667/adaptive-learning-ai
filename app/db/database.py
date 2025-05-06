import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import logging

logger = logging.getLogger(__name__)

# Получение строки подключения из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/adaptive_learning")

# Создание движка базы данных
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool
)

# Создание асинхронной сессии
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Базовая модель для ORM
Base = declarative_base()

# Функция для получения сессии БД
async def get_db():
    """Асинхронная функция-зависимость для получения сессии БД."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Инициализация БД
async def init_db():
    """Инициализация базы данных."""
    try:
        async with engine.begin() as conn:
            # Для разработки можно использовать create_all,
            # для продакшена лучше использовать миграции
            # await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
