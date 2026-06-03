import pytest
import uuid
import io
import httpx
from datetime import date
from unittest.mock import patch, AsyncMock
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.dependencies import get_db, get_current_user
from app.schemas.auth import CurrentUser
from app.models.tenant import Tenant
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.padron import VersionPadron, EntradaPadron
from sqlalchemy import select

@pytest.fixture
async def setup_entities(db_session):
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    tenant = Tenant(id=tenant_id, name="UTN FRBA Test")
    actor = Usuario(
        id=actor_id,
        tenant_id=tenant_id,
        email="coordinator@test.com",
        hashed_password="password",
        nombre="Coordinator",
        apellidos="RBAC"
    )
    carrera = Carrera(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        codigo="ISI",
        nombre="Sistemas",
        estado="Activa"
    )
    db_session.add_all([tenant, actor, carrera])
    await db_session.flush()

    cohorte = Cohorte(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        carrera_id=carrera.id,
        nombre="Cohorte 2026",
        anio=2026,
        vig_desde=date(2026, 3, 1),
        estado="Activa"
    )
    materia = Materia(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        codigo="AED",
        nombre="Algoritmos",
        estado="Activa"
    )
    db_session.add_all([cohorte, materia])
    await db_session.commit()

    return {
        "tenant_id": tenant_id,
        "actor_id": actor_id,
        "cohorte_id": cohorte.id,
        "materia_id": materia.id
    }

# We need to import Usuario in setup_entities so it's resolved
from app.models.usuario import Usuario

@pytest.mark.asyncio
async def test_manual_csv_upload_e2e(db_session, setup_entities, monkeypatch):
    actor_id = setup_entities["actor_id"]
    tenant_id = setup_entities["tenant_id"]
    materia_id = setup_entities["materia_id"]
    cohorte_id = setup_entities["cohorte_id"]

    # Mock permission check to always pass
    async def mock_get_perms(*args, **kwargs):
        return ["estructura:gestionar"]
    
    monkeypatch.setattr(
        "app.repositories.asignacion.AsignacionRepository.get_effective_permissions",
        mock_get_perms
    )

    mock_user = CurrentUser(
        id=actor_id,
        tenant_id=tenant_id,
        email="coordinator@test.com",
        roles=["COORDINADOR"]
    )

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Prepare mock CSV file content
    csv_content = (
        "email,nombre,apellidos,comision,regional\n"
        "alumn1@test.com,Pedro,Rodriguez,1K3,Medrano\n"
        "alumn2@test.com,Clara,Sosa,1K3,Campus\n"
    )
    csv_file = io.BytesIO(csv_content.encode('utf-8'))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        files = {"file": ("students.csv", csv_file, "text/csv")}
        data = {
            "materia_id": str(materia_id),
            "cohorte_id": str(cohorte_id)
        }
        res = await ac.post("/api/v1/padron/import-csv", files=files, data=data)
        assert res.status_code == 201
        
        # Verify response attributes
        res_data = res.json()
        assert res_data["activa"] is True
        assert res_data["materia_id"] == str(materia_id)
        assert res_data["cohorte_id"] == str(cohorte_id)

        # Verify DB entries
        version_id = uuid.UUID(res_data["id"])
        query = select(EntradaPadron).where(EntradaPadron.version_id == version_id)
        res_entries = await db_session.execute(query)
        entries = res_entries.scalars().all()
        assert len(entries) == 2
        
        emails = {e.email for e in entries}
        assert "alumn1@test.com" in emails
        assert "alumn2@test.com" in emails

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_moodle_sync_success_with_retry_on_502(db_session, setup_entities, monkeypatch):
    actor_id = setup_entities["actor_id"]
    tenant_id = setup_entities["tenant_id"]
    materia_id = setup_entities["materia_id"]
    cohorte_id = setup_entities["cohorte_id"]

    # Mock permissions
    async def mock_get_perms(*args, **kwargs):
        return ["estructura:gestionar"]
    monkeypatch.setattr(
        "app.repositories.asignacion.AsignacionRepository.get_effective_permissions",
        mock_get_perms
    )

    mock_user = CurrentUser(id=actor_id, tenant_id=tenant_id, email="coordinator@test.com", roles=["COORDINADOR"])
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Mock httpx.AsyncClient.get to simulate transient HTTP 502
    call_count = 0
    
    async def mock_get(url, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        req = httpx.Request("GET", url)
        if call_count == 1:
            # First attempt: 502 Bad Gateway
            return httpx.Response(status_code=502, request=req)
        else:
            # Second attempt: 200 OK with students list
            return httpx.Response(
                status_code=200,
                json=[
                    {
                        "firstname": "MoodleUser",
                        "lastname": "Test",
                        "email": "moodle_user@test.com",
                        "groups": [{"name": "GroupA"}]
                    }
                ],
                request=req
            )

    # Patch tenacity wait so the test runs instantly without delay
    with patch("tenacity.nap.time.sleep", return_value=None):
        with patch("httpx.AsyncClient.get", side_effect=mock_get):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                payload = {
                    "materia_id": str(materia_id),
                    "cohorte_id": str(cohorte_id),
                    "moodle_course_id": 101
                }
                res = await ac.post("/api/v1/padron/sync", json=payload)
                assert res.status_code == 200
                assert call_count == 2  # Verify retry occurred

                # Check database entry
                version_id = uuid.UUID(res.json()["id"])
                query = select(EntradaPadron).where(EntradaPadron.version_id == version_id)
                res_entries = await db_session.execute(query)
                entries = res_entries.scalars().all()
                assert len(entries) == 1
                assert entries[0].email == "moodle_user@test.com"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_moodle_sync_fail_all_retries(db_session, setup_entities, monkeypatch):
    actor_id = setup_entities["actor_id"]
    tenant_id = setup_entities["tenant_id"]
    materia_id = setup_entities["materia_id"]
    cohorte_id = setup_entities["cohorte_id"]

    # Mock permissions
    async def mock_get_perms(*args, **kwargs):
        return ["estructura:gestionar"]
    monkeypatch.setattr(
        "app.repositories.asignacion.AsignacionRepository.get_effective_permissions",
        mock_get_perms
    )

    mock_user = CurrentUser(id=actor_id, tenant_id=tenant_id, email="coordinator@test.com", roles=["COORDINADOR"])
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Mock httpx.AsyncClient.get to always return HTTP 502
    async def mock_get_always_fail(url, *args, **kwargs):
        return httpx.Response(status_code=502, request=httpx.Request("GET", url))

    # Patch tenacity wait so the test runs instantly
    with patch("tenacity.nap.time.sleep", return_value=None):
        with patch("httpx.AsyncClient.get", side_effect=mock_get_always_fail):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                payload = {
                    "materia_id": str(materia_id),
                    "cohorte_id": str(cohorte_id),
                    "moodle_course_id": 101
                }
                res = await ac.post("/api/v1/padron/sync", json=payload)
                assert res.status_code == 502
                assert "Error al sincronizar con Moodle WS" in res.json()["detail"]

                # Ensure no new VersionPadron is added to database
                query = select(VersionPadron).where(
                    VersionPadron.materia_id == materia_id,
                    VersionPadron.cohorte_id == cohorte_id
                )
                res_versions = await db_session.execute(query)
                assert len(res_versions.scalars().all()) == 0

    app.dependency_overrides.clear()
