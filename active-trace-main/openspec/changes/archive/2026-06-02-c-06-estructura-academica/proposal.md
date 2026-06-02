# Proposal: C-06 Estructura Académica (Entidades Raíz)

## 1. Executive Summary
El objetivo de **C-06** es establecer las entidades fundacionales del dominio académico: `Carrera`, `Cohorte` y `Materia`. 
Con esto materializamos el **ADR-006**: el catálogo de materias es único por tenant, y su instancia de dictado se dará luego mediante asignaciones, separando definición de ejecución.

Se construirán:
1. **Modelos SQLAlchemy**: Carrera (E1), Cohorte (E2) y Materia (E3).
2. **Migración Alembic**: `005_estructura_academica` (dado que la 004 fue AuditLog).
3. **ABM (Endpoints)**: `/api/v1/admin/carreras`, `/cohortes`, y `/materias`.
4. **Validaciones de Negocio**: Unicidades compuestas, y restricción de apertura de cohortes en carreras inactivas.

## 2. Arquitectura y Diseño

### 2.1 Modelos de Datos
Todas las entidades heredarán de un Base que garantiza `id` (UUID), `tenant_id` y timestamps (`TimestampedTenant` si aplica).

**Carrera**:
* `codigo` (String, único por tenant, indexado).
* `nombre` (String).
* `estado` (Enum: Activa | Inactiva).

**Materia**:
* `codigo` (String, único por tenant, indexado).
* `nombre` (String).
* `estado` (Enum: Activa | Inactiva).

**Cohorte**:
* `carrera_id` (FK a Carrera).
* `nombre` (String).
* `anio` (Integer).
* `vig_desde` (Date), `vig_hasta` (Date, nullable).
* `estado` (Enum: Activa | Inactiva).
* Unicidad: `(tenant_id, carrera_id, nombre)`.

### 2.2 Endpoints y Guards
Los ABMs estarán bajo el path `/api/v1/admin/` (ej: `/carreras`, `/cohortes`, `/materias`).
Todos requerirán el guard de permisos: `Depends(require_permission("estructura:gestionar"))`.

### 2.3 Reglas de Negocio a Implementar (Capa de Servicio)
1. **Unicidad Fuerte**: Se atraparán las excepciones de `IntegrityError` (UniqueConstraint) provenientes de la DB y se devolverá un `HTTP 400` amigable.
2. **Bloqueo Cohorte/Carrera**: Si se intenta crear o activar una Cohorte cuya Carrera asociada está Inactiva, el servicio levantará un `HTTP 400`.
3. **Auditoría**: Cada ABM (crear, actualizar, archivar/desactivar) disparará un registro en el `AuditLog` (ej: `CARRERA_CREAR`, `MATERIA_MODIFICAR`) atribuidos al actor que ejecuta la acción (aprovechando C-05).

## 3. Scope / Tareas Principales
- [ ] Mapeo de Enums (EstadoActivoInactivo).
- [ ] Creación de Modelos SQLAlchemy (`carrera.py`, `cohorte.py`, `materia.py`).
- [ ] Generación y revisión de Migración Alembic `005`.
- [ ] Pydantic Schemas para Request/Response de cada entidad.
- [ ] Repositories & Services con lógica de validación (estado de carrera para la cohorte).
- [ ] Routers con guard `estructura:gestionar`.
- [ ] Suite de Tests (CRUD, unicidad tenant-isolated, aislamiento multitenant, validación de estado de carrera).

## 4. Open Questions / Riesgos (Resueltos)
1. **Soft-delete:** Se confirmó que el estado "Inactiva" es suficiente como *soft-delete*. No habrá ruta `DELETE` destructiva (física).
2. **Tipos de Estado:** Se usarán `VARCHAR` en la base de datos (con constrain `ChoiceType` o check), y los Enums se mantendrán únicamente a nivel aplicación (Pydantic / SQLAlchemy `ChoiceType`) para evitar la fricción de migrar enums en Postgres nativo con Alembic.

---
> [!IMPORTANT]
> **Aprobado:**
> El usuario ha aprobado esta propuesta y las decisiones técnicas. Se procede a generar specs, diseño y tareas.
