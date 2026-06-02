from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.carrera import CarreraCreate, CarreraUpdate, CarreraResponse
from app.services.carrera import CarreraService

router = APIRouter(prefix="/admin/carreras", tags=["carreras"])

@router.post("/", response_model=CarreraResponse, status_code=status.HTTP_201_CREATED)
async def create_carrera(
    payload: CarreraCreate,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = CarreraService(db, current_user.tenant_id)
    try:
        carrera = await service.create_carrera(payload, actor_id=current_user.id)
        await db.commit()
        return carrera
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[CarreraResponse])
async def list_carreras(
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = CarreraService(db, current_user.tenant_id)
    return await service.list_carreras(estado=estado, skip=skip, limit=limit)

@router.get("/{carrera_id}", response_model=CarreraResponse)
async def get_carrera(
    carrera_id: UUID,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = CarreraService(db, current_user.tenant_id)
    carrera = await service.get_carrera(carrera_id)
    if not carrera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La carrera no existe o pertenece a otro tenant."
        )
    return carrera

@router.patch("/{carrera_id}", response_model=CarreraResponse)
async def update_carrera(
    carrera_id: UUID,
    payload: CarreraUpdate,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = CarreraService(db, current_user.tenant_id)
    try:
        carrera = await service.update_carrera(carrera_id, payload, actor_id=current_user.id)
        await db.commit()
        return carrera
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
