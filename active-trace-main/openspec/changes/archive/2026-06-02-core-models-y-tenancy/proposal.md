## Why

activia-trace necesita un modelo de datos multi-tenant desde el cimiento. Aunque C-01 ya materializó el esqueleto ejecutable (FastAPI, conexión a DB, observabilidad), el sistema aún no tiene **entidades de dominio, aislamiento de tenant a nivel de datos, ni la capacidad de cifrar datos sensibles en reposo**. Sin estos componentes fundamentales, C-03 (auth) y C-04 (RBAC) no tienen donde apoyarse. Este change implementa la base de persistencia que toda la lógica de negocio posterior requiere.

## What Changes

- **Modelo `Tenant` raíz** — la entidad que define cada institución cliente y es el scope de aislamiento de toda consulta de base de datos.
- **Mixin base `TimestampedTenant`** — plantilla reutilizable con `id` (UUID), `tenant_id`, `created_at`, `updated_at`, `deleted_at` (soft delete). Todos los modelos posteriores heredarán de este mixin.
- **Repository genérico** con scope de tenant SIEMPRE activo — toda consulta filtra automáticamente por `tenant_id` por defecto. Un query sin scope debe ser rechazado en revisión.
- **Utilidad AES-256** para cifrado en reposo de atributos sensibles — DNI, CUIL, CBU, email (cuando sea necesario). Interfaz de cifrado/descifrado que nunca expone datos en texto plano en logs.
- **Setup Alembic** — inicialización del framework de migraciones con `env.py` configurado para engine async; **Migración 001: tenant** como primer cambio de esquema; convención de "una migración por cambio de schema" establecida.
- **Tests de aislamiento multi-tenant** — un tenant no puede ver datos de otro; soft delete preserva auditoría; cifrado round-trip funciona correctamente; timestamps derivados funcionan.

No hay BREAKING changes: C-01 definió slots reservados (core/tenancy.py, core/exceptions.py) que C-02 rellenará. El resto del sistema aún no existe.

## Capabilities

### New Capabilities

- `tenant-model`: Modelo `Tenant` que define el scope de aislamiento de datos. Cada institución cliente es un tenant separado; todas las consultas filtran por `tenant_id` por defecto.
- `timestamped-tenant-mixin`: Mixin base reutilizable que proporciona `id` (UUID), `tenant_id`, `created_at`, `updated_at`, `deleted_at` (soft delete). Todos los modelos de negocio heredarán de este mixin.
- `generic-repository-tenant-scoped`: Repository genérico que implementa operaciones CRUD estándar con **scope de tenant automático**. Todo query filtra por `tenant_id`; un query sin scope debe ser detectado en revisión.
- `aes256-encryption-utility`: Utilidad para cifrar/descifrar atributos sensibles en reposo (DNI, CUIL, CBU, email). Interfaz que jamás expone datos en texto plano en logs ni en excepciones.
- `alembic-async-setup`: Framework Alembic configurado para migraciones async; convención de "una migración por change de schema"; **Migración 001: tenant** que crea la tabla `tenant` y establece el contrato de identidad.
- `soft-delete-append-only-audit`: Patrón de soft delete transversal (nunca hard delete). Los datos borrados se conservan con `deleted_at` timestamp, preservando la auditoría append-only.
- `tenant-isolation-tests`: Suite de tests que valida aislamiento multi-tenant, soft delete, cifrado, timestamps.

### Modified Capabilities

<!-- No existing specs affected; this is the foundation layer. -->

## Impact

- **Nuevo código** — modelos raíz (`Tenant`), mixin base (`TimestampedTenant`), repository genérico (`GenericRepository`), utilidad de cifrado (`encryption.py`), migraciones iniciales.
- **Dependencias nuevas** — cryptography (para AES-256).
- **Estructura de persistencia** — define el patrón que C-03+ (auth, RBAC, dominio académico) siguen. Sin esta capa, auth no tiene identidad de usuario.
- **Auditoría** — soft delete prepara el terreno para append-only en C-05.
- **Governance** — CRÍTICO. Multi-tenancy y cifrado son propiedades de seguridad no negociables. Fallan en code review si no están correctas.
