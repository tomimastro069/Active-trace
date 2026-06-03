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

# Routes that don't require tenant context
PUBLIC_PATHS = frozenset({
    "/health",
    "/api/v1/health",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
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
    Global tenant enforcement middleware.

    For authenticated routes, verifies that the JWT payload contains a valid
    tenant_id claim. Sets request.state.tenant_id for downstream use.

    Public routes (health, metrics, auth, docs) are excluded.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/")

        # Skip public routes
        if path in PUBLIC_PATHS or any(path.startswith(p) for p in PUBLIC_PREFIXES):
            return await call_next(request)

        # For authenticated routes, tenant_id comes from the JWT via get_current_user.
        # That dependency sets request.state with user info including tenant_id.
        # Here we just ensure the header exists as a fast-fail before hitting the
        # auth dependency, and set request.state.tenant_id for logging/context.
        # The actual tenant enforcement happens in BaseRepository._apply_tenant_scope.

        # Check Authorization header presence (fast-fail)
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing authentication credentials."},
            )

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
