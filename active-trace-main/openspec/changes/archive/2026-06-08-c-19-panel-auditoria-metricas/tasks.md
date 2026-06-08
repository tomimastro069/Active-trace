# Tasks: panel-auditoria-metricas

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 250-350 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Full implementation and verification of metrics dashboard & audit logs | PR 1 | Base branch; tests and migration included |

## Phase 1: Infrastructure & Model

- [x] 1.1 Add ForeignKey constraint to `materia_id` in `backend/app/models/audit_log.py` referencing `materias.id`.
- [x] 1.2 Generate the DB migration script via Alembic.

## Phase 2: Schemas & Service

- [x] 2.1 Create schemas for query filters and metrics response DTOs in `backend/app/schemas/audit.py`.
- [x] 2.2 Implement `get_interaction_metrics` and `get_logs` in `backend/app/services/audit.py` with direct SQL aggregations and coordinator scoping.

## Phase 3: REST Router

- [x] 3.1 Create endpoints `/interacciones` and `/logs` in `backend/app/api/v1/routers/auditoria.py`.
- [x] 3.2 Register `auditoria_router` in `backend/app/main.py`.

## Phase 4: Testing & Verification

- [x] 4.1 Write service unit and integration tests verifying query filters and aggregations.
- [x] 4.2 Write endpoint E2E/integration tests verifying RBAC and coordinator scope isolation.
