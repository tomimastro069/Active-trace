# Tasks: fix-03-auth-me-endpoint

## 1. Backend

- [x] 1.1 Agregar `GET /me` (`response_model=CurrentUser`) al router de auth, devolviendo el
      resultado de `Depends(get_current_user)`.

## 2. Tests

- [x] 2.1 `test_me_endpoint`: login real → `GET /api/v1/auth/me` con el access token devuelve
      `email`, `tenant_id` y `roles` del JWT; sin header → 401.

## 3. Verificación

- [x] 3.1 `pytest tests/test_auth.py` en verde.
