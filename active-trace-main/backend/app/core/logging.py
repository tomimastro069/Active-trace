import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Context var to propagate tenant_id across async call stack
_tenant_id_ctx: ContextVar[str | None] = ContextVar("tenant_id", default=None)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        # ADD tenant_id from contextvars (auto-injected by middleware)
        tenant_id = _tenant_id_ctx.get()
        if tenant_id:
            log_entry["tenant_id"] = tenant_id
        # Fallback: explicit tenant_id on the record (manual calls)
        elif hasattr(record, "tenant_id") and record.tenant_id:
            log_entry["tenant_id"] = str(record.tenant_id)
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

def setup_logging(level: int = logging.INFO, stream: Any = None) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)


class TenantLoggingMiddleware(BaseHTTPMiddleware):
    """
    Injects tenant_id into the logging context for every request.

    After auth resolves the user, request.state will contain tenant info.
    This middleware reads it and sets the contextvar so ALL logs within
    the request automatically include tenant_id without manual effort.
    """

    async def dispatch(self, request: Request, call_next):
        # Try to extract tenant_id from the auth header (JWT sub claim)
        # This runs AFTER TenantMiddleware but BEFORE route handlers
        tenant_id = getattr(request.state, "tenant_id", None)
        if tenant_id:
            token = _tenant_id_ctx.set(str(tenant_id))
        else:
            # Try extracting from Authorization header directly for early logging
            token = None
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                try:
                    import base64
                    jwt_payload = auth.split(".")[1]
                    # Add padding
                    jwt_payload += "=" * (4 - len(jwt_payload) % 4)
                    payload = json.loads(base64.urlsafe_b64decode(jwt_payload))
                    tid = payload.get("tenant_id")
                    if tid:
                        token = _tenant_id_ctx.set(str(tid))
                except Exception:
                    pass  # Best-effort: don't break request for logging

        try:
            response = await call_next(request)
            return response
        finally:
            if token is not None:
                _tenant_id_ctx.reset(token)
