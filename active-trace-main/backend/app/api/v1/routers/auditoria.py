from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.audit import AuditMetricsResponse, AuditLogQuerySchema, AuditLogResponse
from app.services.audit import AuditService

router = APIRouter(tags=["Auditoría"])

@router.get("/interacciones", response_model=AuditMetricsResponse)
async def get_interacciones(
    query: AuditLogQuerySchema = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("auditoria:ver"))
):
    service = AuditService(db, current_user.tenant_id)
    return await service.get_interaction_metrics(
        current_user=current_user,
        materia_id=query.materia_id
    )

@router.get("/logs", response_model=List[AuditLogResponse])
async def get_logs(
    query: AuditLogQuerySchema = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission("auditoria:ver"))
):
    service = AuditService(db, current_user.tenant_id)
    return await service.get_logs(
        current_user=current_user,
        fecha_desde=query.fecha_desde,
        fecha_hasta=query.fecha_hasta,
        materia_id=query.materia_id,
        actor_id=query.actor_id,
        limit=query.limit,
        offset=query.offset
    )

