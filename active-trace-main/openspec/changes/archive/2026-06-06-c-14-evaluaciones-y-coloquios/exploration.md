## Exploration: C-14 Evaluaciones y Coloquios

### Current State
El sistema actualmente maneja materias, alumnos y asignaciones, pero no cuenta con soporte en backend ni en base de datos para Evaluaciones, Reservas y Resultados. Los modelos `Evaluacion`, `ReservaEvaluacion` y `ResultadoEvaluacion` definidos en `04_modelo_de_datos.md` no se encuentran implementados aún.

### Affected Areas
- `backend/app/models/evaluacion.py` — Nuevos modelos SQLAlchemy para `Evaluacion`, `ReservaEvaluacion` y `ResultadoEvaluacion`.
- `backend/app/schemas/evaluacion.py` — Pydantic schemas para request/response.
- `backend/app/api/v1/endpoints/evaluaciones.py` — Endpoints para coordinadores (crear convocatoria, ver métricas, listar convocatorias) y alumnos (reservar turno).
- `backend/app/crud/crud_evaluacion.py` — Operaciones de DB para cupos, reservas y resultados.
- `backend/alembic/versions/...` — Migración `0NN_evaluacion`.
- `frontend/src/...` — Interfaces F7.1 (métricas), F7.2 (importar alumnos), F7.3 (convocatoria), F7.4 (listado), F7.5 (admin).

### Approaches
1. **Modelado Integrado con Cupos Atómicos** — Manejar la disponibilidad de cupos usando transacciones seguras (ej. row locking o un campo de reservas activas contado al vuelo).
   - Pros: Evita overbooking (sobreventa de cupos) en reservas simultáneas de alumnos.
   - Cons: Requiere cuidado extra en SQLAlchemy (`with_for_update` o validación rigurosa).
   - Effort: Medium

2. **Endpoints Modulares por Rol (Coordinador vs Alumno)** — Separar rutas de gestión administrativa (crear coloquio) de la acción puramente estudiantil (reservar turno).
   - Pros: Refleja perfectamente las reglas de RBAC y mantiene el código aislado.
   - Cons: Requiere crear dos routers o manejar el control estrictamente.
   - Effort: Low

### Recommendation
Proceder con la implementación de **Modelado Integrado con Cupos Atómicos** para evitar problemas de concurrencia y **Endpoints Modulares por Rol** para asegurar el aislamiento estricto (RBAC). La dependencia con C-07 implica que los alumnos (Usuario) ya deben estar definidos, lo cual está verificado.

### Risks
- **Concurrencia**: Alumnos intentando reservar el mismo cupo a la vez. Debe gestionarse de forma atómica.
- **Migraciones**: Dependencia de la migración de `C-07`, asegurando que `alumno_id` respete el modelo actual.

### Ready for Proposal
Yes — The orchestrator should proceed to generate the proposal for this change.
