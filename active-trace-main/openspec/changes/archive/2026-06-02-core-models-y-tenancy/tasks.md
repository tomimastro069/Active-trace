## 1. Tenant Model y Base Mixin

- [x] 1.1 (RED) Escribir test que verifique que `Tenant` se puede instanciar con UUID y nombre
- [x] 1.2 (RED) Escribir test que valide que `TimestampedTenant` mixin proporciona `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at`
- [x] 1.3 (GREEN) Implementar modelo `Tenant` en `app/models/tenant.py` con campos básicos (id, name, created_at, updated_at, deleted_at)
- [x] 1.4 (GREEN) Implementar mixin `TimestampedTenant` en `app/models/base.py` con todos los campos requeridos
- [x] 1.5 (TRIANGULATE) Agregar test que verifique que `created_at` es inmodificable luego de creación
- [x] 1.6 (TRIANGULATE) Agregar test que `updated_at` se actualiza en `flush()` del ORM
- [x] 1.7 (REFACTOR) Extraer constantes y tipos (ej. Field definitions)

## 2. Repository Genérico con Scope de Tenant

- [x] 2.1 (RED) Escribir test que `BaseRepository[T]` filtra automáticamente por `tenant_id`
- [x] 2.2 (RED) Escribir test que `list_all()` excluye registros con `deleted_at IS NOT NULL`
- [x] 2.3 (GREEN) Implementar clase base `BaseRepository[T]` en `app/repositories/base.py` con métodos CRUD (get_by_id, list_all, create, update, delete_logical)
- [x] 2.4 (TRIANGULATE) Agregar test que `get_by_id()` retorna 404 si el registro es de otro tenant
- [x] 2.5 (TRIANGULATE) Agregar test que `delete_logical()` marca `deleted_at`, no hace DELETE físico
- [x] 2.6 (TRIANGULATE) Agregar test que `update()` modifica `updated_at` automáticamente
- [x] 2.7 (REFACTOR) Extraer validaciones y simplificar métodos large

## 3. Cifrado AES-256

- [x] 3.1 (RED) Escribir test que `encrypt_attr()` retorna cipher diferente del plaintext
- [x] 3.2 (RED) Escribir test que `decrypt_attr(cipher)` recupera exactamente el plaintext original
- [x] 3.3 (RED) Escribir test que descifrado con llave incorrecta falla gracefully (excepción clara)
- [x] 3.4 (GREEN) Implementar `core/security.py` con `encrypt_attr(plaintext: str) -> str` usando Fernet (cryptography)
- [x] 3.5 (GREEN) Implementar `decrypt_attr(cipher: str) -> str`; gestionar excepciones de descifrado
- [x] 3.6 (TRIANGULATE) Agregar test con strings vacíos y Unicode
- [x] 3.7 (TRIANGULATE) Agregar test que cifrado round-trip con diferentes valores siempre produce ciphers diferentes (no determinístico si usa IV)
- [x] 3.8 (REFACTOR) Documentar contrato de interfaz; validar que ENCRYPTION_KEY tiene exactamente 32 bytes

## 4. Tenancy Resolution (Placeholder)

- [x] 4.1 Crear `core/tenancy.py` con placeholder `get_current_tenant()` que retorna None o levanta NotImplementedError; docstring "RESERVADO para C-03 (auth)"
- [x] 4.2 Documentar que este módulo será rellenado en C-03 cuando JWT esté implementado

## 5. Alembic y Migración 001

- [x] 5.1 Inicializar Alembic en `backend/alembic/` con `alembic init` (ya hecho en C-01); verificar que `env.py` está configurado para async engine
- [x] 5.2 (RED) Escribir test que verifica que `Migración 001: tenant` existe en `alembic/versions/`
- [x] 5.3 (GREEN) Crear `alembic/versions/001_tenant.py` que crea tabla `tenant` con columnas: `id` (UUID PK), `name` (text, unique), `created_at`, `updated_at`, `deleted_at` (nullable)
- [x] 5.4 (TRIANGULATE) Ejecutar `alembic upgrade head` contra DB test; verificar que la tabla existe en DB
- [x] 5.5 (TRIANGULATE) Ejecutar `alembic downgrade -1`; verificar que la tabla se elimina
- [x] 5.6 (REFACTOR) Validar que la migración sigue convención (nombre claro, índices si corresponden)

## 6. Tests de Aislamiento Multi-Tenant

- [x] 6.1 (RED) Escribir test que Tenant A creando un registro NO lo hace visible a Tenant B
- [x] 6.2 (RED) Escribir test que `repository.get_by_id()` para otro tenant retorna 404
- [x] 6.3 (RED) Escribir test que soft-delete marca `deleted_at` pero no borra el registro
- [x] 6.4 (RED) Escribir test que cifrado round-trip de atributo sensible funciona
- [x] 6.5 (GREEN) Implementar fixtures en `tests/conftest.py`: sesión de DB test, tenant factory, modelos test
- [x] 6.6 (GREEN) Implementar `tests/test_tenant_isolation.py` con casos RED
- [x] 6.7 (TRIANGULATE) Agregar test de concurrencia: dos tenants creando datos simultáneamente no hay leak
- [x] 6.8 (TRIANGULATE) Agregar test que `list_all()` con múltiples registros en distintos tenants retorna solo del tenant actual
- [x] 6.9 (REFACTOR) Consolidar fixtures; extraer helpers de test

## 7. Integración con Core

- [x] 7.1 Importar `Tenant`, `TimestampedTenant`, `BaseRepository` en `app/core/__init__.py` para exportarlos
- [x] 7.2 Actualizar `core/database.py` para usar `TimestampedTenant` como base declarativa (si no ya lo hace)
- [x] 7.3 Actualizar `core/config.py` para validar `ENCRYPTION_KEY` = 32 bytes exactamente (si no ya lo hace)
- [x] 7.4 Verificar que no hay conflictos de imports entre C-01 reserves y C-02 implementations

## 8. Verificación Final

- [x] 8.1 Ejecutar suite completa de tests (`pytest`) y confirmar verde: ≥80% line coverage, ≥90% reglas de negocio
- [x] 8.2 Verificar que ningun archivo `.py` supera 500 LOC
- [x] 8.3 Levantar stack con docker-compose; hacer `SELECT 1 FROM tenant` vía psql para validar tabla existe
- [x] 8.4 Documentar en docstrings cómo utilizar `BaseRepository[T]`, `TimestampedTenant`, cifrado
- [x] 8.5 Validar que todos los slots reservados están documentados (get_current_tenant, require_permission, etc.)
