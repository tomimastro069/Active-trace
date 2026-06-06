import pytest
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.aviso import Aviso, AlcanceEnum
from app.repositories.aviso import AvisoRepository
from app.models.asignacion import Asignacion

# Fixture para tenant_id
@pytest.fixture
def tenant_id():
    return uuid4()

@pytest.fixture
def repo(db_session: AsyncSession, tenant_id: UUID):
    return AvisoRepository(db_session, tenant_id)

@pytest.mark.asyncio
async def test_obtener_avisos_activos_global(db_session: AsyncSession, repo: AvisoRepository, tenant_id: UUID):
    # Setup
    usuario_id = uuid4()
    
    # Aviso global activo
    aviso_global = Aviso(
        tenant_id=tenant_id,
        alcance=AlcanceEnum.GLOBAL,
        titulo="Global",
        cuerpo="Test Global",
        severidad="INFO",
        inicio_en=datetime.utcnow() - timedelta(days=1),
        fin_en=datetime.utcnow() + timedelta(days=1),
        activo=True
    )
    db_session.add(aviso_global)
    await db_session.commit()
    
    # Action
    # Testing logic that doesn't exist yet (this should fail)
    asignaciones_vacias = []
    avisos = await repo.obtener_activos_para_usuario(
        tenant_id=tenant_id,
        usuario_id=usuario_id,
        asignaciones=asignaciones_vacias
    )
    
    # Assert
    assert len(avisos) == 1
    assert avisos[0].id == aviso_global.id

@pytest.mark.asyncio
async def test_obtener_avisos_activos_materia(db_session: AsyncSession, repo: AvisoRepository, tenant_id: UUID):
    usuario_id = uuid4()
    materia_id = uuid4()
    
    # Aviso materia
    aviso_mat = Aviso(
        tenant_id=tenant_id,
        alcance=AlcanceEnum.POR_MATERIA,
        materia_id=materia_id,
        titulo="Mat",
        cuerpo="Test",
        severidad="INFO",
        inicio_en=datetime.utcnow() - timedelta(days=1),
        fin_en=datetime.utcnow() + timedelta(days=1)
    )
    db_session.add(aviso_mat)
    await db_session.commit()
    
    # No assignments
    avisos_empty = await repo.obtener_activos_para_usuario(
        tenant_id, usuario_id, asignaciones=[]
    )
    assert len(avisos_empty) == 0
    
    # Matching assignment
    avisos_match = await repo.obtener_activos_para_usuario(
        tenant_id, usuario_id, asignaciones=[{"materia_id": materia_id}]
    )
    assert len(avisos_match) == 1
    assert avisos_match[0].id == aviso_mat.id

@pytest.mark.asyncio
async def test_obtener_avisos_activos_filtra_ack(db_session: AsyncSession, repo: AvisoRepository, tenant_id: UUID):
    usuario_id = uuid4()
    
    # Aviso que requiere ack
    aviso_ack = Aviso(
        tenant_id=tenant_id,
        alcance=AlcanceEnum.GLOBAL,
        titulo="Global Ack",
        cuerpo="Test Global Ack",
        severidad="INFO",
        inicio_en=datetime.utcnow() - timedelta(days=1),
        fin_en=datetime.utcnow() + timedelta(days=1),
        activo=True,
        requiere_ack=True
    )
    db_session.add(aviso_ack)
    await db_session.commit()
    
    # Usuario aún no dio acuse, debería aparecer
    avisos_antes = await repo.obtener_activos_para_usuario(tenant_id, usuario_id, [])
    assert len(avisos_antes) == 1
    assert avisos_antes[0].id == aviso_ack.id
    
    # Registrar acuse
    await repo.registrar_acuse(tenant_id, aviso_ack.id, usuario_id)
    
    # Ya no debería aparecer
    avisos_despues = await repo.obtener_activos_para_usuario(tenant_id, usuario_id, [])
    assert len(avisos_despues) == 0
