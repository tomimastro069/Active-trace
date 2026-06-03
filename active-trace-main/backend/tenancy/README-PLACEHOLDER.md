# Tenancy

Módulo reservado para futura extracción de lógica multi-tenant.

## Ubicación actual

La implementación activa de tenancy vive en:

- **Middleware global**: [`app/core/tenancy.py`](../app/core/tenancy.py) — `TenantMiddleware`
- **Scope automático**: [`app/repositories/base.py`](../app/repositories/base.py) — `_apply_tenant_scope`
- **Resolución JWT**: [`app/core/dependencies.py`](../app/core/dependencies.py) — `get_current_user`

## Convención

Todas las queries DEBEN pasar por `BaseRepository._apply_tenant_scope`. Un query sin filtro de tenant es un defecto.