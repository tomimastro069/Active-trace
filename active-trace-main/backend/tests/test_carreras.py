import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.dependencies import get_db, get_current_user
from app.schemas.auth import CurrentUser
from app.models.carrera import Carrera
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.audit_log import AuditLog
from sqlalchemy import select

@pytest.mark.asyncio
async def test_carreras_crud_and_audit(db_session, monkeypatch):
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    # Primero creamos el tenant y el usuario en la base de datos para las FKs
    tenant = Tenant(id=tenant_id, name="Test Tenant")
    actor = Usuario(id=actor_id, tenant_id=tenant_id, email="coord_carreras@example.com", hashed_password="hashed_pass")
    db_session.add_all([tenant, actor])
    await db_session.commit()

    # Mock de los permisos efectivos del repositorio
    async def mock_get_perms(*args, **kwargs):
        return ["estructura:gestionar"]
    
    monkeypatch.setattr(
        "app.repositories.asignacion.AsignacionRepository.get_effective_permissions",
        mock_get_perms
    )

    # Mock de usuario actual
    mock_user = CurrentUser(
        id=actor_id,
        tenant_id=tenant_id,
        email="coord_carreras@example.com",
        roles=["COORDINADOR"]
    )

    # Overrides de dependencias
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Crear Carrera (POST)
        payload = {
            "codigo": "ING_SIST",
            "nombre": "Ingeniería en Sistemas de Información",
            "estado": "Activa"
        }
        res_create = await ac.post("/api/v1/admin/carreras/", json=payload)
        assert res_create.status_code == 201
        data_create = res_create.json()
        assert data_create["codigo"] == "ING_SIST"
        assert data_create["nombre"] == "Ingeniería en Sistemas de Información"
        assert data_create["estado"] == "Activa"
        carrera_id = data_create["id"]

        # Verificar log de auditoría CARRERA_CREAR
        query_audit = select(AuditLog).where(AuditLog.accion == "CARRERA_CREAR")
        res_audit = await db_session.execute(query_audit)
        audit_log = res_audit.scalars().first()
        assert audit_log is not None
        assert audit_log.tenant_id == tenant_id
        assert audit_log.actor_id == actor_id
        assert audit_log.detalle["id"] == carrera_id

        # 2. Intentar crear con el mismo código (debe fallar por unicidad)
        res_create_dup = await ac.post("/api/v1/admin/carreras/", json=payload)
        assert res_create_dup.status_code == 400
        assert "Ya existe una carrera con el código" in res_create_dup.json()["detail"]

        # 3. Listar Carreras (GET)
        res_list = await ac.get("/api/v1/admin/carreras/")
        assert res_list.status_code == 200
        data_list = res_list.json()
        assert len(data_list) == 1
        assert data_list[0]["id"] == carrera_id

        # 4. Obtener Carrera por ID (GET)
        res_get = await ac.get(f"/api/v1/admin/carreras/{carrera_id}")
        assert res_get.status_code == 200
        assert res_get.json()["codigo"] == "ING_SIST"

        # 5. Modificar Carrera (PATCH)
        update_payload = {
            "nombre": "Ingeniería en Sistemas de Información - UTN"
        }
        res_patch = await ac.patch(f"/api/v1/admin/carreras/{carrera_id}", json=update_payload)
        assert res_patch.status_code == 200
        assert res_patch.json()["nombre"] == "Ingeniería en Sistemas de Información - UTN"

        # Verificar log de auditoría CARRERA_MODIFICAR
        query_audit_mod = select(AuditLog).where(AuditLog.accion == "CARRERA_MODIFICAR")
        res_audit_mod = await db_session.execute(query_audit_mod)
        audit_mod = res_audit_mod.scalars().first()
        assert audit_mod is not None
        assert audit_mod.detalle["nombre_nuevo"] == "Ingeniería en Sistemas de Información - UTN"

        # 6. Desactivar (Soft-Delete) Carrera (PATCH estado -> Inactiva)
        state_payload = {
            "estado": "Inactiva"
        }
        res_state = await ac.patch(f"/api/v1/admin/carreras/{carrera_id}", json=state_payload)
        assert res_state.status_code == 200
        assert res_state.json()["estado"] == "Inactiva"

        # Verificar log de auditoría CARRERA_ESTADO_CAMBIAR
        query_audit_state = select(AuditLog).where(AuditLog.accion == "CARRERA_ESTADO_CAMBIAR")
        res_audit_state = await db_session.execute(query_audit_state)
        audit_state = res_audit_state.scalars().first()
        assert audit_state is not None
        assert audit_state.detalle["estado_nuevo"] == "Inactiva"

    # Verificar que el registro sigue existiendo en la DB físicamente
    query_carrera = select(Carrera).where(Carrera.id == uuid.UUID(carrera_id))
    res_carrera = await db_session.execute(query_carrera)
    carrera_db = res_carrera.scalars().first()
    assert carrera_db is not None
    assert carrera_db.estado == "Inactiva"

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_carreras_tenant_isolation(db_session, monkeypatch):
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    actor_a = uuid.uuid4()
    actor_b = uuid.uuid4()

    # Creación de tenants y usuarios para la FK
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
        # Tenant A crea carrera
        app.dependency_overrides[get_current_user] = lambda: mock_user_a
        res_create_a = await ac.post("/api/v1/admin/carreras/", json={"codigo": "ING_SIST", "nombre": "Sistemas A"})
        assert res_create_a.status_code == 201
        id_a = res_create_a.json()["id"]

        # Tenant B crea la misma carrera (con mismo código) -> Debe permitirlo por aislamiento de tenant
        app.dependency_overrides[get_current_user] = lambda: mock_user_b
        res_create_b = await ac.post("/api/v1/admin/carreras/", json={"codigo": "ING_SIST", "nombre": "Sistemas B"})
        assert res_create_b.status_code == 201
        id_b = res_create_b.json()["id"]
        assert id_a != id_b

        # Tenant A lista carreras -> Solo debe ver la suya
        app.dependency_overrides[get_current_user] = lambda: mock_user_a
        res_list_a = await ac.get("/api/v1/admin/carreras/")
        assert len(res_list_a.json()) == 1
        assert res_list_a.json()[0]["id"] == id_a

        # Tenant A intenta acceder a la carrera de Tenant B -> Debe dar 404
        res_get_b_from_a = await ac.get(f"/api/v1/admin/carreras/{id_b}")
        assert res_get_b_from_a.status_code == 404

    app.dependency_overrides.clear()
