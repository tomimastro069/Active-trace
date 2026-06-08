import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.dependencies import get_db, get_current_user
from app.schemas.auth import CurrentUser

@pytest.mark.asyncio
async def test_get_interacciones_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Request without Authorization header should fail with 401 due to TenantMiddleware
        response = await ac.get("/api/v1/auditoria/interacciones")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_logs_unauthorized():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Request without Authorization header should fail with 401 due to TenantMiddleware
        response = await ac.get("/api/v1/auditoria/logs")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_interacciones_forbidden(db_session, monkeypatch):
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    
    # Mock empty permissions (forbidden)
    async def mock_get_asig_perms(*args, **kwargs):
        return []
    
    monkeypatch.setattr(
        "app.repositories.asignacion.AsignacionRepository.get_effective_permissions",
        mock_get_asig_perms
    )
    
    mock_user = CurrentUser(
        id=actor_id,
        tenant_id=tenant_id,
        email="user_no_perms@example.com",
        roles=["PROFESOR"]
    )
    
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/auditoria/interacciones",
            headers={"Authorization": "Bearer fake"}
        )
        assert response.status_code == 403

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_interacciones_admin(db_session, monkeypatch):
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    
    # Mock admin permissions
    async def mock_get_asig_perms(*args, **kwargs):
        return ["auditoria:ver"]
    
    monkeypatch.setattr(
        "app.repositories.asignacion.AsignacionRepository.get_effective_permissions",
        mock_get_asig_perms
    )
    
    mock_admin = CurrentUser(
        id=actor_id,
        tenant_id=tenant_id,
        email="admin_audit@example.com",
        roles=["ADMIN"]
    )
    
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/auditoria/interacciones",
            headers={"Authorization": "Bearer fake"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "daily_activity" in data
        assert "teacher_communications" in data
        assert "teacher_subject_interactions" in data

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_logs_admin(db_session, monkeypatch):
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    
    # Mock admin permissions
    async def mock_get_asig_perms(*args, **kwargs):
        return ["auditoria:ver"]
    
    monkeypatch.setattr(
        "app.repositories.asignacion.AsignacionRepository.get_effective_permissions",
        mock_get_asig_perms
    )
    
    mock_admin = CurrentUser(
        id=actor_id,
        tenant_id=tenant_id,
        email="admin_audit@example.com",
        roles=["ADMIN"]
    )
    
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/auditoria/logs",
            headers={"Authorization": "Bearer fake"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    app.dependency_overrides.clear()
