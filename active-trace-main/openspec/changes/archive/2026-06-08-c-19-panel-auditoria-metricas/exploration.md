## Exploration: panel-auditoria-metricas

### Current State
Currently, `AuditLog` (E-AUD) and `AuditLogRepository` exist as an append-only structure. However, there are no endpoints, schemas, or service methods implemented to expose these logs or metrics to the frontend.
The `AuditLog` table contains columns such as `actor_id`, `impersonado_id`, `materia_id`, `accion`, `detalle`, `filas_afectadas`, `ip`, and `user_agent`.

There is no routing for `/api/v1/auditoria` (or `/api/auditoria`) in the backend, and there is no guard implementation for `auditoria:ver` checks for `ADMIN`, `COORDINADOR (propio)` or `FINANZAS`.

### Affected Areas
- `backend/app/models/audit_log.py` — Update `materia_id` column to reference `materias.id` with `ondelete='SET NULL'` now that `C-06` is complete.
- `backend/app/api/v1/routers/auditoria.py` — [NEW] Create router exposing `/api/v1/auditoria` (for panel metrics and full logs query).
- `backend/app/schemas/audit.py` — [NEW] Create schemas for filtering, listing, and metrics responses (e.g., daily action volumes, communications states per teacher, and metrics by teacher-subject combination).
- `backend/app/services/audit.py` — Implement query logic, filters, metrics aggregations, and validation of the coordinator's owned subject scope (`_propio`).
- `backend/app/main.py` — Register the new auditoría router.
- `backend/tests/test_auditoria_endpoints.py` — [NEW] Integration tests verifying filtering, metrics aggregations, and permissions/guards (`auditoria:ver` / `auditoria:ver_propio`).

### Approaches
1. **Direct SQL Aggregations via SQLAlchemy** — Perform metric aggregations (by day, by teacher, and by teacher × subject) directly in database queries using SQLAlchemy's aggregation functions (`func.count`, `func.date_trunc`, etc.).
   - Pros: Efficient performance, minimal memory usage in the app server, scales well.
   - Cons: Slightly more complex repository queries.
   - Effort: Medium

2. **In-Memory Python Aggregations** — Retrieve raw audit logs from database and perform aggregations/groupings in Python.
   - Pros: Easier to write initially.
   - Cons: Horrible performance for large datasets, high memory consumption, does not scale.
   - Effort: Low

### Recommendation
We recommend **Option 1 (Direct SQL Aggregations via SQLAlchemy)**. Since audit logs can grow significantly, performing groupings and daily/teacher counts in the database is the only scalable solution. We will extend `AuditLogRepository` or create clean SQL helper methods in `AuditService`.

### Risks
- **Performance Risk**: The `audit_log` table could grow very large. We need to make sure we index queries on `tenant_id`, `fecha_hora`, `actor_id`, and `materia_id`.
- **RBAC Leak Risk**: Coordinators with the `_propio` permission must only see audit logs and metrics related to subjects/courses they are assigned to. We must strictly filter query results for this role in the service layer.

### Ready for Proposal
Yes — The requirements are clear and the database models are ready. We can proceed to the Proposal phase.
