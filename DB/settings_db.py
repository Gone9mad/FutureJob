import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.engine import URL
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


load_dotenv()


#####################################################
# Collecting the object's URL
db_url = URL.create(
    drivername="postgresql+asyncpg",  # Обязательно асинхронный драйвер
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_NAME")
)

# Create async engine
async_engine = create_async_engine(
    url=db_url,
    pool_size = 10,  # Максимум 10 постоянных соединений
    max_overflow = 20,  # До 20 дополнительных при пиках нагрузки
    pool_recycle = 3600  # Сбрасывать соединения каждый час
)

# Create async session
async_sessions = async_sessionmaker(async_engine, expire_on_commit=False)

# Create the object's MetaData
meta_obj = MetaData()


#####################################################
# Class ABS
class Base(AsyncAttrs, DeclarativeBase):
    pass
