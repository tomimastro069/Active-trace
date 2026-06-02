from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.carrera import Carrera
from app.repositories.carrera import CarreraRepository
from app.schemas.carrera import CarreraCreate, CarreraUpdate
from app.services.audit import AuditService

class CarreraService:
    def __init__(self, db: AsyncSession, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = CarreraRepository(db, tenant_id)
        self.audit_service = AuditService(db, tenant_id)

    async def create_carrera(self, schema: CarreraCreate, actor_id: UUID) -> Carrera:
        # Validar unicidad de código dentro del tenant
        existing = await self.repo.get_by_codigo(schema.codigo)
        if existing:
            raise ValueError(f"Ya existe una carrera con el código '{schema.codigo}'.")

        carrera = Carrera(
            codigo=schema.codigo,
            nombre=schema.nombre,
            estado=schema.estado or "Activa"
        )
        carrera = await self.repo.create(carrera)
        await self.db.flush()

        # Loguear en auditoría
        await self.audit_service.log_action(
            actor_id=actor_id,
            accion="CARRERA_CREAR",
            detalle={"id": str(carrera.id), "codigo": carrera.codigo, "nombre": carrera.nombre}
        )
        return carrera

    async def update_carrera(self, carrera_id: UUID, schema: CarreraUpdate, actor_id: UUID) -> Carrera:
        carrera = await self.repo.get_by_id(carrera_id)
        if not carrera:
            raise ValueError("La carrera no existe o pertenece a otro tenant.")

        cambio_estado = False
        antiguo_estado = carrera.estado
        detalle_cambio = {}

        if schema.nombre is not None and schema.nombre != carrera.nombre:
            detalle_cambio["nombre_antiguo"] = carrera.nombre
            detalle_cambio["nombre_nuevo"] = schema.nombre
            carrera.nombre = schema.nombre

        if schema.estado is not None and schema.estado != carrera.estado:
            if schema.estado not in ["Activa", "Inactiva"]:
                raise ValueError("El estado debe ser 'Activa' o 'Inactiva'.")
            detalle_cambio["estado_antiguo"] = carrera.estado
            detalle_cambio["estado_nuevo"] = schema.estado
            carrera.estado = schema.estado
            cambio_estado = True

        if not detalle_cambio:
            return carrera

        carrera = await self.repo.update(carrera)
        await self.db.flush()

        # Loguear en auditoría
        if cambio_estado:
            await self.audit_service.log_action(
                actor_id=actor_id,
                accion="CARRERA_ESTADO_CAMBIAR",
                detalle={"id": str(carrera.id), **detalle_cambio}
            )
        else:
            await self.audit_service.log_action(
                actor_id=actor_id,
                accion="CARRERA_MODIFICAR",
                detalle={"id": str(carrera.id), **detalle_cambio}
            )

        return carrera

    async def get_carrera(self, carrera_id: UUID) -> Optional[Carrera]:
        return await self.repo.get_by_id(carrera_id)

    async def list_carreras(
        self,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Carrera]:
        return await self.repo.list_carreras(estado=estado, skip=skip, limit=limit)
