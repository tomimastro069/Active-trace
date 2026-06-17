from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.usuario import Usuario
from app.repositories.usuario import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.services.audit import AuditService
from sqlalchemy import func
from app.core.security import generate_email_hash, hash_password

class UsuarioService:
    def __init__(self, db: AsyncSession, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = UsuarioRepository(Usuario, db, tenant_id)
        self.audit_service = AuditService(db, tenant_id)

    def to_response(self, user: Usuario, mask_pii: bool = True) -> UsuarioResponse:
        """
        Convierte un Usuario a UsuarioResponse enmascarando los campos PII si se requiere.
        """
        dni = user.dni
        cuil = user.cuil
        cbu = user.cbu
        alias_cbu = user.alias_cbu

        if mask_pii:
            dni = f"*****{user.dni[-4:]}" if user.dni and len(user.dni) >= 4 else ("*****" if user.dni else None)
            cuil = f"*****{user.cuil[-4:]}" if user.cuil and len(user.cuil) >= 4 else ("*****" if user.cuil else None)
            cbu = f"*****{user.cbu[-4:]}" if user.cbu and len(user.cbu) >= 4 else ("*****" if user.cbu else None)
            alias_cbu = f"*****{user.alias_cbu[-4:]}" if user.alias_cbu and len(user.alias_cbu) >= 4 else ("*****" if user.alias_cbu else None)

        return UsuarioResponse(
            id=user.id,
            tenant_id=user.tenant_id,
            email=user.email,
            nombre=user.nombre,
            apellidos=user.apellidos,
            estado=user.estado,
            dni=dni,
            cuil=cuil,
            cbu=cbu,
            alias_cbu=alias_cbu,
            banco=user.banco,
            regional=user.regional,
            legajo=user.legajo,
            legajo_profesional=user.legajo_profesional,
            facturador=user.facturador,
            modalidad_cobro=user.modalidad_cobro,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    async def create_usuario(self, schema: UsuarioCreate, actor_id: UUID) -> Usuario:
        # Generar hash determinista del email
        email_hash = generate_email_hash(schema.email)
        
        # Validar si el email ya existe en este tenant
        existing = await self.repo.get_by_email_hash(email_hash)
        if existing:
            raise ValueError(f"Ya existe un usuario con el email '{schema.email}' en este tenant.")

        # Cifrar password
        hashed_pwd = hash_password(schema.password)

        usuario = Usuario(
            email=schema.email,
            email_hash=email_hash,
            hashed_password=hashed_pwd,
            estado=schema.estado or "Activo",
            nombre=schema.nombre,
            apellidos=schema.apellidos,
            dni=schema.dni,
            cuil=schema.cuil,
            cbu=schema.cbu,
            alias_cbu=schema.alias_cbu,
            banco=schema.banco,
            regional=schema.regional,
            legajo=schema.legajo,
            legajo_profesional=schema.legajo_profesional,
            facturador=schema.facturador or False,
            modalidad_cobro=schema.modalidad_cobro
        )

        usuario = await self.repo.create(usuario)
        await self.db.flush()

        # Loguear en auditoría
        await self.audit_service.log_action(
            actor_id=actor_id,
            accion="USUARIO_CREAR",
            detalle={"id": str(usuario.id), "email_hash": email_hash}
        )
        return usuario

    async def update_usuario(self, usuario_id: UUID, schema: UsuarioUpdate, actor_id: UUID) -> Usuario:
        usuario = await self.repo.get_by_id(usuario_id)
        if not usuario:
            raise ValueError("El usuario no existe o pertenece a otro tenant.")

        detalle_cambio = {}

        # Mapear cambios
        updatable_fields = [
            "nombre", "apellidos", "dni", "cuil", "cbu", "alias_cbu",
            "banco", "regional", "legajo", "legajo_profesional", "facturador", "modalidad_cobro"
        ]

        for field in updatable_fields:
            val = getattr(schema, field)
            if val is not None:
                old_val = getattr(usuario, field)
                if val != old_val:
                    # No registrar el valor anterior en texto plano para PII en la auditoría
                    if field in ["dni", "cuil", "cbu", "alias_cbu"]:
                        detalle_cambio[field] = "MODIFICADO"
                    else:
                        detalle_cambio[f"{field}_antiguo"] = old_val
                        detalle_cambio[f"{field}_nuevo"] = val
                    setattr(usuario, field, val)

        if schema.estado is not None and schema.estado != usuario.estado:
            if schema.estado not in ["Activo", "Inactivo"]:
                raise ValueError("El estado debe ser 'Activa' o 'Inactiva'.")
            detalle_cambio["estado_antiguo"] = usuario.estado
            detalle_cambio["estado_nuevo"] = schema.estado
            usuario.estado = schema.estado

        if not detalle_cambio:
            return usuario

        usuario = await self.repo.update(usuario)
        await self.db.flush()

        # Loguear en auditoría
        await self.audit_service.log_action(
            actor_id=actor_id,
            accion="USUARIO_MODIFICAR",
            detalle={"id": str(usuario.id), **detalle_cambio}
        )

        return usuario

    async def get_usuario(self, usuario_id: UUID) -> Optional[Usuario]:
        return await self.repo.get_by_id(usuario_id)

    async def list_usuarios(self, skip: int = 0, limit: int = 100) -> List[UsuarioResponse]:
        # Fetch users
        users = await self.repo.list_all(skip=skip, limit=limit)
        # Load role names for each user (first active assignment)
        from sqlalchemy import select
        from app.models.asignacion import Asignacion
        from app.models.rol import Rol
        result = []
        for user in users:
            # Try to get active assignment (current date within validity)
            active_stmt = select(Asignacion.rol_id).where(
                Asignacion.usuario_id == user.id,
                Asignacion.desde <= func.now(),
                (Asignacion.hasta == None) | (Asignacion.hasta >= func.now())
            ).order_by(Asignacion.desde.desc()).limit(1)
            active_row = await self.db.execute(active_stmt)
            role_id = active_row.scalar_one_or_none()
            role_name = None
            if role_id:
                role = await self.db.get(Rol, role_id)
                role_name = role.nombre if role else None
            # Fallback: most recent assignment regardless of dates
            if not role_name:
                fallback_stmt = select(Asignacion.rol_id).where(
                    Asignacion.usuario_id == user.id
                ).order_by(Asignacion.desde.desc()).limit(1)
                fallback_row = await self.db.execute(fallback_stmt)
                fallback_role_id = fallback_row.scalar_one_or_none()
                if fallback_role_id:
                    fallback_role = await self.db.get(Rol, fallback_role_id)
                    role_name = fallback_role.nombre if fallback_role else None
            # Convert to response, injecting role name
            response = self.to_response(user, mask_pii=True)
            response.role_nombre = role_name
            result.append(response)
        return result
