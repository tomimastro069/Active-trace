import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_get_db_yields_session_and_closes(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
    
    from app.core.dependencies import get_db
    
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    # We want to patch the sessionmaker to return our mock session
    with patch("app.core.dependencies.SessionLocal", return_value=mock_session):
        db_generator = get_db()
        session = await anext(db_generator)
        assert session == mock_session
        
        # Verify it closes when generator finishes
        with pytest.raises(StopAsyncIteration):
            await anext(db_generator)
            
        mock_session.close.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_db_closes_on_exception(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
    
    from app.core.dependencies import get_db
    
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    
    with patch("app.core.dependencies.SessionLocal", return_value=mock_session):
        db_generator = get_db()
        session = await anext(db_generator)
        assert session == mock_session
        
        # Raise exception inside the generator's client scope
        with pytest.raises(ValueError, match="Database error"):
            # Instead of consuming normally, we throw into the generator
            await db_generator.athrow(ValueError("Database error"))
            
        # Verify close was still awaited
        mock_session.close.assert_awaited_once()

