# Especificaciones: C-06 Estructura Académica

## Entidades

### Carrera
La `Carrera` representa un programa académico ofrecido por un Tenant.
- **Campos**: `id`, `tenant_id`, `codigo` (único por tenant), `nombre`, `estado` (Activa/Inactiva).
- **Validaciones**:
  - `codigo` debe ser único dentro de un `tenant_id`.

### Materia
La `Materia` es un catálogo único de asignaturas por Tenant.
- **Campos**: `id`, `tenant_id`, `codigo` (único por tenant), `nombre`, `estado` (Activa/Inactiva).
- **Validaciones**:
  - `codigo` debe ser único dentro de un `tenant_id`.

### Cohorte
La `Cohorte` representa la inscripción a un periodo académico específico para una `Carrera`.
- **Campos**: `id`, `tenant_id`, `carrera_id`, `nombre`, `anio`, `vig_desde`, `vig_hasta`, `estado` (Activa/Inactiva).
- **Validaciones**:
  - La tupla `(tenant_id, carrera_id, nombre)` debe ser única.
  - Al crear o activar, la `carrera_id` asociada **no puede** estar inactiva.

## Casos de Uso (CRUD API)

Los administradores de cada tenant (usuarios con permiso `estructura:gestionar`) pueden realizar operaciones ABM sobre el catálogo:

1. **Creación (POST):**
   - Recibe Payload de creación.
   - Verifica unicidad vía Constraint DB / Query previo.
   - Valida reglas de estado (ej. Carrera no inactiva para crear Cohorte).
   - Genera Audit Log.

2. **Lectura (GET):**
   - Paginada y filtrada por `tenant_id`.
   - Filtros adicionales: `estado`.

3. **Modificación (PUT/PATCH):**
   - No está permitido modificar el `tenant_id`.
   - Si cambia `estado` a Inactiva, se registra en log.
   - Si se cambia a Activa una Cohorte, se revalida que la Carrera esté Activa.

4. **Borrado Físico no permitido**:
   - Todo se hace mediante cambio de `estado` a `Inactiva` (Soft Delete Semántico).

## Auditoría
Cualquier modificación o creación emitirá los eventos correspondientes en el sistema de Auditoría implementado en C-05:
- `CARRERA_CREAR`, `CARRERA_MODIFICAR`, `CARRERA_ESTADO_CAMBIAR`
- `MATERIA_CREAR`, `MATERIA_MODIFICAR`, `MATERIA_ESTADO_CAMBIAR`
- `COHORTE_CREAR`, `COHORTE_MODIFICAR`, `COHORTE_ESTADO_CAMBIAR`
