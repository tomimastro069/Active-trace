from uuid import UUID
from typing import List
from app.repositories.aviso import AvisoRepository
from app.schemas.aviso import AvisoCreate
from app.models.aviso import Aviso

class AvisoService:
    def __init__(self, repository: AvisoRepository):
        self.repository = repository
        
    async def crear_aviso(
        self,
        tenant_id: UUID,
        usuario_id: UUID,
        permisos_usuario: List[str],
        data: AvisoCreate
    ) -> Aviso:
        if "avisos:publicar" not in permisos_usuario:
            raise PermissionError("El usuario no tiene permisos para publicar avisos.")
            
        aviso = Aviso(
            tenant_id=tenant_id,
            **data.model_dump()
        )
        return await self.repository.create(aviso)

    async def acusar_recibo(self, tenant_id: UUID, aviso_id: UUID, usuario_id: UUID):
        return await self.repository.registrar_acuse(tenant_id, aviso_id, usuario_id)
