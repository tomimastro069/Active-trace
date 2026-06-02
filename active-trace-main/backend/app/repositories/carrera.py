from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, and_
from app.repositories.base import BaseRepository
from app.models.carrera import Carrera

class CarreraRepository(BaseRepository[Carrera]):
    def __init__(self, session, tenant_id: UUID):
        super().__init__(Carrera, session, tenant_id)

    async def get_by_codigo(self, codigo: str) -> Optional[Carrera]:
        """
        Busca una carrera por su código dentro del tenant actual.
        """
        query = select(self.model).where(self.model.codigo == codigo)
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_carreras(
        self,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Carrera]:
        """
        Lista las carreras del tenant actual, con filtro opcional por estado.
        """
        query = select(self.model)
        if estado:
            query = query.where(self.model.estado == estado)
        query = self._apply_tenant_scope(query)
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
