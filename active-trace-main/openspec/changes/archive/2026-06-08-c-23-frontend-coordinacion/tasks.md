# Tasks: c-23-frontend-coordinacion

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~520-580 lines |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (Types/Services/Nav) → PR 2 (Equipos + Avisos) → PR 3 (Tareas + Monitor) |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Types, Services, App routing, Layout nav | PR 1 | Base infra for the feature |
| 2 | Equipos + Avisos pages/components | PR 2 | Depends on PR 1 |
| 3 | Tareas workflow + Monitor + tests | PR 3 | Depends on PR 1 |

## Phase 1: Foundation (Types & API Services)

- [x] 1.1 Create `frontend/src/features/coordinacion/types/coordinacion.types.ts` with interfaces for Asignacion, Aviso (+AlcanceAviso), Tarea (+EstadoTarea), ComentarioTarea, MonitorItem and request payloads.
- [x] 1.2 Create `frontend/src/features/coordinacion/services/equipos.service.ts` (`mis-equipos`, `masiva`, `clonar`, `vigencia`, `exportar` blob).
- [x] 1.3 Create `frontend/src/features/coordinacion/services/avisos.service.ts` (`crear`, `activos`, `ack`).
- [x] 1.4 Create `frontend/src/features/coordinacion/services/tareas.service.ts` (`list`, `create`, `get`, `updateEstado`, `comentarios`, `addComentario`).
- [x] 1.5 Create `frontend/src/features/coordinacion/services/monitor.service.ts` (`getMonitor` with query params).

## Phase 2: App Shell and Routing

- [x] 2.1 Modify `frontend/src/shared/components/Layout.tsx` to add a role-gated "Coordinación" nav block (COORDINADOR / ADMIN) linking to equipos, avisos, tareas and monitor.
- [x] 2.2 Modify `frontend/src/App.tsx` to register the new private routes under the Layout/AuthGuard.

## Phase 3: Pages & Components

- [x] 3.1 Create `frontend/src/features/coordinacion/pages/EquiposPage.tsx` (mis-equipos table + masiva/clonar/vigencia forms + CSV export).
- [x] 3.2 Create `frontend/src/features/coordinacion/components/AvisoForm.tsx` (scope-aware advisory create form).
- [x] 3.3 Create `frontend/src/features/coordinacion/pages/AvisosPage.tsx` (active list + ack + embeds AvisoForm).
- [x] 3.4 Create `frontend/src/features/coordinacion/components/TareaCard.tsx` (task card + state change).
- [x] 3.5 Create `frontend/src/features/coordinacion/components/TareaDetalle.tsx` (threaded comments panel).
- [x] 3.6 Create `frontend/src/features/coordinacion/pages/TareasPage.tsx` (workflow board + create/delegate + detail).
- [x] 3.7 Create `frontend/src/features/coordinacion/pages/MonitorCoordinacionPage.tsx` (filters + results table + empty state).

## Phase 4: Verification

- [x] 4.1 Write Vitest unit tests for `equipos.service.ts`, `avisos.service.ts`, `tareas.service.ts` and `monitor.service.ts` (mocked api).
- [x] 4.2 Write a smoke/integration test for `TareasPage.tsx` (render + create + state transition with mocked services).
- [x] 4.3 Run `tsc --noEmit` and the Vitest suite; confirm clean. (tsc exit 0; full suite 9 files / 28 tests passing.)
