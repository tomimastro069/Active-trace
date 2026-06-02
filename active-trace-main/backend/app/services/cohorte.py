from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cohorte import Cohorte
from app.repositories.cohorte import CohorteRepository
from app.repositories.carrera import CarreraRepository
from app.schemas.cohorte import CohorteCreate, CohorteUpdate
from app.services.audit import AuditService

class CohorteService:
    def __init__(self, db: AsyncSession, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = CohorteRepository(db, tenant_id)
        self.carrera_repo = CarreraRepository(db, tenant_id)
        self.audit_service = AuditService(db, tenant_id)

    async def create_cohorte(self, schema: CohorteCreate, actor_id: UUID) -> Cohorte:
        # Verificar estado de la carrera
        carrera = await self.carrera_repo.get_by_id(schema.carrera_id)
        if not carrera:
            raise ValueError("No se puede crear cohorte en carrera Inactiva o inexistente.")
        if carrera.estado == "Inactiva":
            raise ValueError("No se puede crear cohorte en carrera Inactiva o inexistente.")

        # Verificar unicidad (carrera_id, nombre) dentro del tenant
        existing = await self.repo.get_by_carrera_y_nombre(schema.carrera_id, schema.nombre)
        if existing:
            raise ValueError(f"Ya existe una cohorte con el nombre '{schema.nombre}' para esta carrera.")

        cohorte = Cohorte(
            carrera_id=schema.carrera_id,
            nombre=schema.nombre,
            anio=schema.anio,
            vig_desde=schema.vig_desde,
            vig_hasta=schema.vig_hasta,
            estado=schema.estado or "Activa"
        )
        cohorte = await self.repo.create(cohorte)
        await self.db.flush()

        # Loguear en auditoría
        await self.audit_service.log_action(
            actor_id=actor_id,
            accion="COHORTE_CREAR",
            detalle={
                "id": str(cohorte.id),
                "carrera_id": str(cohorte.carrera_id),
                "nombre": cohorte.nombre,
                "anio": cohorte.anio
            }
        )
        return cohorte

    async def update_cohorte(self, cohorte_id: UUID, schema: CohorteUpdate, actor_id: UUID) -> Cohorte:
        cohorte = await self.repo.get_by_id(cohorte_id)
        if not cohorte:
            raise ValueError("La cohorte no existe o pertenece a otro tenant.")

        cambio_estado = False
        detalle_cambio = {}

        # Si cambia el nombre, validar unicidad
        nueva_carrera_id = cohorte.carrera_id
        nuevo_nombre = schema.nombre if schema.nombre is not None else cohorte.nombre

        if schema.nombre is not None and schema.nombre != cohorte.nombre:
            existing = await self.repo.get_by_carrera_y_nombre(nueva_carrera_id, nuevo_nombre)
            if existing and existing.id != cohorte.id:
                raise ValueError(f"Ya existe una cohorte con el nombre '{nuevo_nombre}' para esta carrera.")

        # Guardar valores para el log de auditoría
        if schema.nombre is not None and schema.nombre != cohorte.nombre:
            detalle_cambio["nombre_antiguo"] = cohorte.nombre
            detalle_cambio["nombre_nuevo"] = schema.nombre
            cohorte.nombre = schema.nombre

        if schema.anio is not None and schema.anio != cohorte.anio:
            detalle_cambio["anio_antiguo"] = cohorte.anio
            detalle_cambio["anio_nuevo"] = schema.anio
            cohorte.anio = schema.anio

        if schema.vig_desde is not None and schema.vig_desde != cohorte.vig_desde:
            detalle_cambio["vig_desde_antiguo"] = str(cohorte.vig_desde)
            detalle_cambio["vig_desde_nuevo"] = str(schema.vig_desde)
            cohorte.vig_desde = schema.vig_desde

        if schema.vig_hasta is not None and schema.vig_hasta != cohorte.vig_hasta:
            detalle_cambio["vig_hasta_antiguo"] = str(cohorte.vig_hasta) if cohorte.vig_hasta else None
            detalle_cambio["vig_hasta_nuevo"] = str(schema.vig_hasta)
            cohorte.vig_hasta = schema.vig_hasta

        if schema.estado is not None and schema.estado != cohorte.estado:
            if schema.estado not in ["Activa", "Inactiva"]:
                raise ValueError("El estado debe ser 'Activa' o 'Inactiva'.")
            
            # Si se quiere activar, verificar que la carrera no esté Inactiva
            if schema.estado == "Activa":
                carrera = await self.carrera_repo.get_by_id(nueva_carrera_id)
                if not carrera or carrera.estado == "Inactiva":
                    raise ValueError("No se puede activar una cohorte cuya carrera está Inactiva o inexistente.")

            detalle_cambio["estado_antiguo"] = cohorte.estado
            detalle_cambio["estado_nuevo"] = schema.estado
            cohorte.estado = schema.estado
            cambio_estado = True

        if not detalle_cambio:
            return cohorte

        cohorte = await self.repo.update(cohorte)
        await self.db.flush()

        # Loguear en auditoría
        if cambio_estado:
            await self.audit_service.log_action(
                actor_id=actor_id,
                accion="COHORTE_ESTADO_CAMBIAR",
                detalle={"id": str(cohorte.id), **detalle_cambio}
            )
        else:
            await self.audit_service.log_action(
                actor_id=actor_id,
                accion="COHORTE_MODIFICAR",
                detalle={"id": str(cohorte.id), **detalle_cambio}
            )

        return cohorte

    async def get_cohorte(self, cohorte_id: UUID) -> Optional[Cohorte]:
        return await self.repo.get_by_id(cohorte_id)

    async def list_cohortes(
        self,
        carrera_id: Optional[UUID] = None,
        estado: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cohorte]:
        return await self.repo.list_cohortes(carrera_id=carrera_id, estado=estado, skip=skip, limit=limit)
