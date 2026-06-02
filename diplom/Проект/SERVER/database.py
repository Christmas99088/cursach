import os
import asyncio
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from fastapi import Depends
from dotenv import load_dotenv
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

load_dotenv()

class Settings:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", 3306)
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_NAME = os.getenv("DB_NAME", "airline_booking")

    @property
    def DATABASE_URL_async(self):
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()

# Исправление для Windows + Python 3.13
import sys
if sys.platform == "win32" and sys.version_info >= (3, 13):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

engine = create_async_engine(
    url=settings.DATABASE_URL_async,
    echo=False,  # Отключаем логирование SQL для производительности
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=False,
    pool_recycle=3600,
    connect_args={
        "autocommit": True,
        "local_infile": True,
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=True,
    autocommit=False
)

metadata = MetaData()


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


async def get_db() -> AsyncSession:
    """
    Зависимость для получения асинхронной сессии БД
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        await session.rollback()
        raise
    finally:
        try:
            await session.close()
        except Exception as e:
            logger.warning(f"Error closing session: {e}")


async def setup_database():
    """
    Создание всех таблиц в базе данных
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created successfully!")
            print("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        print(f"❌ Error creating database tables: {e}")
        raise


async def drop_database():
    """
    Удаление всех таблиц (для тестирования)
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped!")
            print("Database tables dropped!")
    except Exception as e:
        logger.error(f"Error dropping database: {e}")
        print(f"Error dropping database: {e}")
        raise


async def check_connection():
    """
    Проверка подключения к базе данных
    """
    try:
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            data = result.fetchone()
            if data and data[0] == 1:
                print("✅ Database connection successful!")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    return False