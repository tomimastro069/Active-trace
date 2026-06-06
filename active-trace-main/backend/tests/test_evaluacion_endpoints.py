import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from datetime import datetime
from app.main import app
from app.core.dependencies import get_db, get_current_user
from app.schemas.auth import CurrentUser
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.carrera import Carrera
from app.models.materia import Materia
from app.models.cohorte import Cohorte
from app.models.evaluacion import Evaluacion, EvaluacionTipoEnum
from app.core.security import generate_email_hash

@pytest.fixture
async def evaluacion_api_setup(db_session):
    tenant_id = uuid.uuid4()
    admin_id = uuid.uuid4()
    alumno_id = uuid.uuid4()

    tenant = Tenant(id=tenant_id, name="Tenant Test")
    db_session.add(tenant)
    await db_session.flush()

    admin = Usuario(
        id=admin_id,
        tenant_id=tenant_id,
        email="admin@test.com",
        email_hash=generate_email_hash("admin@test.com"),
        hashed_password="pwd"
    )
    alumno = Usuario(
        id=alumno_id,
        tenant_id=tenant_id,
        email="alumno@test.com",
        email_hash=generate_email_hash("alumno@test.com"),
        hashed_password="pwd"
    )
    db_session.add_all([admin, alumno])
    await db_session.flush()

    carrera = Carrera(tenant_id=tenant.id, codigo="CAR", nombre="Carrera")
    materia = Materia(tenant_id=tenant.id, codigo="MAT", nombre="Materia")
    db_session.add_all([carrera, materia])
    await db_session.flush()

    cohorte = Cohorte(tenant_id=tenant.id, carrera_id=carrera.id, nombre="Cohorte", anio=2026, vig_desde=datetime(2026, 1, 1).date(), vig_hasta=datetime(2026, 12, 31).date())
    db_session.add(cohorte)
    await db_session.flush()

    eval_obj = Evaluacion(
        tenant_id=tenant.id,
        materia_id=materia.id,
        cohorte_id=cohorte.id,
        tipo=EvaluacionTipoEnum.COLOQUIO,
        instancia="Coloquio Final",
        dias_disponibles=2,
        cupos_totales=2
    )
    db_session.add(eval_obj)
    await db_session.flush()

    await db_session.commit()

    return {
        "tenant_id": tenant_id,
        "admin_id": admin_id,
        "alumno_id": alumno_id,
        "evaluacion_id": eval_obj.id,
        "materia_id": materia.id,
        "cohorte_id": cohorte.id
    }

@pytest.mark.asyncio
async def test_crear_evaluacion_endpoint(db_session, monkeypatch, evaluacion_api_setup):
    setup = evaluacion_api_setup

    mock_admin = CurrentUser(
        id=setup["admin_id"],
        tenant_id=setup["tenant_id"],
        email="admin@test.com",
        roles=["ADMIN"]
    )

    async def mock_get_admin_perms(*args, **kwargs):
        return ["encuentros:gestionar"] # Arbitrary permission to manage evaluations
    
    monkeypatch.setattr(
        "app.repositories.asignacion.AsignacionRepository.get_effective_permissions",
        mock_get_admin_perms
    )

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_admin

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "materia_id": str(setup["materia_id"]),
            "cohorte_id": str(setup["cohorte_id"]),
            "tipo": "Coloquio",
            "instancia": "Coloquio 2",
            "dias_disponibles": 3,
            "cupos_totales": 15
        }
        res = await ac.post("/api/v1/admin/evaluaciones/", json=payload, headers={"Authorization": "Bearer mock"})
        assert res.status_code == 201
        data = res.json()
        assert data["instancia"] == "Coloquio 2"
        assert data["cupos_totales"] == 15

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_reservar_evaluacion_endpoint(db_session, monkeypatch, evaluacion_api_setup):
    setup = evaluacion_api_setup

    mock_alumno = CurrentUser(
        id=setup["alumno_id"],
        tenant_id=setup["tenant_id"],
        email="alumno@test.com",
        roles=["ALUMNO"]
    )

    async def mock_get_alumno_perms(*args, **kwargs):
        return [] # Alumno doesn't need specific backend perms typically, but uses endpoint scoping
    
    monkeypatch.setattr(
        "app.repositories.asignacion.AsignacionRepository.get_effective_permissions",
        mock_get_alumno_perms
    )

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_alumno

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "evaluacion_id": str(setup["evaluacion_id"]),
            "alumno_id": str(setup["alumno_id"]),
            "fecha_hora": "2026-07-06T10:00:00Z"
        }
        res = await ac.post("/api/v1/reservas/evaluaciones/", json=payload, headers={"Authorization": "Bearer mock"})
        assert res.status_code == 201
        data = res.json()
        assert data["evaluacion_id"] == str(setup["evaluacion_id"])
        assert data["alumno_id"] == str(setup["alumno_id"])

        # Try duplicate
        res_dup = await ac.post("/api/v1/reservas/evaluaciones/", json=payload, headers={"Authorization": "Bearer mock"})
        assert res_dup.status_code == 400
        assert "activa" in res_dup.json()["detail"].lower()

    app.dependency_overrides.clear()
