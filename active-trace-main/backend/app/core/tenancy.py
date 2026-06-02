"""
Tenancy context resolution.

RESERVED FOR C-03 (auth): This module will be filled in when JWT authentication
is implemented in C-03. Currently it serves as a placeholder to establish the
contract for how tenant context is resolved.

Usage (in C-03+):
    from app.core.tenancy import get_current_tenant
    from app.core.dependencies import get_tenant_from_session
    
    @router.get("/data")
    async def get_data(session: AsyncSession = Depends(get_db)):
        tenant_id = await get_current_tenant(session)
        repo = SomeRepository(SomeModel, session, tenant_id)
        return await repo.list_all()
"""

from typing import Optional
from uuid import UUID


async def get_current_tenant(session=None) -> Optional[UUID]:
    """
    Resolve the current tenant from the request context (JWT token).
    
    RESERVED FOR C-03: Auth will implement this to extract tenant_id from the
    verified JWT token.
    
    Args:
        session: AsyncSession (optional, for context)
    
    Returns:
        UUID: The current tenant's ID
    
    Raises:
        NotImplementedError: Until C-03 implements auth
    """
    raise NotImplementedError(
        "Tenant resolution not implemented. "
        "This will be filled in C-03 (auth-jwt-2fa) when JWT tokens are added."
    )


def get_tenant_context() -> Optional[UUID]:
    """
    Get tenant context from async local storage or request context.
    
    RESERVED FOR C-03: Will be populated by dependency injection in the
    auth/JWT context.
    
    Returns:
        UUID: The current tenant's ID, or None if not authenticated
    """
    raise NotImplementedError(
        "Tenant context not implemented. "
        "This will be filled in C-03 when auth is implemented."
    )
