from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.models.evaluacion import Evaluacion, ReservaEvaluacion, EstadoReservaEnum
from app.schemas.evaluacion import ReservaCreate

class CRUDEvaluacion:
    def __init__(self, db: AsyncSession, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id

    async def reservar_evaluacion(self, reserva_in: ReservaCreate) -> ReservaEvaluacion:
        # 1. Lock the Evaluacion row for update
        stmt = select(Evaluacion).where(
            Evaluacion.id == reserva_in.evaluacion_id,
            Evaluacion.tenant_id == self.tenant_id
        ).with_for_update()
        result = await self.db.execute(stmt)
        evaluacion = result.scalar_one_or_none()

        if not evaluacion:
            raise ValueError("Evaluación no encontrada")

        # 2. Check current active reservations
        stmt_count = select(func.count(ReservaEvaluacion.id)).where(
            ReservaEvaluacion.evaluacion_id == evaluacion.id,
            ReservaEvaluacion.estado == EstadoReservaEnum.ACTIVA
        )
        count_result = await self.db.execute(stmt_count)
        current_reservations = count_result.scalar_one()

        # 3. Verify cupos
        if current_reservations >= evaluacion.cupos_totales:
            raise ValueError("No hay cupos disponibles")

        # 4. Check if student already has a reservation
        stmt_dup = select(ReservaEvaluacion).where(
            ReservaEvaluacion.evaluacion_id == evaluacion.id,
            ReservaEvaluacion.alumno_id == reserva_in.alumno_id,
            ReservaEvaluacion.estado == EstadoReservaEnum.ACTIVA
        )
        dup_result = await self.db.execute(stmt_dup)
        if dup_result.scalar_one_or_none():
            raise ValueError("El alumno ya tiene una reserva activa")

        # 5. Create reservation
        reserva = ReservaEvaluacion(
            tenant_id=self.tenant_id,
            evaluacion_id=reserva_in.evaluacion_id,
            alumno_id=reserva_in.alumno_id,
            fecha_hora=reserva_in.fecha_hora,
            estado=EstadoReservaEnum.ACTIVA
        )
        self.db.add(reserva)
        
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("El alumno ya tiene una reserva activa")

        return reserva
