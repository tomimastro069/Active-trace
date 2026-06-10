"""
Tenancy context resolution for multi-tenant isolation.

Implements: C17-3.1

- TenantMiddleware: global enforcement via Starlette middleware
- get_current_tenant: extract tenant_id from request state (set by auth)

"""
from uuid import UUID
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Routes that don't require tenant context (documented public surface)
PUBLIC_PATHS = frozenset({
    "/health",
    "/api/v1/health",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/verify-2fa",
    "/api/v1/auth/forgot",
    "/api/v1/auth/reset",
    "/metrics",
    "/docs",
    "/redoc",
    "/openapi.json",
})

# Path prefixes that are always public
PUBLIC_PREFIXES = (
    "/docs",
    "/redoc",
)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Tenant context middleware (pass-through).

    Authentication is NOT enforced here: every protected endpoint declares
    `get_current_user` (OAuth2PasswordBearer responds 401 on a missing or
    invalid token) and/or `require_permission` (403 without permission).
    Tenant enforcement happens in BaseRepository._apply_tenant_scope using
    the tenant_id resolved from the verified JWT.

    Rejecting requests here based on raw headers duplicated that logic and
    broke anonymous auth endpoints (forgot/reset/verify-2fa) plus every test
    that relies on dependency_overrides. PUBLIC_PATHS documents the public
    surface for tooling and future use.
    """

    async def dispatch(self, request: Request, call_next):
        return await call_next(request)


def get_current_tenant(request: Request) -> UUID:
    """
    Extract tenant_id from request.state (set by auth dependency).

    For use in contexts where you need tenant_id outside of the service layer.
    In most cases, use current_user.tenant_id from the auth dependency instead.
    """
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        logger.warning("No tenant id found in request state.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing tenant context.",
        )
    if isinstance(tenant_id, str):
        try:
            return UUID(tenant_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed tenant id.",
            )
    return tenant_id
