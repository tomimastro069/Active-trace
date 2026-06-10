# Tasks: fix-01-tenant-middleware-endpoints-publicos

## 1. Backend

- [x] 1.1 Verificar que todos los routers protegidos declaran `get_current_user`/`require_permission`
      (fail-closed se mantiene sin el fast-fail del middleware).
- [x] 1.2 Agregar `/api/v1/auth/forgot`, `/api/v1/auth/reset` y `/api/v1/auth/verify-2fa` a
      `PUBLIC_PATHS` en `app/core/tenancy.py`.
- [x] 1.3 Eliminar el rechazo 401 por header `Authorization` ausente en `TenantMiddleware.dispatch`;
      actualizar docstring explicando dónde vive la autenticación real.

## 2. Verificación

- [x] 2.1 Probe in-proc: `POST /api/v1/auth/forgot|reset|verify-2fa` sin header ya no devuelven 401
      del middleware.
- [x] 2.2 Suite completa de pytest contra Postgres real: los 20 tests que fallaban por 401 pasan;
      sin regresiones (incluye `test_auditoria` unauthorized → 401 vía OAuth2PasswordBearer).
