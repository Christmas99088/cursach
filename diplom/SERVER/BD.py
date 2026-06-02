import asyncio
import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

import hashlib


class Settings:
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = "root"
    DB_NAME = "auto_service_db"

    @property
    def DATABASE_URL_sync(self):
        return f"mysql+mysqldb://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_async(self):
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


def hash_(password: str) -> str:
    print(hashlib.sha256(password.encode()).hexdigest())
    return hashlib.sha256(password.encode()).hexdigest()

def check_hash(password: str, hashed_password: str) -> bool:
    return hash_(password) == hashed_password


engine = create_async_engine(url=Settings().DATABASE_URL_async,
                       echo=False,
                       pool_size=5,
                       max_overflow=10)

new_session = async_sessionmaker(engine, expire_on_commit=False)
metadata = MetaData()



#Синхронный вариант
'''def get_connection() -> Connection:
    with engine.connect() as connection:
        #print(connection.execute(text("SELECT VERSION()")).first())
        #print(connection.execute(text("SELECT * FROM to_do_list.users")).first())
        return connection
'''

async def get_connection():
    async with new_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def setup_database():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("CREATED")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class Base(DeclarativeBase):pass


SessionDep = Annotated[AsyncSession, Depends(get_connection)]
