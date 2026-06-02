from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.materia import Materia

class MateriaRepository(BaseRepository[Materia]):
    def __init__(self, session, tenant_id: UUID):
        super().__init__(Materia, session, tenant_id)

    async def get_by_codigo(self, codigo: str) -> Optional[Materia]:
        """
        Busca una materia por su código dentro del tenant actual.
        """
        query = select(self.model).where(self.model.codigo == codigo)
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_materias(
        self,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Materia]:
        """
        Lista las materias del tenant actual, con filtro opcional por estado.
        """
        query = select(self.model)
        if estado:
            query = query.where(self.model.estado == estado)
        query = self._apply_tenant_scope(query)
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
