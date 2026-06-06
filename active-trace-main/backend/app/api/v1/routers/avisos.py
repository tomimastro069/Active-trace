from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.schemas.aviso import AvisoResponse, AvisoCreate, AcknowledgmentAvisoCreate, AcknowledgmentAvisoResponse
from app.services.aviso import AvisoService
from app.repositories.aviso import AvisoRepository
from app.core.dependencies import get_db, get_current_user, require_permission
from app.schemas.auth import CurrentUser
from app.repositories.asignacion import AsignacionRepository
from app.models.asignacion import Asignacion

router = APIRouter()

@router.post("/", response_model=AvisoResponse, status_code=status.HTTP_201_CREATED)
async def crear_aviso(
    data: AvisoCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_permission("avisos:publicar"))
):
    repo = AvisoRepository(db, user.tenant_id)
    service = AvisoService(repo)
    permisos = ["avisos:publicar"]
    try:
        return await service.crear_aviso(user.tenant_id, user.id, permisos, data)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get("/activos", response_model=List[AvisoResponse])
async def obtener_avisos_activos(
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    repo = AvisoRepository(db, user.tenant_id)
    asig_repo = AsignacionRepository(Asignacion, db, user.tenant_id)
    
    asignaciones_raw = await asig_repo.list_assignments(usuario_id=user.id)
    asignaciones_dict = []
    
    roles_activos = await asig_repo.get_active_roles(user.id)
    for r in roles_activos:
        asignaciones_dict.append({"rol": r})
        
    for a in asignaciones_raw:
        asignaciones_dict.append({
            "materia_id": a.materia_id,
            "cohorte_id": a.cohorte_id,
        })

    return await repo.obtener_activos_para_usuario(user.tenant_id, user.id, asignaciones_dict)

@router.post("/ack", status_code=status.HTTP_200_OK)
async def acusar_recibo(
    data: AcknowledgmentAvisoCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    repo = AvisoRepository(db, user.tenant_id)
    service = AvisoService(repo)
    await service.acusar_recibo(user.tenant_id, data.aviso_id, user.id)
    return {"status": "ok"}
