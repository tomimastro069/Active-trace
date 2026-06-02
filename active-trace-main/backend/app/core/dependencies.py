from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# RESERVADO para C-03: get_current_user (resolución y autenticación de usuario vía JWT)
# async def get_current_user(...) -> User:
#     pass

# RESERVADO para C-04: get_tenant (resolución del tenant actual para multi-tenancy)
# async def get_tenant(...) -> Tenant:
#     pass

# RESERVADO para C-03: require_permission (autorización basada en roles/permisos)
# def require_permission(permission: str):
#     pass

