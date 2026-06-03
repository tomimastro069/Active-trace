from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.materia import MateriaRepository
from app.repositories.cohorte import CohorteRepository
from app.repositories.padron_repository import PadronRepository
from app.repositories.usuario import UsuarioRepository
from app.services.audit import AuditService
from app.schemas.padron import EntradaPadronCreate
from app.models.padron import VersionPadron, EntradaPadron
from app.models.usuario import Usuario
from app.core.security import generate_email_hash

class PadronService:
    def __init__(self, db: AsyncSession, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = PadronRepository(db, tenant_id)
        self.materia_repo = MateriaRepository(db, tenant_id)
        self.cohorte_repo = CohorteRepository(db, tenant_id)
        self.usuario_repo = UsuarioRepository(Usuario, db, tenant_id)
        self.audit_service = AuditService(db, tenant_id)

    async def importar_padron(
        self,
        materia_id: UUID,
        cohorte_id: UUID,
        entradas_schema: List[EntradaPadronCreate],
        actor_id: UUID
    ) -> VersionPadron:
        """
        Validates Materia and Cohorte, performs a performant batch lookup to map
        student emails to registered Usuario accounts, creates a new active version
        of the padron atomically deactivating the previous one, and creates an audit entry.
        """
        # 1. Validar materia activa
        materia = await self.materia_repo.get_by_id(materia_id)
        if not materia or materia.estado == "Inactiva":
            raise ValueError("La materia no existe o está Inactiva.")

        # 2. Validar cohorte activa
        cohorte = await self.cohorte_repo.get_by_id(cohorte_id)
        if not cohorte or cohorte.estado == "Inactiva":
            raise ValueError("La cohorte no existe o está Inactiva.")

        # 3. Performante resolution of usuario_id by batch hashing and lookup
        emails = [e.email for e in entradas_schema]
        email_hashes = [generate_email_hash(email) for email in emails]
        
        # Look up all active registered users with matching email hashes in a single query
        from app.models.usuario import Usuario
        query = select(Usuario).where(
            Usuario.tenant_id == self.tenant_id,
            Usuario.email_hash.in_(email_hashes),
            Usuario.deleted_at.is_(None)
        )
        res = await self.db.execute(query)
        usuarios = res.scalars().all()
        
        # Map email_hash -> usuario_id
        hash_to_user_id = {u.email_hash: u.id for u in usuarios}

        # 4. Prepare data for repository creation
        entradas_data = []
        for e in entradas_schema:
            hashed_email = generate_email_hash(e.email)
            # Override usuario_id if matching user exists locally, otherwise fallback to provided id
            usr_id = hash_to_user_id.get(hashed_email)
            
            entradas_data.append({
                "usuario_id": usr_id or e.usuario_id,
                "email": e.email,
                "nombre": e.nombre,
                "apellidos": e.apellidos,
                "comision": e.comision,
                "regional": e.regional
            })

        # 5. Call repository to deactivate old versions and create the new one atomically
        new_version = await self.repo.crear_version_con_entradas(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            entradas_data=entradas_data
        )

        # 6. Audit action
        await self.audit_service.log_action(
            actor_id=actor_id,
            accion="PADRON_CARGAR",
            materia_id=materia_id,
            detalle={
                "version_id": str(new_version.id),
                "cohorte_id": str(cohorte_id),
                "total_alumnos": len(entradas_schema)
            },
            filas_afectadas=len(entradas_schema)
        )

        return new_version

    async def vaciar_padron(
        self,
        materia_id: UUID,
        cohorte_id: UUID,
        actor_id: UUID
    ) -> None:
        """
        Deactivates the current active padron version for a specific Materia and Cohorte.
        """
        # Validate materia and cohorte exist first
        materia = await self.materia_repo.get_by_id(materia_id)
        if not materia:
            raise ValueError("La materia no existe.")
        
        cohorte = await self.cohorte_repo.get_by_id(cohorte_id)
        if not cohorte:
            raise ValueError("La cohorte no existe.")

        # Deactivate any active version
        deactivated_count = await self.repo.desactivar_versiones_activas(materia_id, cohorte_id)
        
        # Log audit action
        await self.audit_service.log_action(
            actor_id=actor_id,
            accion="PADRON_VACIAR",
            materia_id=materia_id,
            detalle={
                "cohorte_id": str(cohorte_id)
            },
            filas_afectadas=deactivated_count
        )

    async def get_active_version(self, materia_id: UUID, cohorte_id: UUID) -> Optional[VersionPadron]:
        return await self.repo.get_active_version(materia_id, cohorte_id)

    async def get_entradas(self, version_id: UUID) -> List[EntradaPadron]:
        return await self.repo.get_entradas_by_version(version_id)
