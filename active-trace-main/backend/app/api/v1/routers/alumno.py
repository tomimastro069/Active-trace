from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from app.core.dependencies import get_db, get_current_user
from app.schemas.auth import CurrentUser
from app.schemas.alumno import AlumnoMateriaResponse, AlumnoProgresoResponse
from app.services.alumno import AlumnoService

router = APIRouter(prefix="/alumno", tags=["alumno"])

def require_alumno(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if "ALUMNO" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol ALUMNO"
        )
    return current_user

@router.get("/materias", response_model=List[AlumnoMateriaResponse])
async def list_mis_materias(
    current_user: CurrentUser = Depends(require_alumno),
    db: AsyncSession = Depends(get_db)
):
    service = AlumnoService(db, current_user.tenant_id)
    return await service.get_mis_materias(current_user.id)

@router.get("/materias/{materia_id}/progreso", response_model=AlumnoProgresoResponse)
async def get_mi_progreso(
    materia_id: UUID,
    current_user: CurrentUser = Depends(require_alumno),
    db: AsyncSession = Depends(get_db)
):
    service = AlumnoService(db, current_user.tenant_id)
    try:
        return await service.get_mi_progreso(current_user.id, materia_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
