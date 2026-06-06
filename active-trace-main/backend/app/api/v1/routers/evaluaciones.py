from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.dependencies import get_db, require_permission, get_current_user
from app.schemas.auth import CurrentUser
from app.models.evaluacion import Evaluacion, EvaluacionTipoEnum, EstadoReservaEnum
from app.schemas.evaluacion import ReservaCreate, ReservaResponse
from app.crud.crud_evaluacion import CRUDEvaluacion
from pydantic import BaseModel, ConfigDict

router = APIRouter(tags=["Evaluaciones"])

class EvaluacionCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    materia_id: UUID
    cohorte_id: UUID
    tipo: EvaluacionTipoEnum
    instancia: str
    dias_disponibles: int = 1
    cupos_totales: int = 10

class EvaluacionResponse(BaseModel):
    id: UUID
    materia_id: UUID
    cohorte_id: UUID
    tipo: EvaluacionTipoEnum
    instancia: str
    dias_disponibles: int
    cupos_totales: int
    
    model_config = ConfigDict(from_attributes=True)

@router.post("/admin/evaluaciones/", response_model=EvaluacionResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluacion(
    eval_in: EvaluacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("encuentros:gestionar"))
):
    evaluacion = Evaluacion(
        tenant_id=current_user.tenant_id,
        materia_id=eval_in.materia_id,
        cohorte_id=eval_in.cohorte_id,
        tipo=eval_in.tipo,
        instancia=eval_in.instancia,
        dias_disponibles=eval_in.dias_disponibles,
        cupos_totales=eval_in.cupos_totales
    )
    db.add(evaluacion)
    await db.commit()
    await db.refresh(evaluacion)
    return evaluacion

@router.post("/reservas/evaluaciones/", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
async def reservar_evaluacion(
    reserva_in: ReservaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    # Only ALUMNO or self reservation
    if str(current_user.id) != str(reserva_in.alumno_id) and "ADMIN" not in current_user.roles:
        raise HTTPException(status_code=403, detail="No puedes reservar para otro alumno")
    
    crud = CRUDEvaluacion(db, current_user.tenant_id)
    try:
        reserva = await crud.reservar_evaluacion(reserva_in)
        await db.commit()
        await db.refresh(reserva)
        return reserva
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
