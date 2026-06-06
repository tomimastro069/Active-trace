from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.aviso import Aviso, AlcanceEnum, AcknowledgmentAviso

class AvisoRepository(BaseRepository[Aviso]):
    def __init__(self, session: AsyncSession, tenant_id: UUID):
        super().__init__(Aviso, session, tenant_id)
        
    async def obtener_activos_para_usuario(
        self,
        tenant_id: UUID,
        usuario_id: UUID,
        asignaciones: List[Dict[str, Any]]
    ) -> List[Aviso]:
        now = datetime.utcnow()
        condiciones = [Aviso.alcance == AlcanceEnum.GLOBAL]
        
        for asig in asignaciones:
            if asig.get("materia_id"):
                condiciones.append(
                    and_(
                        Aviso.alcance == AlcanceEnum.POR_MATERIA,
                        Aviso.materia_id == asig["materia_id"]
                    )
                )
            if asig.get("cohorte_id"):
                condiciones.append(
                    and_(
                        Aviso.alcance == AlcanceEnum.POR_COHORTE,
                        Aviso.cohorte_id == asig["cohorte_id"]
                    )
                )
            if asig.get("rol"):
                condiciones.append(
                    and_(
                        Aviso.alcance == AlcanceEnum.POR_ROL,
                        Aviso.rol_destino == asig["rol"]
                    )
                )

        stmt = (
            select(Aviso)
            .outerjoin(
                AcknowledgmentAviso,
                and_(
                    AcknowledgmentAviso.aviso_id == Aviso.id,
                    AcknowledgmentAviso.usuario_id == usuario_id
                )
            )
            .where(
                Aviso.tenant_id == tenant_id,
                Aviso.activo == True,
                Aviso.inicio_en <= now,
                Aviso.fin_en >= now,
                or_(*condiciones),
                or_(
                    Aviso.requiere_ack == False,
                    and_(
                        Aviso.requiere_ack == True,
                        AcknowledgmentAviso.id.is_(None)
                    )
                )
            )
            .order_by(Aviso.orden.asc(), Aviso.created_at.desc())
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def registrar_acuse(self, tenant_id: UUID, aviso_id: UUID, usuario_id: UUID) -> AcknowledgmentAviso:
        ack = AcknowledgmentAviso(
            tenant_id=tenant_id,
            aviso_id=aviso_id,
            usuario_id=usuario_id
        )
        self.session.add(ack)
        await self.session.commit()
        await self.session.refresh(ack)
        return ack
