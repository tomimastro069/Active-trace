# Fix 03 — Falta `GET /api/v1/auth/me`: el login y la restauración de sesión del frontend están rotos

## Why

El shell del frontend (C-21) depende de `GET /auth/me` en dos puntos:

- `LoginPage` lo llama inmediatamente después de un login exitoso para obtener el usuario y
  poblar el `AuthContext` (`loginUser(user, access_token)`).
- `AuthContext.initializeAuth` lo llama al montar la app para restaurar la sesión desde el
  refresh token persistido.

El backend **no expone ese endpoint** (verificado volcando las rutas registradas). Consecuencia:
aun con credenciales válidas el login falla en la UI, y cada recarga de página desloguea al
usuario. Los tests del frontend no lo detectan porque mockean `authService`.

## What Changes

- Nuevo endpoint `GET /api/v1/auth/me` en el router de auth. Devuelve el `CurrentUser` resuelto
  por `get_current_user` desde el JWT verificado (regla de oro: identidad solo de la sesión;
  stateless, sin hit a DB, igual que el resto de los access checks).
- El shape de `CurrentUser` (`id`, `tenant_id`, `email`, `roles`, `impersonated_by_id`) coincide
  campo a campo con la interfaz `AuthUser` del frontend — no hace falta tocar el frontend.

## Impact

- `backend/app/api/v1/routers/auth.py` (+1 endpoint)
- `backend/tests/test_auth.py` (+1 test: login real → `GET /me` con bearer devuelve la identidad
  del token; sin token → 401)
- Sin migraciones ni cambios de schema.
