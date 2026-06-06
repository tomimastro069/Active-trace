import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import patch, AsyncMock

from app.main import app
from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import CurrentUser

@pytest.mark.asyncio
async def test_crear_y_obtener_avisos(db_session):
    tenant_id = uuid4()
    docente_id = uuid4()
    alumno_id = uuid4()
    
    docente_user = CurrentUser(id=docente_id, tenant_id=tenant_id, email="docente@test.com", roles=["docente"])
    alumno_user = CurrentUser(id=alumno_id, tenant_id=tenant_id, email="alumno@test.com", roles=["alumno"])
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        
        app.dependency_overrides[get_db] = lambda: db_session
        
        with patch('app.repositories.asignacion.AsignacionRepository.get_effective_permissions', new_callable=AsyncMock) as mock_perms:
            with patch('app.repositories.asignacion.AsignacionRepository.list_assignments', new_callable=AsyncMock) as mock_list:
                with patch('app.repositories.asignacion.AsignacionRepository.get_active_roles', new_callable=AsyncMock) as mock_roles:
                    
                    mock_perms.return_value = ["avisos:publicar"]
                    mock_list.return_value = []
                    mock_roles.return_value = []
                    
                    # 1. Crear Aviso como Docente
                    async def override_docente(): return docente_user
                    app.dependency_overrides[get_current_user] = override_docente
                    
                    payload = {
                        "alcance": "Global",
                        "titulo": "Aviso Integracion",
                        "cuerpo": "Prueba",
                        "severidad": "INFO",
                        "inicio_en": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                        "fin_en": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                        "orden": 0,
                        "activo": True,
                        "requiere_ack": True
                    }
                    
                    resp_post = await client.post("/api/v1/avisos/", json=payload, headers={"Authorization": "Bearer fake"})
                    assert resp_post.status_code == 201
                    aviso_creado = resp_post.json()
                    
                    # 2. Obtener Avisos como Alumno
                    async def override_alumno(): return alumno_user
                    app.dependency_overrides[get_current_user] = override_alumno
                    
                    resp_get = await client.get("/api/v1/avisos/activos", headers={"Authorization": "Bearer fake"})
                    assert resp_get.status_code == 200
                    avisos = resp_get.json()
                    assert any(a["id"] == aviso_creado["id"] for a in avisos)
                    
                    # 3. Acusar recibo
                    ack_payload = {"aviso_id": aviso_creado["id"]}
                    resp_ack = await client.post("/api/v1/avisos/ack", json=ack_payload, headers={"Authorization": "Bearer fake"})
                    assert resp_ack.status_code == 200
                    
                    # 4. Obtener avisos y verificar que ya no está (porque requiere_ack y ya se acusó)
                    resp_get_after = await client.get("/api/v1/avisos/activos", headers={"Authorization": "Bearer fake"})
                    assert resp_get_after.status_code == 200
                    avisos_after = resp_get_after.json()
                    assert not any(a["id"] == aviso_creado["id"] for a in avisos_after)
                    
        app.dependency_overrides.clear()
