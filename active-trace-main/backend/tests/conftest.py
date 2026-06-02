import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.base import Base
from app.core.config import Settings


@pytest.fixture
def env_setup(monkeypatch):
    """Setup environment variables for testing"""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/active_trace_test")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-must-be-32-chars!")
    monkeypatch.setenv("ENCRYPTION_KEY", "12345678901234567890123456789012")  # Exactly 32 bytes
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")


@pytest.fixture
async def test_engine(env_setup):
    """Create an async SQLAlchemy engine for testing"""
    database_url = os.getenv("DATABASE_URL")
    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup: drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    """Provide an async database session for tests"""
    async_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def settings(env_setup):
    """Provide application settings"""
    return Settings()
