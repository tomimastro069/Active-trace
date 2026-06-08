# Proposal: panel-auditoria-metricas

## Intent
Expose a readonly dashboard and filterable logs for user interactions and system activity (`AuditLog`), satisfying Epic 9 (F9.1, F9.2) and keeping access governed under `auditoria:ver` / `auditoria:ver_propio`.

## Scope

### In Scope
- Expose `/api/v1/auditoria/interacciones` for panel metrics:
  - Daily activity volume (actions by day).
  - Outbound communication states distribution grouped by teacher.
  - Interaction counts by teacher × subject (detailed action counts).
  - Configurable recent actions stream (default 200).
- Expose `/api/v1/auditoria/logs` for full logs query with pagination and filters (date range, `materia_id`, `actor_id`, and active/inactive status).
- Enforce RBAC validation where ADMIN and FINANZAS have global access, while COORDINADOR `(propio)` is restricted to their assigned subjects.

### Out of Scope
- Interactive audit log manipulation (logs are strictly append-only/read-only).
- Performance dashboard UI components (frontend is out of scope).

## Capabilities

### New Capabilities
- `panel-auditoria-metricas`: Read-only queries, aggregation metrics, and log stream for system audit records.

### Modified Capabilities
- `soft-delete-append-only-audit`: Adding relationship to `Materia` model.

## Approach
- Add a foreign key constraint from `audit_log.materia_id` to `materias.id` (ondelete='SET NULL').
- Create `AuditLogQuerySchema` and response DTO schemas in `app/schemas/audit.py`.
- Implement SQL aggregation functions in `AuditService` (via SQLAlchemy select queries with `group_by`, `func.count`, etc.) to calculate daily/teacher/subject statistics.
- Create `/api/v1/auditoria` routes in a new router `auditoria.py` with `require_permission("auditoria:ver")` guard.
- Enforce subject ownership filter in `AuditService` if user has `auditoria:ver_propio` (check coordinator's active assignments in database).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/models/audit_log.py` | Modified | Add `ForeignKey` to `materias.id` |
| `backend/app/schemas/audit.py` | New | Schemas for query filters and response formats |
| `backend/app/services/audit.py` | Modified | Add query/aggregations logic and access validation |
| `backend/app/api/v1/routers/auditoria.py` | New | REST endpoints with RBAC guards |
| `backend/app/main.py` | Modified | Register the new auditoría router |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Query slowdown on large `audit_log` | Low | Enforce mandatory date filters and indexes |
| Unauthorized access by coordinators | Med | Strictly filter query by assigned `materia_id` |

## Rollback Plan
- Revert code edits.
- Demote DB migration (if foreign key migration is applied) via `alembic downgrade`.

## Dependencies
- C-05 (Audit log tables).
- C-06 (Materia model/table).

## Success Criteria
- [ ] Direct SQL aggregations query daily/teacher/subject counts.
- [ ] Admins see global metrics; coordinators only see logs for their assigned subjects.
- [ ] Unit & integration tests pass with >80% coverage.
