from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.materia import MateriaCreate, MateriaUpdate, MateriaResponse
from app.services.materia import MateriaService

router = APIRouter(prefix="/admin/materias", tags=["materias"])

@router.post("/", response_model=MateriaResponse, status_code=status.HTTP_201_CREATED)
async def create_materia(
    payload: MateriaCreate,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = MateriaService(db, current_user.tenant_id)
    try:
        materia = await service.create_materia(payload, actor_id=current_user.id)
        await db.commit()
        return materia
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[MateriaResponse])
async def list_materias(
    estado: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = MateriaService(db, current_user.tenant_id)
    return await service.list_materias(estado=estado, skip=skip, limit=limit)

@router.get("/{materia_id}", response_model=MateriaResponse)
async def get_materia(
    materia_id: UUID,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = MateriaService(db, current_user.tenant_id)
    materia = await service.get_materia(materia_id)
    if not materia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La materia no existe o pertenece a otro tenant."
        )
    return materia

@router.patch("/{materia_id}", response_model=MateriaResponse)
async def update_materia(
    materia_id: UUID,
    payload: MateriaUpdate,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = MateriaService(db, current_user.tenant_id)
    try:
        materia = await service.update_materia(materia_id, payload, actor_id=current_user.id)
        await db.commit()
        return materia
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
