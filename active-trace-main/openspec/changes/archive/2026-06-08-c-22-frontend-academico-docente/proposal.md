# Proposal: c-22-frontend-academico-docente

## Intent
Implement the React frontend interfaces for the Teacher/Professor to manage commissions, view student tracking metrics, import grades and checkouts, and dispatch communications for delayed students.

## Scope

### In Scope
- **Commission Dashboard** (`/comisiones/:materiaId/:cohorteId`): Unified tabbed interface for:
  - *Calificaciones & Umbral*: Upload grades CSV, preview activities/students, set approval threshold, clear grades.
  - *Alumnos Atrasados*: Tabular view of students below threshold/missing assignments, with filters.
  - *Ranking & Reportes*: Graphical metrics and final grades.
  - *Entregas sin Corregir*: Completion report import and CSV export.
  - *Comunicaciones*: Select students, preview template, send to queue, track state.
- **Tutor/Teacher Monitor** (`/monitor-seguimiento`): Comprehensive filters for assigned students.
- **App Layout**: Sidebar/header with responsive drawers, identity info, and role-based links.
- **Service Integration**: Services calling Axios endpoints for `/calificaciones`, `/analisis`, and `/comunicaciones`.
- **Component Tests**: Unit/integration tests with MSW (Mock Service Worker) or local mocks.

### Out of Scope
- Backend changes or Alembic migrations (already completed in C-10, C-11, C-12).
- Coordination-specific screens (C-23) or Admin/Finance screens (C-24).

## Capabilities

### New Capabilities
- `frontend-academico-docente`: UI presentation layer for teachers to manage grades, configure thresholds, view delayed students, and dispatch communication templates.

### Modified Capabilities
- None

## Approach
- Create React 19 components under `src/features/academico-docente/` following a clean modular design.
- Create `/comisiones` parent route to list assigned commissions (using token user assignment details).
- Use TanStack Query for caching and polling status of communication batches.
- Create a reusable `Layout` component in `src/shared/components/` and wrap all private routes with it in `src/App.tsx`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `frontend/src/App.tsx` | Modified | Add routes for commission list, commission details, and tutor monitor. |
| `frontend/src/features/academico-docente/` | New | Feature folder: components, pages, services, and tests. |
| `frontend/src/shared/components/Layout.tsx` | New | Dashboard navigation layout. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Rendering heavy student tables | Med | Use simple pagination or virtual scroll. |
| Stale communication batch statuses | High | Poll status endpoint every 5s for active queues. |

## Rollback Plan
Revert changes to `frontend/src/App.tsx` and delete the new `frontend/src/features/academico-docente` and `Layout.tsx` files.

## Dependencies
- Backend services running (`C-12` completed).
- React Auth Guard shell (`C-21` completed).

## Success Criteria
- [ ] Teachers can upload grades, configure umbral, and see delayed student list.
- [ ] Users can preview and enqueue bulk communications and monitor queue statuses.
- [ ] All components are fully responsive and pass tests under Vitest.
