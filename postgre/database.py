import asyncio
from contextlib import asynccontextmanager
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()
Base = declarative_base()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(
    DB_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=20,
)

AsyncSessionFabric = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession
)

@asynccontextmanager
async def get_db():
    async with AsyncSessionFabric() as session:
        yield session

async def check_db_connection():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
    return False

if __name__ == "__main__":
    print(asyncio.run(check_db_connection()))