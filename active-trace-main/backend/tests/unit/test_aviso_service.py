import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, timedelta
from app.services.aviso import AvisoService
from app.models.aviso import AlcanceEnum
from app.schemas.aviso import AvisoCreate

@pytest.fixture
def repo_mock():
    return AsyncMock()

@pytest.fixture
def service(repo_mock):
    return AvisoService(repo_mock)

@pytest.mark.asyncio
async def test_crear_aviso_sin_permiso(service, repo_mock):
    # Setup
    tenant_id = uuid4()
    usuario_id = uuid4()
    
    # Usuario no tiene permiso "avisos:publicar"
    permisos_usuario = ["comunicaciones:leer"]
    
    aviso_data = AvisoCreate(
        alcance=AlcanceEnum.GLOBAL,
        severidad="INFO",
        titulo="Test",
        cuerpo="Cuerpo",
        inicio_en=datetime.utcnow(),
        fin_en=datetime.utcnow() + timedelta(days=1),
        orden=0,
        activo=True,
        requiere_ack=False
    )
    
    # Action & Assert
    with pytest.raises(PermissionError):
        await service.crear_aviso(tenant_id, usuario_id, permisos_usuario, aviso_data)

@pytest.mark.asyncio
async def test_acusar_recibo(service, repo_mock):
    tenant_id = uuid4()
    usuario_id = uuid4()
    aviso_id = uuid4()
    
    ack_mock = AsyncMock()
    repo_mock.registrar_acuse.return_value = ack_mock
    
    result = await service.acusar_recibo(tenant_id, aviso_id, usuario_id)
    
    repo_mock.registrar_acuse.assert_called_once_with(tenant_id, aviso_id, usuario_id)
    assert result == ack_mock
