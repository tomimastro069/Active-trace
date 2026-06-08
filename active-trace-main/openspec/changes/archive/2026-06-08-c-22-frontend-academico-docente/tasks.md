# Tasks: c-22-frontend-academico-docente

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~450-500 lines |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (Core/Services) → PR 2 (Dashboard) → PR 3 (Monitor) |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Types, Services, App Routing, Layout | PR 1 | Base infrastructure for feature |
| 2 | Commission Dashboard & Tab Components | PR 2 | Depends on PR 1 |
| 3 | Monitor Seguimiento View & Verification | PR 3 | Depends on PR 1 |

## Phase 1: Foundation (Types & API Services)

- [x] 1.1 Create `frontend/src/features/academico-docente/types/academico.types.ts` with interfaces for grades, students, and context.
- [x] 1.2 Create `frontend/src/features/academico-docente/services/academico.service.ts` for analysis and grades module APIs.
- [x] 1.3 Create `frontend/src/features/academico-docente/services/comunicaciones.service.ts` for batch communications.

## Phase 2: App Shell and Routing

- [x] 2.1 Create `frontend/src/shared/components/Layout.tsx` for layout structure.
- [x] 2.2 Modify `frontend/src/App.tsx` to add layout wrapper and private routes for the new views.

## Phase 3: Dashboard & Components

- [x] 3.1 Create `frontend/src/features/academico-docente/pages/ComisionDashboard.tsx` with URL param extraction and tab navigation.
- [x] 3.2 Create `frontend/src/features/academico-docente/components/TabCalificaciones.tsx` for grade import form and umbral setting.
- [x] 3.3 Create `frontend/src/features/academico-docente/components/TabAtrasados.tsx` for student listing table.
- [x] 3.4 Create `frontend/src/features/academico-docente/components/TabComunicaciones.tsx` for enqueueing and polling statuses.
- [x] 3.5 Create `frontend/src/features/academico-docente/pages/MonitorSeguimientoPage.tsx` as standalone view.
- [x] 3.6 Create `frontend/src/features/academico-docente/components/TabTrabajosSinCorregir.tsx` for CSV import, grading cross-reference, and exporting pending corrections.
- [x] 3.7 Integrate `TabTrabajosSinCorregir` as a new tab ("Trabajos sin Corregir") in `ComisionDashboard.tsx`.

## Phase 4: Verification

- [x] 4.1 Write unit tests for API services.
- [x] 4.2 Verify component routing and data flow in `ComisionDashboard.tsx`.
- [x] 4.3 Verify `TabTrabajosSinCorregir` CSV upload, crossing logic, and CSV download.
