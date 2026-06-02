from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import Settings
from app.models.base import Base

# Force config load to get env vars
settings = Settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base is imported from models.base for consistency
__all__ = ['engine', 'SessionLocal', 'AsyncSession', 'Base']
