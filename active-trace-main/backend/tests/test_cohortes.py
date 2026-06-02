import pytest
import uuid
from datetime import date
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.dependencies import get_db, get_current_user
from app.schemas.auth import CurrentUser
from app.models.cohorte import Cohorte
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.models.audit_log import AuditLog
from sqlalchemy import select

@pytest.mark.asyncio
async def test_cohortes_crud_validation_and_audit(db_session, monkeypatch):
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    # Creación de tenant y usuario para FKs
    tenant = Tenant(id=tenant_id, name="Test Tenant")
    actor = Usuario(id=actor_id, tenant_id=tenant_id, email="coord_cohortes@example.com", hashed_password="hashed_pass")
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
        email="coord_cohortes@example.com",
        roles=["COORDINADOR"]
    )

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: mock_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 0. Crear Carrera para asociar a la cohorte
        res_carrera = await ac.post("/api/v1/admin/carreras/", json={
            "codigo": "K_SIST",
            "nombre": "Sistemas de Info",
            "estado": "Activa"
        })
        assert res_carrera.status_code == 201
        carrera_id = res_carrera.json()["id"]

        # 1. Crear Cohorte exitosa (POST)
        payload = {
            "carrera_id": carrera_id,
            "nombre": "Cohorte 2026",
            "anio": 2026,
            "vig_desde": str(date(2026, 3, 1)),
            "vig_hasta": str(date(2026, 12, 18)),
            "estado": "Activa"
        }
        res_create = await ac.post("/api/v1/admin/cohortes/", json=payload)
        assert res_create.status_code == 201
        cohorte_id = res_create.json()["id"]

        # Verificar log de auditoría COHORTE_CREAR
        query_audit = select(AuditLog).where(AuditLog.accion == "COHORTE_CREAR")
        res_audit = await db_session.execute(query_audit)
        audit_log = res_audit.scalars().first()
        assert audit_log is not None

        # 2. Intentar crear cohorte duplicada (carrera_id, nombre) -> debe dar 400
        res_dup = await ac.post("/api/v1/admin/cohortes/", json=payload)
        assert res_dup.status_code == 400

        # 3. Listar Cohortes (GET)
        res_list = await ac.get("/api/v1/admin/cohortes/")
        assert res_list.status_code == 200
        assert len(res_list.json()) == 1

        # 4. Modificar Cohorte (PATCH)
        res_patch = await ac.patch(f"/api/v1/admin/cohortes/{cohorte_id}", json={"nombre": "Cohorte 2026 UTN"})
        assert res_patch.status_code == 200
        assert res_patch.json()["nombre"] == "Cohorte 2026 UTN"

        # Verificar log de auditoría COHORTE_MODIFICAR
        query_audit_mod = select(AuditLog).where(AuditLog.accion == "COHORTE_MODIFICAR")
        res_audit_mod = await db_session.execute(query_audit_mod)
        assert res_audit_mod.scalars().first() is not None

        # 5. Inactivar la carrera asociada
        res_carrera_inact = await ac.patch(f"/api/v1/admin/carreras/{carrera_id}", json={"estado": "Inactiva"})
        assert res_carrera_inact.status_code == 200

        # 6. Intentar crear una cohorte para esa carrera ahora inactivada -> debe fallar con 400
        payload_fail = {
            "carrera_id": carrera_id,
            "nombre": "Cohorte Fallida",
            "anio": 2026,
            "vig_desde": str(date(2026, 3, 1)),
            "estado": "Activa"
        }
        res_fail_post = await ac.post("/api/v1/admin/cohortes/", json=payload_fail)
        assert res_fail_post.status_code == 400
        assert "No se puede crear cohorte en carrera Inactiva" in res_fail_post.json()["detail"]

        # 7. Desactivar Cohorte
        res_cohorte_inact = await ac.patch(f"/api/v1/admin/cohortes/{cohorte_id}", json={"estado": "Inactiva"})
        assert res_cohorte_inact.status_code == 200
        assert res_cohorte_inact.json()["estado"] == "Inactiva"

        # 8. Intentar activar la cohorte desactivada mientras la carrera sigue inactiva -> debe dar 400
        res_cohorte_react = await ac.patch(f"/api/v1/admin/cohortes/{cohorte_id}", json={"estado": "Activa"})
        assert res_cohorte_react.status_code == 400
        assert "No se puede activar una cohorte cuya carrera está Inactiva" in res_cohorte_react.json()["detail"]

    app.dependency_overrides.clear()
