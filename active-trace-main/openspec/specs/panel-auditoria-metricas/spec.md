# panel-auditoria-metricas Specification

## Purpose
This specification governs the read-only audit log dashboard and metrics querying behavior. It outlines RBAC constraints, scope-isolation for coordinators, and metric aggregations.

## Requirements

### Requirement: RBAC and Scope Isolation
The system SHALL restrict access to audit logs and metrics based on roles and active teaching assignments.
- ADMIN and FINANZAS roles MUST have unrestricted read-only access.
- COORDINADOR with the `auditoria:ver_propio` permission MUST only see audit logs and metrics associated with subjects (`materia_id`) for which they have a current, active assignment.
- All other users MUST be rejected with a 403 Forbidden status.

#### Scenario: Admin retrieves global logs
- GIVEN an authenticated user with ADMIN role
- WHEN they request the audit logs without filters
- THEN the system returns the logs across all subjects and actors in the tenant.

#### Scenario: Coordinator retrieves scoped logs
- GIVEN an authenticated Coordinator with `auditoria:ver_propio` permission assigned only to Subject A
- WHEN they request audit logs
- THEN the system returns only logs where `materia_id` is Subject A
- AND logs for other subjects are omitted.

#### Scenario: Coordinator requests unauthorized subject logs
- GIVEN an authenticated Coordinator assigned only to Subject A
- WHEN they request audit logs filtering for Subject B
- THEN the system rejects the request with 403 Forbidden or ValueError.

### Requirement: Interaction Metrics Aggregations
The system MUST provide direct database aggregations for usage metrics.
- The metrics MUST include: actions per day, communications status counts per teacher, and detailed action counts grouped by teacher and subject.

#### Scenario: Retrieve interaction metrics
- GIVEN an authenticated ADMIN user requesting metrics
- WHEN they query the metrics endpoint
- THEN the system returns aggregated daily counts, communication status groups per teacher, and action counts per teacher-subject combination.

### Requirement: Filterable Paginated Audit Log Stream
The system MUST expose a stream of raw audit log entries with filters.
- Filters MUST support: date range (from/to), `materia_id`, `actor_id`, and actor's active state.
- The logs MUST be returned paginated and support a configurable maximum limit of recent records (default 200).

#### Scenario: Query logs with date range and actor filter
- GIVEN audit log entries in the database
- WHEN an Admin queries logs filtering by actor X and a date range
- THEN the system returns matching audit log entries within the limit.
