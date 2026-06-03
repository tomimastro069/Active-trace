# Proposal: C-09 padron-ingesta-moodle

## Intent

Implementar el mecanismo de ingesta de padrones de alumnos inscritos en materias y cohortes. Este mecanismo alimenta el dominio operativo del sistema al traer los datos desde el LMS (Moodle) o mediante carga manual (CSV/XLSX), permitiendo gestionar alumnos, hacerles seguimiento y emitirles comunicaciones masivas basadas en su avance académico.

## Scope

### In Scope
- Creación de los modelos `VersionPadron` y `EntradaPadron`.
- Lógica de versionado: solo una versión activa por binomio de materia×cohorte (activar una desactiva la anterior).
- Ingesta de padrones de alumnos a través de carga manual (archivos `.xlsx` / `.csv`) como fallback (F1.3, F1.4).
- Ingesta sincrónica vía Moodle Web Services (`integrations/moodle_ws.py`) con reintentos para fallas HTTP 502.
- Manejo de estudiantes sin usuario en el sistema (entradas de padrón donde `usuario_id` puede ser nulo o diferido).
- Auditoría estricta de la carga de padrón mediante `PADRON_CARGAR` y vaciado de datos con `PADRON_VACIAR` (F1.5, RN-04).

### Out of Scope
- Interfaz gráfica en el Frontend SPA (será abordado en las épicas de Frontend C-22).
- Cálculo o importación de notas/calificaciones y umbrales (es scope de C-10).

## Capabilities

> This section is the CONTRACT between proposal and specs phases.

### New Capabilities
- `padron-ingesta`: Importación y versionado de padrones vía CSV/XLSX y Moodle WS con control de transacciones y auditoría.

### Modified Capabilities
- None

## Approach

Implementación **iterativa orientada local-primero**:
1. Crear los modelos `VersionPadron` y `EntradaPadron` usando SQLAlchemy e incluir la migración de esquema vía Alembic.
2. Desarrollar el servicio central de ingesta (`PadronService`) utilizando la carga manual (CSV/XLSX) para perfeccionar las reglas de versionado (upsert destructivo donde la versión vieja se marca inactiva) y el parseo de estudiantes sin ID de usuario.
3. Crear el cliente `MoodleWSClient` en `integrations/moodle_ws.py` encapsulando la lógica de requests y reintentos en fallas comunes como 502, el cual consumirá internamente el `PadronService`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/models/padron.py` | New | Modelos `VersionPadron` y `EntradaPadron` |
| `backend/alembic/versions/` | New | Script de migración para las tablas |
| `backend/app/schemas/padron.py` | New | Pydantic Schemas para validación y preview |
| `backend/app/services/padron_service.py` | New | Lógica de negocio e ingesta de padrón |
| `backend/app/routers/padron.py` | New | API Endpoints de carga y sincronización |
| `backend/app/integrations/moodle_ws.py` | New | Cliente externo HTTP para Moodle WS |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Resolución inestable de identidad al cruzar datos PII cifrados | Med | Proveer un lookup robusto y cacheadol de e-mails descifrados durante la carga masiva en memoria, minimizando queries DB. |
| Fallos en Moodle WS | High | Implementar Circuit Breaker y retry policies con `Tenacity` para manejar errores 502 limpiamente sin romper el request. |
| Inconsistencia de DB por carga masiva fallida | Med | Realizar la creación de la nueva versión y entradas en una transacción única. Fallas no commitean. |

## Rollback Plan

- **Código:** Revertir los PRs correspondientes a `C-09`.
- **Base de Datos:** Ejecutar el `downgrade` de Alembic asociado a la migración generada, eliminando las tablas `version_padron` y `entrada_padron`.
- **Datos:** No se requiere migración de datos existentes, la funcionalidad es nueva.

## Dependencies

- Requiere el completamiento de la fase `C-07 usuarios-y-asignaciones` para tener usuarios con PII y relaciones base.

## Success Criteria

- [ ] Un padrón de estudiantes puede importarse desde un `.csv` de forma exitosa y persistente.
- [ ] La importación de un nuevo padrón desactiva automáticamente el anterior, preservando el histórico.
- [ ] La integración a Moodle WS recupera la lista de participantes y falla graciosamente al simular un error 502, reportándolo correctamente al usuario.
- [ ] Entradas de padrón pueden crearse aunque el alumno aún no tenga cuenta (identificador `usuario_id` nulo).
