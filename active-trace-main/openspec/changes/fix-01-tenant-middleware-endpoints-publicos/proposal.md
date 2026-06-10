# Fix 01 — TenantMiddleware bloquea endpoints anónimos y rompe 20 tests

## Why

`TenantMiddleware` (`app/core/tenancy.py`, introducido junto al change archivado C-17) devuelve
`401 Missing authentication credentials` a toda request sin header `Authorization`, salvo las de
`PUBLIC_PATHS`. Esa lista no incluye los endpoints anónimos del flujo de auth:

- `POST /api/v1/auth/forgot` — recuperación de contraseña (usuario sin sesión)
- `POST /api/v1/auth/reset` — reset de contraseña con token de un solo uso
- `POST /api/v1/auth/verify-2fa` — segundo paso del login con TOTP (pre-sesión)

Verificado contra la app real: los tres devuelven 401, es decir **la recuperación de contraseña y
el login con 2FA están rotos en producción** (FL-01 / C-03).

Además, el fast-fail corta la request **antes** de que actúen las dependencies, lo que rompió
20 tests preexistentes de C-03/C-04/C-06/C-07/C-08/C-09/C-10/C-11/C-19/C-20 que usan
`app.dependency_overrides[get_current_user]` sin enviar header (`assert 401 == 200/201`).

## What Changes

- El fast-fail por header ausente se elimina del middleware. La autenticación queda donde siempre
  estuvo y de forma fail-closed: `get_current_user` usa `OAuth2PasswordBearer`, que ya responde
  `401` ante header ausente o inválido, y `require_permission` responde `403` sin permiso.
  Se verificó que **todos** los routers protegidos declaran esas dependencies.
- `PUBLIC_PATHS` se conserva como documentación de la superficie pública e incorpora
  `/api/v1/auth/forgot`, `/api/v1/auth/reset` y `/api/v1/auth/verify-2fa`.
- El middleware queda como punto de extensión para contexto de tenant (logging), sin lógica de
  rechazo propia.

## Impact

- `backend/app/core/tenancy.py`
- Sin cambios de schema ni de API pública. Sin migraciones.
- Tests: los 20 tests rotos vuelven a pasar; `tests/api/test_auditoria.py::test_get_*_unauthorized`
  siguen pasando porque el 401 ahora lo emite `OAuth2PasswordBearer`.
