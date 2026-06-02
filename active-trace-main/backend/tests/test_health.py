import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_health_endpoint_up(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
    
    from app.main import app
    from app.core.dependencies import get_db
    
    # Mock database session to succeed on SELECT 1
    mock_db = AsyncMock()
    mock_db.execute.return_value = MagicMock()
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "up"
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_health_endpoint_down(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
    
    from app.main import app
    from app.core.dependencies import get_db
    
    # Mock database session to raise exception on SELECT 1
    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("DB Down")
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["database"] == "down"
    
    app.dependency_overrides.clear()

