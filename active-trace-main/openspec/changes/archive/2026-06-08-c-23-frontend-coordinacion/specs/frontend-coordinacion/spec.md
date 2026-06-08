# Spec: frontend-coordinacion

## ADDED Requirements

### Requirement: Teaching team management UI
The system SHALL provide a Coordinación route `/equipos` where a user with role COORDINADOR or ADMIN can view their teaching teams and perform bulk team operations against the `/api/v1/equipos` endpoints.

#### Scenario: View my teams
- **WHEN** a coordinator opens `/equipos`
- **THEN** the page calls `GET /equipos/mis-equipos` and renders one row per assignment showing role, context (materia/carrera/cohorte) and validity state

#### Scenario: Bulk assignment
- **WHEN** the coordinator submits the bulk-assignment form with one or more `usuario_ids`, a `rol_id`, a context and a `desde` date
- **THEN** the page calls `POST /equipos/masiva` and, on success, invalidates and refreshes the teams list

#### Scenario: Clone a team between periods
- **WHEN** the coordinator submits source materia/cohorte, target materia/cohorte and a new validity start
- **THEN** the page calls `POST /equipos/clonar` and surfaces a conflict message when the target already has active assignments (409)

#### Scenario: Export team to CSV
- **WHEN** the coordinator clicks "Exportar"
- **THEN** the page calls `GET /equipos/exportar` requesting a blob and triggers a browser download named `equipo_docente.csv`

### Requirement: Advisory (avisos) publication and acknowledgment UI
The system SHALL provide a Coordinación route `/avisos` where a coordinator can publish scoped advisories and any authenticated user can view active advisories and acknowledge those requiring it.

#### Scenario: Publish a scoped advisory
- **WHEN** the coordinator completes the advisory form choosing an `alcance` (Global, PorMateria, PorCohorte or PorRol), severity, title, body and a validity window
- **THEN** the page calls `POST /avisos/` and, on success, the new advisory appears in the active list

#### Scenario: List active advisories
- **WHEN** the page loads
- **THEN** it calls `GET /avisos/activos` and renders the advisories ordered by priority with their severity and scope

#### Scenario: Acknowledge an advisory
- **WHEN** the user acknowledges an advisory that has `requiere_ack`
- **THEN** the page calls `POST /avisos/ack` with the `aviso_id` and the advisory is marked as acknowledged

### Requirement: Internal task workflow UI
The system SHALL provide a Coordinación route `/tareas` where a coordinator can create, delegate, comment on and transition internal tasks through their workflow states against `/api/v1/tareas`.

#### Scenario: List tasks
- **WHEN** the coordinator opens `/tareas`
- **THEN** the page calls `GET /tareas/` and groups tasks by state (Pendiente, En progreso, Resuelta, Cancelada)

#### Scenario: Create and delegate a task
- **WHEN** the coordinator submits a task with a description and an `asignado_a` user
- **THEN** the page calls `POST /tareas/` and the new task appears in the Pendiente column

#### Scenario: Change task state
- **WHEN** the coordinator selects a new state for a task
- **THEN** the page calls `PATCH /tareas/{id}` with the new `estado` and the task moves to the corresponding column

#### Scenario: Thread comments on a task
- **WHEN** the coordinator opens a task detail and posts a comment
- **THEN** the page calls `POST /tareas/{id}/comentarios` and the comment appears in the thread fetched via `GET /tareas/{id}/comentarios`

### Requirement: Cross-cutting follow-up monitor UI
The system SHALL provide a Coordinación route `/monitor-coordinacion` that renders the cross-cutting follow-up monitor for a commission with filters, consuming `GET /api/v1/analisis/monitor`.

#### Scenario: Filtered monitor query
- **WHEN** the coordinator provides `materia_id` and `cohorte_id` and optional filters (regional, comisión, search, estado_actividad, date range)
- **THEN** the page calls `GET /analisis/monitor` with those query parameters and renders the returned follow-up rows

#### Scenario: Empty result
- **WHEN** the monitor query returns no rows
- **THEN** the page shows an explicit empty-state message instead of an empty table

### Requirement: Role-gated coordination navigation
The system SHALL show the Coordinación navigation section only to sessions whose roles include COORDINADOR or ADMIN, while server-side authorization remains the enforcing authority.

#### Scenario: Coordinator sees the section
- **WHEN** a user whose session roles include COORDINADOR or ADMIN renders the app shell
- **THEN** the sidebar shows the "Coordinación" block with links to equipos, avisos, tareas and the coordination monitor

#### Scenario: Non-coordinator does not see the section
- **WHEN** a user without COORDINADOR or ADMIN roles renders the app shell
- **THEN** the "Coordinación" block is not displayed
