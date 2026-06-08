# Design: panel-auditoria-metricas

## Technical Approach

We will extend the `AuditService` to support database-level aggregations and paginated queries on the `AuditLog` model. This allows us to serve the new `/api/v1/auditoria/interacciones` and `/api/v1/auditoria/logs` endpoints without pulling excessive data into Python memory. Access control will reuse existing dependencies (`require_permission`) and enforce `_propio` rules (subject restrictions for coordinators) via the `AsignacionRepository`, mirroring the approach used in `AnalisisService`. We will also add a proper SQLAlchemy `ForeignKey` from `AuditLog.materia_id` to `Materia.id`.

## Architecture Decisions

### Decision: Direct SQL Aggregations vs. Application-side Aggregation

**Choice**: Direct SQL Aggregations via SQLAlchemy `func` (`group_by`, `count`, `date`).
**Alternatives considered**: Pulling all logs and grouping them in Python.
**Rationale**: `AuditLog` is an append-only table that can grow very large rapidly. SQL-level aggregations are highly optimized and avoid massive memory footprints in the Python process.

### Decision: Subject Scoping (`_propio` pattern)

**Choice**: Enforce subject isolation within `AuditService` using `AsignacionRepository` to check active assignments.
**Alternatives considered**: Performing the check entirely at the router level.
**Rationale**: The logic requires database queries to check the active assignments of the current user. Placing this in the service ensures that the query logic remains reusable and encapsulates the domain rules for `auditoria:ver_propio`.

### Decision: Foreign Key to Materia

**Choice**: Add an explicit `ForeignKey('materias.id', ondelete='SET NULL')` to `AuditLog.materia_id`.
**Alternatives considered**: Keeping it as a loose UUID reference without a constraint.
**Rationale**: Explicit foreign keys enforce referential integrity. Setting `ondelete='SET NULL'` guarantees that if a subject is deleted (not typical due to soft deletes, but for completeness), the audit log is preserved and does not block the deletion, adhering to the append-only nature of the audit trail.

## Data Flow

    User Request (Admin/Coordinator)
         │
    Router (/api/v1/auditoria/...) ─── Validate Auth/Permission (`auditoria:ver`)
         │
    AuditService
         │─── Check `_propio`? ──> AsignacionRepository (List Active Assignments)
         │
    SQLAlchemy (`db.execute`) ──> PostgreSQL (Group By / Count on `audit_log`)
         │
    Router (Returns `AuditMetricsResponse` or `PaginatedAuditLogs`)

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/models/audit_log.py` | Modify | Add `ForeignKey('materias.id', ondelete='SET NULL')` to `materia_id`. |
| `backend/app/schemas/audit.py` | Create | DTO schemas: `AuditLogQuerySchema`, `AuditLogResponse`, `AuditMetricsResponse`. |
| `backend/app/services/audit.py` | Modify | Add `get_interaction_metrics` and `get_logs` methods with RBAC scope checks. Inject `AsignacionRepository`. |
| `backend/app/api/v1/routers/auditoria.py` | Create | Define REST endpoints for `/logs` and `/interacciones` protected by `require_permission`. |
| `backend/app/main.py` | Modify | Import and register the new `auditoria` router. |

## Interfaces / Contracts

```python
# backend/app/schemas/audit.py
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class DailyActivity(BaseModel):
    date: str
    count: int

class TeacherStatusCount(BaseModel):
    teacher_id: UUID
    status: str
    count: int

class TeacherSubjectInteraction(BaseModel):
    teacher_id: UUID
    subject_id: Optional[UUID]
    count: int

class AuditMetricsResponse(BaseModel):
    daily_activity: List[DailyActivity]
    teacher_communications: List[TeacherStatusCount]
    teacher_subject_interactions: List[TeacherSubjectInteraction]

class AuditLogQuerySchema(BaseModel):
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    materia_id: Optional[UUID] = None
    actor_id: Optional[UUID] = None
    limit: int = 200
    offset: int = 0
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Service RBAC filtering | Mock `AsignacionRepository` and verify that the `materia_id` filter is injected correctly for users with `auditoria:ver_propio`. |
| Integration | `AuditService` aggregations | Seed `audit_log` table with varied entries and verify that `get_interaction_metrics` returns correctly grouped data. |
| E2E | Router Endpoints | Call `/api/v1/auditoria/interacciones` as an Admin (gets all data) and as a Coordinator (gets 403 or filtered data depending on assignment). |

## Migration / Rollout

We will need an Alembic migration to apply the `ForeignKey` to `audit_log.materia_id`.
Run `alembic revision --autogenerate -m "Add FK to audit_log.materia_id"` and ensure there are no orphaned records preventing the migration (if so, they might need to be set to NULL manually in the migration script before applying the constraint).

## Open Questions

- None
