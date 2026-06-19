from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from uuid import UUID
from typing import List

from app.models.padron import EntradaPadron, VersionPadron
from app.models.materia import Materia
from app.models.cohorte import Cohorte
from app.models.calificacion import Calificacion
from app.schemas.alumno import AlumnoMateriaResponse, AlumnoProgresoResponse, AlumnoActividad

class AlumnoService:
    def __init__(self, db: AsyncSession, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id

    async def get_mis_materias(self, usuario_id: UUID) -> List[AlumnoMateriaResponse]:
        stmt = (
            select(EntradaPadron, VersionPadron, Materia, Cohorte)
            .join(VersionPadron, EntradaPadron.version_id == VersionPadron.id)
            .join(Materia, VersionPadron.materia_id == Materia.id)
            .join(Cohorte, VersionPadron.cohorte_id == Cohorte.id)
            .where(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.usuario_id == usuario_id,
                VersionPadron.activa == True,
                EntradaPadron.deleted_at.is_(None),
                VersionPadron.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        resp = []
        for entrada, version, materia, cohorte in rows:
            stmt_total = select(func.count(func.distinct(Calificacion.actividad))).where(
                Calificacion.materia_id == materia.id,
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.deleted_at.is_(None)
            )
            total_acts = await self.db.scalar(stmt_total) or 0

            stmt_student = select(func.count(Calificacion.id)).where(
                Calificacion.entrada_padron_id == entrada.id,
                Calificacion.materia_id == materia.id,
                Calificacion.tenant_id == self.tenant_id,
                Calificacion.deleted_at.is_(None)
            )
            student_acts = await self.db.scalar(stmt_student) or 0

            progreso = (student_acts / total_acts * 100) if total_acts > 0 else 0.0

            resp.append(AlumnoMateriaResponse(
                materia_id=materia.id,
                materia_nombre=materia.nombre,
                materia_codigo=materia.codigo,
                cohorte_id=cohorte.id,
                cohorte_nombre=cohorte.nombre,
                porcentaje_progreso=progreso
            ))
        return resp

    async def get_mi_progreso(self, usuario_id: UUID, materia_id: UUID) -> AlumnoProgresoResponse:
        stmt = (
            select(EntradaPadron, VersionPadron)
            .join(VersionPadron, EntradaPadron.version_id == VersionPadron.id)
            .where(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.usuario_id == usuario_id,
                VersionPadron.materia_id == materia_id,
                VersionPadron.activa == True,
                EntradaPadron.deleted_at.is_(None),
                VersionPadron.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if not row:
            raise ValueError("No estás inscripto en esta materia.")
        entrada, version = row

        stmt_calif = select(Calificacion).where(
            Calificacion.entrada_padron_id == entrada.id,
            Calificacion.materia_id == materia_id,
            Calificacion.tenant_id == self.tenant_id,
            Calificacion.deleted_at.is_(None)
        )
        calif_res = await self.db.execute(stmt_calif)
        calificaciones = calif_res.scalars().all()

        actividades = [
            AlumnoActividad(
                actividad=c.actividad,
                nota_numerica=c.nota_numerica,
                nota_textual=c.nota_textual,
                aprobado=c.aprobado,
                finalizado=c.finalizado,
                origen=c.origen
            ) for c in calificaciones
        ]

        stmt_total = select(func.count(func.distinct(Calificacion.actividad))).where(
            Calificacion.materia_id == materia_id,
            Calificacion.tenant_id == self.tenant_id,
            Calificacion.deleted_at.is_(None)
        )
        total_acts = await self.db.scalar(stmt_total) or 0
        student_acts = len(actividades)
        progreso = (student_acts / total_acts * 100) if total_acts > 0 else 0.0

        return AlumnoProgresoResponse(
            materia_id=materia_id,
            cohorte_id=version.cohorte_id,
            actividades=actividades,
            porcentaje_progreso=progreso
        )
