from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.materia import Materia
from app.repositories.materia import MateriaRepository
from app.schemas.materia import MateriaCreate, MateriaUpdate
from app.services.audit import AuditService

class MateriaService:
    def __init__(self, db: AsyncSession, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = MateriaRepository(db, tenant_id)
        self.audit_service = AuditService(db, tenant_id)

    async def create_materia(self, schema: MateriaCreate, actor_id: UUID) -> Materia:
        # Validar unicidad de código dentro del tenant
        existing = await self.repo.get_by_codigo(schema.codigo)
        if existing:
            raise ValueError(f"Ya existe una materia con el código '{schema.codigo}'.")

        materia = Materia(
            codigo=schema.codigo,
            nombre=schema.nombre,
            estado=schema.estado or "Activa"
        )
        materia = await self.repo.create(materia)
        await self.db.flush()

        # Loguear en auditoría
        await self.audit_service.log_action(
            actor_id=actor_id,
            accion="MATERIA_CREAR",
            materia_id=materia.id,
            detalle={"id": str(materia.id), "codigo": materia.codigo, "nombre": materia.nombre}
        )
        return materia

    async def update_materia(self, materia_id: UUID, schema: MateriaUpdate, actor_id: UUID) -> Materia:
        materia = await self.repo.get_by_id(materia_id)
        if not materia:
            raise ValueError("La materia no existe o pertenece a otro tenant.")

        cambio_estado = False
        detalle_cambio = {}

        if schema.nombre is not None and schema.nombre != materia.nombre:
            detalle_cambio["nombre_antiguo"] = materia.nombre
            detalle_cambio["nombre_nuevo"] = schema.nombre
            materia.nombre = schema.nombre

        if schema.estado is not None and schema.estado != materia.estado:
            if schema.estado not in ["Activa", "Inactiva"]:
                raise ValueError("El estado debe ser 'Activa' o 'Inactiva'.")
            detalle_cambio["estado_antiguo"] = materia.estado
            detalle_cambio["estado_nuevo"] = schema.estado
            materia.estado = schema.estado
            cambio_estado = True

        if not detalle_cambio:
            return materia

        materia = await self.repo.update(materia)
        await self.db.flush()

        # Loguear en auditoría
        if cambio_estado:
            await self.audit_service.log_action(
                actor_id=actor_id,
                accion="MATERIA_ESTADO_CAMBIAR",
                materia_id=materia.id,
                detalle={"id": str(materia.id), **detalle_cambio}
            )
        else:
            await self.audit_service.log_action(
                actor_id=actor_id,
                accion="MATERIA_MODIFICAR",
                materia_id=materia.id,
                detalle={"id": str(materia.id), **detalle_cambio}
            )

        return materia

    async def get_materia(self, materia_id: UUID) -> Optional[Materia]:
        return await self.repo.get_by_id(materia_id)

    async def list_materias(
        self,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Materia]:
        return await self.repo.list_materias(estado=estado, skip=skip, limit=limit)
