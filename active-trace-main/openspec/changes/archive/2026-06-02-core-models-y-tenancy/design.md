## Context

activia-trace es una plataforma **multi-tenant desde el diseño**, donde cada institución cliente es un tenant aislado. C-01 proporcionó el esqueleto ejecutable (FastAPI, SQLAlchemy 2.0 async, engine conectado); ahora C-02 materializa el **modelo de datos raíz** que todas las entidades de negocio (Usuario, Materia, Asignación, etc. en C-03+) heredarán. 

La restricción fundamental es **row-level multi-tenancy**: toda consulta a la base de datos debe filtrar automáticamente por `tenant_id`. Un query sin scope es un bug que debe fallar en code review. Además, datos sensibles (DNI, CUIL, CBU, email) deben cifrarse en reposo.

El contrato arquitectónico vive en `knowledge-base/04_modelo_de_datos.md` (modelo conceptual), `knowledge-base/08_arquitectura_propuesta.md` (patrón Clean Architecture) y `docs/ARQUITECTURA.md` (detalles técnicos: ADR-002 row-level tenant isolation, AES-256).

## Goals / Non-Goals

**Goals:**

- Implementar modelo `Tenant` como raíz de multi-tenancy: cada fila de toda tabla debe llevar `tenant_id` y filtrar por defecto.
- Crear mixin `TimestampedTenant` reutilizable: `id` (UUID), `tenant_id`, `created_at`, `updated_at`, `deleted_at` (soft delete). Todos los modelos posteriores heredan de este mixin.
- Implementar **Repository genérico** con scope de tenant automático: operaciones CRUD estándar que filtran por `tenant_id` por defecto. Un query sin scope debe ser detectable.
- Utilidad **AES-256** para cifrado en reposo: interfaz limpia que cifra/descifra atributos sensibles. Nunca expone datos en claro en logs, excepciones ni respuestas.
- Setup **Alembic** para migraciones async: `Migración 001: tenant` que crea la tabla base. Convención de "una migración por change de schema" para futuros changes.
- **Tests de aislamiento**: validar que un tenant no puede acceder a datos de otro; soft delete preserva auditoría; cifrado round-trip; timestamps derivados.

**Non-Goals:**

- Modelos de Usuario, Materia, Asignación (→ C-03+).
- Auth, JWT, Argon2 (→ C-03).
- RBAC, matriz de permisos (→ C-04).
- Audit log append-only (→ C-05).
- Lógica de negocio específica de dominios académicos.

## Decisions

### D1 — Multi-tenancy row-level: scope automático en todo Repository

**Decisión**: El `GenericRepository` filtro por `tenant_id` en TODA operación de forma automática (sin que el caller tenga que especificarlo). El tenant se obtiene de la sesión/contexto actual (resuelto por `get_current_tenant()` en `core/tenancy.py`, que a su vez obtiene del JWT verificado en C-03).

**Alternativas consideradas**:
- ❌ Parámetro de tenant opcional en cada operación: riesgo de olvido → queries sin scope. Fail-silent.
- ✅ Scope automático por dependency injection: garantiza que TODA consulta está scoped. Fail-explicit en tests si la sesión no tiene tenant.

**Rationale**: ADR-002 (row-level multi-tenancy) declara explícitamente que el aislamiento debe ser garantizado por arquitectura, no por disciplina del desarrollador. Un Repository que olvida filtrar es un defecto crítico. El pattern de "sesión → tenant → scope automático" previene eso.

### D2 — Soft delete con `deleted_at` timestamp (nunca hard delete)

**Decisión**: Todo modelo tiene columna `deleted_at` (nullable). Una fila "borrada" en lógica de aplicación se marca con `deleted_at = now()`, NUNCA se ejecuta `DELETE` físico de la BD. Las queries por defecto filtran `deleted_at IS NULL`.

**Alternativas consideradas**:
- ❌ Hard delete: pérdida de auditoría, imposible recuperar datos, viola append-only.
- ❌ Flag booleano `is_deleted`: menos flexible; difícil saber CUÁNDO se borró o quién lo hizo.
- ✅ Timestamp `deleted_at`: preserva historia (quién, cuándo); permite recuperación; append-only compatible.

**Rationale**: El sistema es "todo audita" (nombre del producto: *trace*). Soft delete es requisito para auditoría append-only en C-05. Además, la recuperación accidental es más fácil (borrar la marca `deleted_at`).

### D3 — AES-256 con cryptography.io, no hardcode de llaves

**Decisión**: Usar biblioteca `cryptography` (Fernet para simetría). Llave de cifrado (`ENCRYPTION_KEY` de 32 bytes) carga desde `.env` en `core/config.py` (Settings). Interfaz en `core/security.py`: funciones `encrypt_attr(value: str) -> str` y `decrypt_attr(cipher: str) -> str`. Los atributos marcados como sensibles (`email_cifrado`, `dni_cifrado`, etc.) se cifran antes de guardar en BD y se descifran después de leer.

**Alternativas consideradas**:
- ❌ Hacer que la app maneje columnas en claro: violenta la regla de seguridad. Exposición en logs, respuestas HTTP sin HTTPS, etc.
- ❌ Cifrado solo en transporte (TLS): si alguien accede directamente a la BD, ve todo.
- ✅ Cifrado en reposo (AES-256): garantía de que, incluso si la BD se filtra, los datos sensibles no son legibles sin la llave.

