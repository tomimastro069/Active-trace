from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, and_
from app.repositories.base import BaseRepository
from app.models.padron import VersionPadron, EntradaPadron

class PadronRepository(BaseRepository[VersionPadron]):
    def __init__(self, session, tenant_id: UUID):
        super().__init__(VersionPadron, session, tenant_id)

    async def get_active_version(self, materia_id: UUID, cohorte_id: UUID) -> Optional[VersionPadron]:
        """
        Retrieves the current active version of the padron for a specific Materia and Cohorte.
        """
        query = select(self.model).where(
            self.model.materia_id == materia_id,
            self.model.cohorte_id == cohorte_id,
            self.model.activa == True
        )
        query = self._apply_tenant_scope(query)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def desactivar_versiones_activas(self, materia_id: UUID, cohorte_id: UUID) -> int:
        """
        Deactivates all currently active versions of the padron for the specified Materia and Cohorte.
        Returns the number of rows updated.
        """
        stmt = (
            update(self.model)
            .where(
                self.model.tenant_id == self.tenant_id,
                self.model.materia_id == materia_id,
                self.model.cohorte_id == cohorte_id,
                self.model.activa == True,
                self.model.deleted_at.is_(None)
            )
            .values(activa=False, updated_at=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def crear_version_con_entradas(
        self,
        materia_id: UUID,
        cohorte_id: UUID,
        entradas_data: List[dict]
    ) -> VersionPadron:
        """
        Atomically deactivates any existing active version, creates a new active VersionPadron,
        and inserts the list of student entries. All operations run within the session transaction.
        """
        # 1. Deactivate existing active version
        await self.desactivar_versiones_activas(materia_id, cohorte_id)

        # 2. Create the new VersionPadron (marked as active)
        new_version = VersionPadron(
            tenant_id=self.tenant_id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            activa=True
        )
        self.session.add(new_version)
        await self.session.flush()  # Generates new_version.id

        # 3. Instantiate and batch insert the EntradaPadron records
        db_entries = []
        for data in entradas_data:
            entry = EntradaPadron(
                tenant_id=self.tenant_id,
                version_id=new_version.id,
                usuario_id=data.get('usuario_id'),
                email=data['email'],  # This will trigger hash calculation and encryption
                nombre=data['nombre'],
                apellidos=data['apellidos'],
                comision=data.get('comision'),
                regional=data.get('regional')
            )
            db_entries.append(entry)

        if db_entries:
            self.session.add_all(db_entries)
            await self.session.flush()

        return new_version

    async def get_entradas_by_version(self, version_id: UUID) -> List[EntradaPadron]:
        """
        Retrieves all student entries belonging to a specific padron version.
        """
        query = select(EntradaPadron).where(EntradaPadron.version_id == version_id)
        # Apply tenant scope manually since EntradaPadron is a different model
        if self.tenant_id is None:
            raise ValueError("tenant_id is None. Cannot execute query without tenant scope.")
        query = query.where(
            and_(
                EntradaPadron.tenant_id == self.tenant_id,
                EntradaPadron.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()
