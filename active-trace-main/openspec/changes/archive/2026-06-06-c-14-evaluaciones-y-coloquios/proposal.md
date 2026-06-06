# Proposal: Evaluaciones y Coloquios (C-14)

## Intent
Implementar el soporte para Evaluaciones y Coloquios (Épica 7) permitiendo a coordinadores crear convocatorias con cupos y a los alumnos reservar turnos de examen oral de forma atómica y segura.

## Scope
### In Scope
- Modelos `Evaluacion`, `ReservaEvaluacion`, y `ResultadoEvaluacion` con multitenancy.
- Convocatoria de coloquio: creación (instancia, días, cupos), importación de alumnos, listado, métricas (convocados/reservas/libres) y admin global.
- Reserva de turno (ALUMNO) en día disponible con cupo y validación de estado (Activa/Cancelada).
- Endpoints en `/api/v1/coloquios/*`.
- Base de datos: Migración y transacciones atómicas para reservas.
- Cobertura de tests: creación de turnos, reserva resta cupo, rechazo sin cupo, métricas, y resultados.

### Out of Scope
- Integración automática con calendarios externos (Google Calendar, etc.).
- Gestión de exámenes no orales o subida de archivos de examen.

## Capabilities
### New Capabilities
- `evaluaciones-y-coloquios`: Gestión de convocatorias, reservas de turnos por parte de alumnos, consolidación de notas y métricas de coloquios.

### Modified Capabilities
None

## Approach
- **Backend (FastAPI)**:
  - Crear router `/api/v1/coloquios` para endpoints de alumno y coordinador (con RBAC).
  - Validar concurrencia en reservas con row locking (`with_for_update` o similar) sobre el cupo disponible del día/turno del coloquio en SQLAlchemy.
- **Base de Datos**:
  - Modelos SQLAlchemy mapeando `Evaluacion`, `ReservaEvaluacion` y `ResultadoEvaluacion`.
  - Crear migración de Alembic.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/models/evaluacion.py` | New | Modelos SQLAlchemy E14 |
| `backend/app/schemas/evaluacion.py` | New | Esquemas Pydantic |
| `backend/app/api/v1/endpoints/evaluaciones.py` | New | Rutas API y control de acceso |
| `backend/app/crud/crud_evaluacion.py` | New | Operaciones de persistencia con bloqueo |
| `backend/alembic/versions/` | New | Archivo de migración |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Overbooking por reservas concurrentes | Med | Bloqueo de fila (`with_for_update`) al reservar |
| Carga de alumnos no registrados en C-07 | Low | Restricción FK y validación contra base de datos |

## Rollback Plan
- Alembic downgrade para remover tablas creadas.
- Revertir cambios de git en routers y esquemas.

## Dependencies
- `C-07` (Modelos y asignaciones de usuarios/alumnos listos).

## Success Criteria
- [ ] Convocatorias creadas correctamente y visualizadas en el panel de métricas.
- [ ] Alumnos pueden reservar un turno, reduciendo el cupo disponible de manera atómica.
- [ ] Intentos de reservar sin cupo fallan con error `400 Bad Request`.
