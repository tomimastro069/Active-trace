# Proposal: c-23-frontend-coordinacion

## Intent
Implement the React frontend interfaces for the COORDINADOR / ADMIN roles to run the academic operation: manage teaching teams (assignments), publish and track advisories (avisos), drive the internal task workflow, and consult the cross-cutting follow-up monitor. This is the presentation layer over the backends already shipped in C-08, C-13, C-14, C-15, C-16 and C-17.

## Scope

### In Scope
- **Equipos Docentes** (`/equipos`): view "mis-equipos", bulk assignment (masiva), clone a team between periods (clonar), batch update of validity (vigencia) and CSV export. Consumes `C-08`.
- **Avisos** (`/avisos`): ABM of advisories with scope selector (Global / PorMateria / PorCohorte / PorRol), severity, validity window, order and `requiere_ack`; list active advisories and acknowledge. Consumes `C-15`.
- **Tareas Internas** (`/tareas`): list assigned tasks, create/delegate, change state through the workflow (Pendiente → En progreso → Resuelta / Cancelada) and threaded comments. Consumes `C-16`.
- **Monitor de Coordinación** (`/monitor-coordinacion`): cross-cutting follow-up monitor for a commission with regional/comision/search/state/date-range filters (F2.7, F2.9). Consumes `C-11`.
- **Navigation**: extend the shared `Layout` sidebar with a role-gated "Coordinación" section (COORDINADOR / ADMIN).
- **Service Integration**: typed Axios services for `/equipos`, `/avisos`, `/tareas`, `/analisis/monitor`.
- **Tests**: Vitest unit tests for the new services and a smoke/integration test for the task workflow page.

### Out of Scope
- Backend changes or Alembic migrations (already completed in C-08, C-13, C-14, C-15, C-16, C-17).
- Finance/Admin screens — liquidaciones, facturas, auditoría, estructura académica (those belong to C-24).
- Teacher/Professor commission screens (already shipped in C-22).
- Deep encuentros/coloquios admin UI beyond what coordination needs to operate; full evaluation panels stay light (read/create only) and can be expanded later.

## Capabilities

### New Capabilities
- `frontend-coordinacion`: UI presentation layer for coordinators to manage teaching teams, publish advisories with acknowledgment, run the internal task workflow, and consult the cross-cutting follow-up monitor.

### Modified Capabilities
- None (backend contracts unchanged).

## Approach
- Create React 18 + TypeScript components under `src/features/coordinacion/` following the feature-based structure already used by `academico-docente` (`{components,hooks,pages,services,types}`).
- One typed Axios service per domain (`equipos`, `avisos`, `tareas`, `monitor`) calling the real v1 endpoints, all routed through the centralized `@/shared/services/api` client (transparent refresh inherited).
- Use TanStack Query for fetching/caching and mutations with cache invalidation on writes.
- Extend `src/shared/components/Layout.tsx` with a role-gated "Coordinación" nav block and register the new private routes in `src/App.tsx`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `frontend/src/App.tsx` | Modified | Add private routes for equipos, avisos, tareas and the coordination monitor. |
| `frontend/src/shared/components/Layout.tsx` | Modified | Add role-gated "Coordinación" sidebar section. |
| `frontend/src/features/coordinacion/` | New | Feature folder: types, services, pages, components and tests. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Endpoint contract drift vs. backend (query-param vs path) | Med | Types/services derived directly from the v1 routers and Pydantic schemas. |
| Heavy team/task tables | Low | Simple pagination via `skip`/`limit` already supported by `/tareas`. |
| Scope creep into encuentros/coloquios full UI | Med | Keep evaluation/encuentros UI minimal; defer rich panels. |

## Rollback Plan
Revert the changes to `frontend/src/App.tsx` and `frontend/src/shared/components/Layout.tsx`, and delete the new `frontend/src/features/coordinacion/` folder. No backend or DB impact.

## Dependencies
- `C-21` frontend shell + auth (completed) — Layout, AuthGuard, api client.
- `C-08` equipos-docentes, `C-15` avisos-y-acknowledgment, `C-16` tareas-internas (completed) — backend contracts.
- `C-11` analisis-atrasados-reportes (completed) — monitor endpoint.

## Success Criteria
- [ ] Coordinators can view their teams and run bulk assignment, clone, vigencia update and CSV export.
- [ ] Coordinators can publish a scoped advisory and see active advisories; users can acknowledge `requiere_ack` advisories.
- [ ] Coordinators can create/delegate a task and move it through the workflow with comments.
- [ ] The coordination monitor renders filtered follow-up rows for a commission.
- [ ] New services and the task workflow page pass under Vitest; `tsc` is clean.
