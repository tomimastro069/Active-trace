from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.cohorte import CohorteCreate, CohorteUpdate, CohorteResponse
from app.services.cohorte import CohorteService

router = APIRouter(prefix="/admin/cohortes", tags=["cohortes"])

@router.post("/", response_model=CohorteResponse, status_code=status.HTTP_201_CREATED)
async def create_cohorte(
    payload: CohorteCreate,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = CohorteService(db, current_user.tenant_id)
    try:
        cohorte = await service.create_cohorte(payload, actor_id=current_user.id)
        await db.commit()
        return cohorte
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[CohorteResponse])
async def list_cohortes(
    carrera_id: Optional[UUID] = None,
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = CohorteService(db, current_user.tenant_id)
    return await service.list_cohortes(carrera_id=carrera_id, estado=estado, skip=skip, limit=limit)

@router.get("/{cohorte_id}", response_model=CohorteResponse)
async def get_cohorte(
    cohorte_id: UUID,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = CohorteService(db, current_user.tenant_id)
    cohorte = await service.get_cohorte(cohorte_id)
    if not cohorte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La cohorte no existe o pertenece a otro tenant."
        )
    return cohorte

@router.patch("/{cohorte_id}", response_model=CohorteResponse)
async def update_cohorte(
    cohorte_id: UUID,
    payload: CohorteUpdate,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = CohorteService(db, current_user.tenant_id)
    try:
        cohorte = await service.update_cohorte(cohorte_id, payload, actor_id=current_user.id)
        await db.commit()
        return cohorte
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
