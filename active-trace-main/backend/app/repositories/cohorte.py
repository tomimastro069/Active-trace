from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_
from app.repositories.base import BaseRepository
from app.models.cohorte import Cohorte

class CohorteRepository(BaseRepository[Cohorte]):
    def __init__(self, session, tenant_id: UUID):
        super().__init__(Cohorte, session, tenant_id)

    async def get_by_carrera_y_nombre(self, carrera_id: UUID, nombre: str) -> Optional[Cohorte]:
        """
        Busca una cohorte por carrera y nombre dentro del tenant actual.
        """
        query = select(self.model).where(
            and_(
                self.model.carrera_id == carrera_id,
                self.model.nombre == nombre
            )
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_cohortes(
        self,
        carrera_id: Optional[UUID] = None,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cohorte]:
        """
        Lista las cohortes del tenant actual, con filtros opcionales por carrera y estado.
        """
        query = select(self.model)
        if carrera_id:
            query = query.where(self.model.carrera_id == carrera_id)
        if estado:
            query = query.where(self.model.estado == estado)
        query = self._apply_tenant_scope(query)
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
