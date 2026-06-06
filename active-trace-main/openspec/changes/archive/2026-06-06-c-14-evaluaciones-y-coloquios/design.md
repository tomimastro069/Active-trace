# Design: Evaluaciones y Coloquios (C-14)

## Technical Approach
Implementar los modelos SQLAlchemy `Evaluacion`, `ReservaEvaluacion` y `ResultadoEvaluacion` heredando del mixin base `TimestampedTenant`. Se añadirán esquemas Pydantic y un router con separación semántica de rutas para distinguir las acciones administrativas de la reserva efectuada por alumnos. Para evitar colisiones en la reserva de turnos, el CRUD utilizará transacciones con bloqueo de fila (`with_for_update`).

## Architecture Decisions

### Decision: Aislamiento de rutas por Rol
**Choice**: Separar rutas en `/api/v1/coloquios/admin/*` y `/api/v1/coloquios/reservas/*`.
**Alternatives considered**: Un único endpoint `/api/v1/coloquios/` aplicando condicionales lógicos dentro de las vistas.
**Rationale**: Clarifica y refuerza las políticas de seguridad de RBAC, impidiendo que el middleware o un bug en la capa de vista exponga métricas o modifique la configuración de cupos de forma inadvertida a alumnos.

### Decision: Control atómico de Cupos
**Choice**: Usar row locking de la base de datos (`query(...).with_for_update()`) en la transacción que inscribe un alumno a un turno (ReservaEvaluacion).
**Alternatives considered**: Agregar una capa de caché de Redis para control concurrente, o usar validación post-inserción.
**Rationale**: Mantener Redis fuera de las dependencias core del control de concurrencia simplifica la infraestructura de desarrollo y despliegue local, y `with_for_update` asegura total consistencia a nivel SQL de manera nativa y rápida.

## Data Flow

    [Alumno] ──(Reservar)──→ FastAPI Router (Reserva)
                                  │ (Bloqueo y validación de cupo)
                                  ▼
    [Coordinador] ─(CRUD)──→ Base de Datos (Evaluacion / ReservaEvaluacion)
                                  ▲
    [Profesor] ──(Puntuar)── FastAPI Router (Admin/Puntaje) 

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/models/evaluacion.py` | Create | Define Modelos `Evaluacion`, `ReservaEvaluacion`, `ResultadoEvaluacion` (usando `TimestampedTenant`). |
| `backend/app/schemas/evaluacion.py` | Create | Schemas de validación para requests y responses. |
| `backend/app/api/v1/routers/evaluaciones.py` | Create | Puntos finales de la API (incluye /admin y /reservas). |
| `backend/app/crud/crud_evaluacion.py` | Create | Lógica CRUD y la transacción atómica para reserva (`reservar_turno`). |
| `backend/alembic/versions/*_evaluaciones.py` | Create | Archivo de migraciones de base de datos. |

## Interfaces / Contracts

```python
# Extracto Schema de Reserva (Esquema simplificado)
class ReservaEvaluacionCreate(BaseModel):
    evaluacion_id: UUID
    # No requiere alumno_id, se toma del token de sesión de forma segura

class EvaluacionCreate(BaseModel):
    materia_id: UUID
    cohorte_id: UUID
    tipo: EvaluacionTipoEnum  # Parcial, Coloquio
    instancia: str
    dias_disponibles: int
    cupos_totales: int
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Modelos y schemas | Testear instanciación Pydantic, constraints, y omisión de PKs en data body. |
| Integration | Concurrencia al reservar | Script Pytest que intente realizar >10 requests HTTP concurrentes sobre 1 solo cupo restante. Verificar que solo 1 resulte HTTP 200 y el resto HTTP 400. |
| Integration | Seguridad RBAC | Verificar que un alumno reciba HTTP 403 en `/api/v1/coloquios/admin/*`. |

## Migration / Rollout
Generar una migración estándar de base de datos con Alembic para las tablas de modelo. No hay migraciones de datos legados pendientes ya que esta es una funcionalidad nueva.

## Open Questions

- [ ] ¿Los cupos se manejan de manera global por la `Evaluacion` o por bloque horario / día específico? El alcance asume cupos por `Evaluacion` global, en caso contrario, se requiere ajustar la entidad para que defina sub-turnos de manera más atómica (ej. un modelo secundario de Slot).
