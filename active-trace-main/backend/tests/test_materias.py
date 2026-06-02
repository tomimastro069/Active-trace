import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.dependencies import get_db, get_current_user
from app.schemas.auth import CurrentUser
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.audit_log import AuditLog
from sqlalchemy import select

@pytest.mark.asyncio
async def test_materias_crud_and_audit(db_session, monkeypatch):
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    # Creación de tenant y usuario para FKs
    tenant = Tenant(id=tenant_id, name="Test Tenant")
    actor = Usuario(id=actor_id, tenant_id=tenant_id, email="coord_materias@example.com", hashed_password="hashed_pass")
    db_session.add_all([tenant, actor])
    await db_session.commit()

    async def mock_get_perms(*args, **kwargs):
        return ["estructura:gestionar"]
    
    monkeypatch.setattr(
        "app.repositories.asignacion.AsignacionRepository.get_effective_permissions",
        mock_get_perms
    )

    mock_user = CurrentUser(
        id=actor_id,
        tenant_id=tenant_id,
        email="coord_materias@example.com",
        roles=["COORDINADOR"]
    )

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Crear Materia (POST)
        payload = {
            "codigo": "ALGEBRA",
            "nombre": "Álgebra y Geometría Analítica",
            "estado": "Activa"
        }
        res_create = await ac.post("/api/v1/admin/materias/", json=payload)
        assert res_create.status_code == 201
        data_create = res_create.json()
        assert data_create["codigo"] == "ALGEBRA"
        assert data_create["nombre"] == "Álgebra y Geometría Analítica"
        materia_id = data_create["id"]

        # Verificar log de auditoría MATERIA_CREAR
        query_audit = select(AuditLog).where(AuditLog.accion == "MATERIA_CREAR")
        res_audit = await db_session.execute(query_audit)
        audit_log = res_audit.scalars().first()
        assert audit_log is not None
        assert audit_log.materia_id == uuid.UUID(materia_id)

        # 2. Intentar crear con el mismo código (debe fallar por unicidad)
        res_create_dup = await ac.post("/api/v1/admin/materias/", json=payload)
        assert res_create_dup.status_code == 400
        assert "Ya existe una materia con el código" in res_create_dup.json()["detail"]

        # 3. Listar Materias (GET)
        res_list = await ac.get("/api/v1/admin/materias/")
        assert res_list.status_code == 200
        assert len(res_list.json()) == 1

        # 4. Modificar Materia (PATCH)
        res_patch = await ac.patch(f"/api/v1/admin/materias/{materia_id}", json={"nombre": "Álgebra Lineal"})
        assert res_patch.status_code == 200
        assert res_patch.json()["nombre"] == "Álgebra Lineal"

        # Verificar log de auditoría MATERIA_MODIFICAR
        query_audit_mod = select(AuditLog).where(AuditLog.accion == "MATERIA_MODIFICAR")
        res_audit_mod = await db_session.execute(query_audit_mod)
        audit_mod = res_audit_mod.scalars().first()
        assert audit_mod is not None

        # 5. Desactivar (Soft-Delete) Materia (PATCH estado -> Inactiva)
        res_state = await ac.patch(f"/api/v1/admin/materias/{materia_id}", json={"estado": "Inactiva"})
        assert res_state.status_code == 200
        assert res_state.json()["estado"] == "Inactiva"

        # Verificar log de auditoría MATERIA_ESTADO_CAMBIAR
        query_audit_state = select(AuditLog).where(AuditLog.accion == "MATERIA_ESTADO_CAMBIAR")
        res_audit_state = await db_session.execute(query_audit_state)
        audit_state = res_audit_state.scalars().first()
        assert audit_state is not None

    # Verificar que sigue existiendo en DB físicamente
    query_materia = select(Materia).where(Materia.id == uuid.UUID(materia_id))
    res_materia = await db_session.execute(query_materia)
    materia_db = res_materia.scalars().first()
    assert materia_db is not None
    assert materia_db.estado == "Inactiva"

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_materias_tenant_isolation(db_session, monkeypatch):
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    actor_a = uuid.uuid4()
    actor_b = uuid.uuid4()

    # Creación de tenants y usuarios para FK
    db_session.add(Tenant(id=tenant_a, name="Tenant A"))
    db_session.add(Tenant(id=tenant_b, name="Tenant B"))
    db_session.add(Usuario(id=actor_a, tenant_id=tenant_a, email="user_a@example.com", hashed_password="pass"))
    db_session.add(Usuario(id=actor_b, tenant_id=tenant_b, email="user_b@example.com", hashed_password="pass"))
    await db_session.commit()

    async def mock_get_perms(*args, **kwargs):
        return ["estructura:gestionar"]
    
    monkeypatch.setattr(
        "app.repositories.asignacion.AsignacionRepository.get_effective_permissions",
        mock_get_perms
    )

    mock_user_a = CurrentUser(id=actor_a, tenant_id=tenant_a, email="user_a@example.com", roles=["ADMIN"])
    mock_user_b = CurrentUser(id=actor_b, tenant_id=tenant_b, email="user_b@example.com", roles=["ADMIN"])

    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Tenant A crea materia
        app.dependency_overrides[get_current_user] = lambda: mock_user_a
        res_create_a = await ac.post("/api/v1/admin/materias/", json={"codigo": "ALGEBRA", "nombre": "Álgebra A"})
        assert res_create_a.status_code == 201
        id_a = res_create_a.json()["id"]

        # Tenant B crea la misma materia (con mismo código)
        app.dependency_overrides[get_current_user] = lambda: mock_user_b
        res_create_b = await ac.post("/api/v1/admin/materias/", json={"codigo": "ALGEBRA", "nombre": "Álgebra B"})
        assert res_create_b.status_code == 201
        id_b = res_create_b.json()["id"]
        assert id_a != id_b

        # Tenant A lista materias
        app.dependency_overrides[get_current_user] = lambda: mock_user_a
        res_list_a = await ac.get("/api/v1/admin/materias/")
        assert len(res_list_a.json()) == 1
        assert res_list_a.json()[0]["id"] == id_a

        # Tenant A intenta acceder a la materia de Tenant B
        res_get_b_from_a = await ac.get(f"/api/v1/admin/materias/{id_b}")
        assert res_get_b_from_a.status_code == 404

    app.dependency_overrides.clear()