**Rationale**: PII (Personally Identifiable Information) JAMÁS en claro en BD. Regla dura del proyecto. La llave debe estar en `core/config.py` (Settings desde `.env`) para que sea inyectable y testeable.

### D4 — Repository genérico con type hints: `BaseRepository[T]`

**Decisión**: Clase genérica `BaseRepository[T]` (con type parameter T que es el modelo ORM). Operaciones CRUD standard: `get_by_id(id, session)`, `list_all(session, skip, limit)`, `create(obj, session)`, `update(obj, session)`, `delete_logical(id, session)` (marca `deleted_at`). Cada Repository concreto hereda de esta clase.

**Alternativas consideradas**:
- ❌ Métodos individuales sin abstracción: duplication, sin garantías de scope.
- ✅ Base genérica con scope automático: DRY, consistencia, fail-explicit.

**Rationale**: Clean Architecture (capas de responsabilidad). Centraliza la lógica de multi-tenancy en un solo lugar. Si el scope está mal, todos los Repositories lo heredan correcto.

### D5 — Mixin `TimestampedTenant`, no herencia de múltiples clases

**Decisión**: Clase mixin `TimestampedTenant` que proporciona `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at`. Todos los modelos de negocio hacen `class Usuario(TimestampedTenant, Base)`. El mixin es reutilizable, no duplicado en cada entidad.

**Alternativas consideradas**:
- ❌ Heredar de múltiples clases (problemas de MRO en Python).
- ✅ Mixin limpio con una responsabilidad: timestamps + tenant scope.

**Rationale**: DRY, evita boilerplate en cada modelo. El timestamp y el tenant son tan transversales que el mixin es correcto.

### D6 — `Migración 001: tenant` como única migración de C-02; convención de una por change

**Decisión**: Alembic se inicializa en C-01 sin migraciones de dominio. C-02 crea exactamente una migración: `001_tenant.py` que crea tabla `tenant`, la columna `tenant_id`, índices y constraints. Convención futura: cada change de schema = una migración (el nombre puede ser más largo, ej `002_usuario_asignacion.py`).

**Alternativas consideradas**:
- ❌ Múltiples migraciones por change: difícil trackear qué pertenece a qué change.
- ✅ Una migración por change: clear ownership, rollback atomicity.

**Rationale**: Simplifica versionado y deployment. Cada change es una "transacción" en el DB schema.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **Scope automático olvidado en queries raw**: Un developer escribe `SELECT * FROM users` sin filtro de tenant | Banear queries raw. Usar ORM siempre. Code review. Tests de aislamiento que fallan si hay fuga. |
| **Descifrado fallido en prod (llave incorrecta)**: Los datos se guardan cifrados con llave A, se intenta descifrar con llave B | Las excepciones de descifrado deben ser claras y logeadas. Llave en `.env`, no hardcoded. Backup de llave (rotación futura en C-XX). |
| **Performance de cifrado**: Cifrar/descifrar en cada read es overhead | Aceptable: PII es columnas específicas, no todas. Índices en columnas cifradas funcionan (buscan por cipher, no plaintext). |
| **Soft delete: consultas olvidadas filtran `deleted_at`**: Un query old schema que no checkea `deleted_at` ve filas "borradas" | ORM queries por defecto filtran `deleted_at IS NULL`. Queries raw deben ser revisadas. |
| **Tenant context no disponible en ciertos flows**: Batch jobs, workers, tests | Tenant debe resolverse de: JWT (en requests), sesión de test, parámetro explícito. Nunca asumir. |

## Migration Plan

1. **Setup en C-02**:
   - Crear mixin `TimestampedTenant` en `app/models/base.py`.
   - Crear tabla `Tenant` (modelo ORM).
   - Crear `GenericRepository[T]` en `app/repositories/base.py`.
   - Crear `encryption.py` con `encrypt_attr()`, `decrypt_attr()`.
   - Crear `tenancy.py` con `get_current_tenant()` (placeholder de momento, C-03 lo rellena).
   - Crear `Migración 001: tenant` en Alembic.
   - Tests de aislamiento, cifrado, timestamps.

2. **Validación**:
   - Suite de tests verde (aislamiento, soft delete, cifrado).
   - Migración aplica correcta en DB de test.
   - Ningun modelo viola las reglas (hereda de `TimestampedTenant`).

3. **Rollback** (si es necesario):
   - `alembic downgrade -1` (revierte `Migración 001`).
   - Restaura schema limpio (salvo tablas nuevas de otros changes en paralelo).

## Open Questions

1. **¿Cómo se resuelve el `tenant` en contextos sin sesión (workers, batch jobs)?**
   - Respuesta esperada: Parámetro explícito o variable de contexto asyncio. Details en C-02 design del worker (C-12+).

2. **¿Qué sucede si `deleted_at` se marca pero luego se necesita "desmarcar"?**
   - Respuesta: Setear `deleted_at = NULL`. No hay "delete hard" — siempre recuperable. Pero necesita permiso y auditoría de "recuperación".

3. **¿Rotación de llaves de cifrado?**
   - Fuera de scope C-02. Será un change futuro (`C-XX-encryption-key-rotation`) que re-encripta datos con llave nueva.
