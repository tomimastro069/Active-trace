"""
Seed de desarrollo para Active Trace.

Crea:
  Tenant : Demo University
  Roles  : ADMIN, COORDINADOR, PROFESOR, ALUMNO  (globales y por tenant)
  Usuarios:
    admin@demo.com       / admin1234      → rol ADMIN
    coordinador@demo.com / coord1234      → rol COORDINADOR
    docente@demo.com     / docente1234    → rol PROFESOR

Uso:
    docker compose exec api python scripts/seed_dev.py
    # o localmente (con .env cargado):
    python scripts/seed_dev.py
"""

import asyncio
import sys
import uuid
from datetime import datetime, timezone

# Asegura que /app esté en el path cuando se corre fuera de Docker
sys.path.insert(0, "/app") if "/app" not in sys.path else None

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.core.security import generate_email_hash, hash_password
from app.models.asignacion import Asignacion
from app.models.rol import Rol
from app.models.tenant import Tenant
from app.models.usuario import Usuario

# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------

TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

ROLES = [
    {"nombre": "ADMIN",        "descripcion": "Administrador de tenant"},
    {"nombre": "COORDINADOR",  "descripcion": "Coordinador académico"},
    {"nombre": "PROFESOR",     "descripcion": "Docente / Profesor"},
    {"nombre": "ALUMNO",       "descripcion": "Estudiante"},
]

USUARIOS = [
    {
        "nombre":   "Admin",
        "apellidos": "Demo",
        "email":    "admin@demo.com",
        "password": "admin1234",
        "rol":      "ADMIN",
    },
    {
        "nombre":   "Coordinador",
        "apellidos": "Demo",
        "email":    "coordinador@demo.com",
        "password": "coord1234",
        "rol":      "COORDINADOR",
    },
    {
        "nombre":   "Docente",
        "apellidos": "Demo",
        "email":    "docente@demo.com",
        "password": "docente1234",
        "rol":      "PROFESOR",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def get_or_create_tenant(session: AsyncSession) -> Tenant:
    result = await session.execute(select(Tenant).where(Tenant.id == TENANT_ID))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        tenant = Tenant(id=TENANT_ID, name="Demo University")
        session.add(tenant)
        await session.flush()
        print(f"  [+] Tenant creado: {tenant.name}")
    else:
        print(f"  [~] Tenant ya existe: {tenant.name}")
    return tenant


async def get_or_create_roles(session: AsyncSession) -> dict[str, Rol]:
    roles: dict[str, Rol] = {}
    for r in ROLES:
        result = await session.execute(
            select(Rol).where(Rol.nombre == r["nombre"], Rol.tenant_id == TENANT_ID)
        )
        rol = result.scalar_one_or_none()
        if rol is None:
            rol = Rol(tenant_id=TENANT_ID, nombre=r["nombre"], descripcion=r["descripcion"])
            session.add(rol)
            await session.flush()
            print(f"  [+] Rol creado: {rol.nombre}")
        else:
            print(f"  [~] Rol ya existe: {rol.nombre}")
        roles[rol.nombre] = rol
    return roles


async def get_or_create_usuario(
    session: AsyncSession, data: dict, tenant_id: uuid.UUID
) -> Usuario:
    email_hash = generate_email_hash(data["email"])
    result = await session.execute(
        select(Usuario).where(
            Usuario.tenant_id == tenant_id,
            Usuario.email_hash == email_hash,
        )
    )
    usuario = result.scalar_one_or_none()
    if usuario is None:
        usuario = Usuario(
            tenant_id=tenant_id,
            email=data["email"],
            hashed_password=hash_password(data["password"]),
            nombre=data["nombre"],
            apellidos=data["apellidos"],
            estado="Activo",
        )
        session.add(usuario)
        await session.flush()
        print(f"  [+] Usuario creado: {data['email']}")
    else:
        print(f"  [~] Usuario ya existe: {data['email']}")
    return usuario


async def assign_rol(
    session: AsyncSession, usuario: Usuario, rol: Rol
) -> None:
    result = await session.execute(
        select(Asignacion).where(
            Asignacion.usuario_id == usuario.id,
            Asignacion.rol_id == rol.id,
        )
    )
    if result.scalar_one_or_none() is None:
        asignacion = Asignacion(
            tenant_id=usuario.tenant_id,
            usuario_id=usuario.id,
            rol_id=rol.id,
            desde=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        session.add(asignacion)
        print(f"     → asignado rol {rol.nombre}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def seed() -> None:
    print("\n=== Seed de desarrollo ===\n")
    async with SessionLocal() as session:
        async with session.begin():
            tenant = await get_or_create_tenant(session)
            roles  = await get_or_create_roles(session)

            print()
            for data in USUARIOS:
                usuario = await get_or_create_usuario(session, data, tenant.id)
                await assign_rol(session, usuario, roles[data["rol"]])

    print("\n=== Seed completado ===")
    print("\nCuentas disponibles:")
    print("  admin@demo.com       / admin1234")
    print("  coordinador@demo.com / coord1234")
    print("  docente@demo.com     / docente1234")
    print()


if __name__ == "__main__":
    asyncio.run(seed())
