from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.repositories.audit_log import AuditLogRepository
from app.repositories.asignacion import AsignacionRepository
from app.models.asignacion import Asignacion
from app.schemas.auth import CurrentUser

class AuditService:
    """
    Servicio de Auditoría para registrar acciones significativas en el sistema y proveer métricas.
    """

    def __init__(self, db: AsyncSession, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = AuditLogRepository(AuditLog, db, tenant_id)
        self.asignacion_repo = AsignacionRepository(Asignacion, db, tenant_id)

    async def log_action(
        self,
        actor_id: UUID,
        accion: str,
        impersonado_id: Optional[UUID] = None,
        materia_id: Optional[UUID] = None,
        detalle: Optional[Dict[str, Any]] = None,
        filas_afectadas: Optional[int] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Registra una acción en el log de auditoría.
        """
        log = AuditLog(
            tenant_id=self.tenant_id,
            actor_id=actor_id,
            impersonado_id=impersonado_id,
            materia_id=materia_id,
            accion=accion,
            detalle=detalle,
            filas_afectadas=filas_afectadas,
            ip=ip,
            user_agent=user_agent
        )
        # Usamos el repositorio para crear y persistir el registro
        await self.repo.create(log)
        await self.db.flush()
        return log

    async def _check_access_and_get_materia_filter(
        self,
        current_user: CurrentUser,
        materia_id: Optional[UUID] = None
    ) -> Optional[List[UUID]]:
        """
        Enforces permissions and returns a list of allowed materia_ids if the user has _propio access.
        Returns None if they have global access.
        """
        effective_permissions = await self.asignacion_repo.get_effective_permissions(current_user.id)

        if "auditoria:ver" in effective_permissions:
            # Global access
            return [materia_id] if materia_id else None

        if "auditoria:ver_propio" in effective_permissions:
            # Propio access: restrict to their assigned subjects
            assignments = await self.asignacion_repo.list_assignments(
                usuario_id=current_user.id,
                materia_id=materia_id
            )
            active_materia_ids = [
                a.materia_id for a in assignments if a.estado_vigencia == "Vigente"
            ]

            if materia_id:
                if materia_id not in active_materia_ids:
                    raise ValueError("El usuario no tiene una asignación vigente para la materia especificada.")
                return [materia_id]

            if not active_materia_ids:
                raise ValueError("El usuario no tiene asignaciones vigentes.")

            return active_materia_ids

        raise ValueError("Permisos insuficientes para realizar esta operación.")

    async def get_interaction_metrics(self, current_user: CurrentUser, materia_id: Optional[UUID] = None) -> dict:
        allowed_materia_ids = await self._check_access_and_get_materia_filter(current_user, materia_id)

        def _apply_filters(stmt):
            stmt = stmt.where(AuditLog.tenant_id == self.tenant_id)
            if allowed_materia_ids is not None:
                stmt = stmt.where(AuditLog.materia_id.in_(allowed_materia_ids))
            return stmt

        # 1. Daily activity
        daily_stmt = select(
            func.date(AuditLog.fecha_hora).label("date"),
            func.count(AuditLog.id).label("count")
        )
        daily_stmt = _apply_filters(daily_stmt)
        daily_stmt = daily_stmt.group_by(func.date(AuditLog.fecha_hora)).order_by(func.date(AuditLog.fecha_hora).desc())

        # 2. Teacher communications (status count per teacher)
        comms_stmt = select(
            AuditLog.actor_id.label("teacher_id"),
            AuditLog.accion.label("status"),
            func.count(AuditLog.id).label("count")
        ).where(AuditLog.accion.like('comunicacion%'))
        comms_stmt = _apply_filters(comms_stmt)
        comms_stmt = comms_stmt.group_by(AuditLog.actor_id, AuditLog.accion)

        # 3. Teacher-subject interactions
        ts_stmt = select(
            AuditLog.actor_id.label("teacher_id"),
            AuditLog.materia_id.label("subject_id"),
            func.count(AuditLog.id).label("count")
        )
        ts_stmt = _apply_filters(ts_stmt)
        ts_stmt = ts_stmt.group_by(AuditLog.actor_id, AuditLog.materia_id)

        daily_result = await self.db.execute(daily_stmt)
        comms_result = await self.db.execute(comms_stmt)
        ts_result = await self.db.execute(ts_stmt)

        daily_data = [
            {"date": str(row.date), "count": row.count}
            for row in daily_result.all()
        ]

        comms_data = [
            {"teacher_id": row.teacher_id, "status": row.status, "count": row.count}
            for row in comms_result.all()
        ]

        ts_data = [
            {"teacher_id": row.teacher_id, "subject_id": row.subject_id, "count": row.count}
            for row in ts_result.all()
        ]

        return {
            "daily_activity": daily_data,
            "teacher_communications": comms_data,
            "teacher_subject_interactions": ts_data
        }

    async def get_logs(
        self,
        current_user: CurrentUser,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        materia_id: Optional[UUID] = None,
        actor_id: Optional[UUID] = None,
        limit: int = 200,
        offset: int = 0
    ) -> List[AuditLog]:
        allowed_materia_ids = await self._check_access_and_get_materia_filter(current_user, materia_id)

        stmt = select(AuditLog).where(AuditLog.tenant_id == self.tenant_id)

        if allowed_materia_ids is not None:
            stmt = stmt.where(AuditLog.materia_id.in_(allowed_materia_ids))

        if fecha_desde:
            stmt = stmt.where(AuditLog.fecha_hora >= fecha_desde)
        if fecha_hasta:
            stmt = stmt.where(AuditLog.fecha_hora <= fecha_hasta)
        if actor_id:
            stmt = stmt.where(AuditLog.actor_id == actor_id)

        stmt = stmt.order_by(AuditLog.fecha_hora.desc()).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
