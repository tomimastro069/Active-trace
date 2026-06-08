# Design: c-23-frontend-coordinacion

## Context
The backend for the coordination domain is already shipped and contract-stable:

| Domain | Router prefix | Key endpoints used |
|--------|---------------|--------------------|
| Equipos | `/api/v1/equipos` | `GET /mis-equipos`, `POST /masiva`, `POST /clonar`, `PATCH /vigencia`, `GET /exportar` |
| Avisos | `/api/v1/avisos` | `POST /`, `GET /activos`, `POST /ack` |
| Tareas | `/api/v1/tareas` | `GET /`, `POST /`, `GET /{id}`, `PATCH /{id}`, `GET /{id}/comentarios`, `POST /{id}/comentarios` |
| Monitor | `/api/v1/analisis` | `GET /monitor?materia_id&cohorte_id&…` |

The frontend already has (from C-21 / C-22): the Axios client with transparent refresh (`@/shared/services/api`), `AuthContext`/`useAuth`, `AuthGuard`, `Layout` shell, TanStack Query provider in `App.tsx`, and a feature-folder convention under `src/features/`.

This change is governance **BAJO** (frontend, no critical-domain logic). Full autonomy provided tests pass.

## Goals / Non-Goals

**Goals**
- Mirror the real backend contracts exactly (paths, query params, request/response shapes) in typed services.
- Reuse the existing shell, query client and auth — no new cross-cutting infra.
- Role-gate the coordination navigation to COORDINADOR / ADMIN.
- Keep components small (<200 LOC) and write-paths invalidate their query caches.

**Non-Goals**
- No backend or migration changes.
- No finance/admin screens (C-24).
- No rich encuentros/coloquios panels — coordination operates the team/avisos/tareas/monitor core here.

## Architecture

```
src/features/coordinacion/
├── types/
│   └── coordinacion.types.ts        # Asignacion, Aviso, Tarea, Comentario, MonitorItem, enums
├── services/
│   ├── equipos.service.ts           # /equipos/*
│   ├── avisos.service.ts            # /avisos/*
│   ├── tareas.service.ts            # /tareas/*
│   ├── monitor.service.ts           # /analisis/monitor
│   └── __tests__/                   # Vitest service tests (mocked api)
├── pages/
│   ├── EquiposPage.tsx              # mis-equipos + acciones (masiva/clonar/vigencia/export)
│   ├── AvisosPage.tsx               # ABM avisos + lista activos + ack
│   ├── TareasPage.tsx               # workflow board + detalle/comentarios
│   ├── MonitorCoordinacionPage.tsx  # monitor transversal con filtros
│   └── __tests__/                   # smoke/integration (TareasPage)
└── components/
    ├── AvisoForm.tsx                # form de alta con selector de alcance
    ├── TareaCard.tsx                # tarjeta de tarea + cambio de estado
    └── TareaDetalle.tsx             # panel de comentarios en hilo
```

Data flow stays unidirectional and consistent with the rest of the SPA:

```
Page/Component ──useQuery/useMutation──▶ feature service ──▶ shared api (axios) ──▶ /api/v1/...
       ▲                                                                                │
       └────────────────── TanStack Query cache (invalidate on write) ◀────────────────┘
```

## Key Decisions

### D1 — One service object per domain, typed from the backend schema
Each service is a plain object of async functions returning `response.data`, exactly like `academico.service.ts`. Types are transcribed from the Pydantic response models (`AsignacionResponse`, `AvisoResponse`, `TareaResponse`, `ComentarioTareaResponse`, `MonitorResponse`) so the compiler catches drift. Enums (`EstadoTarea`, `AlcanceAviso`) are modeled as string-literal unions matching the backend enum *values* (`"Pendiente"`, `"En progreso"`, `"Global"`, `"PorMateria"`, …).

### D2 — Monitor uses query params, not path params
The real endpoint is `GET /analisis/monitor?materia_id&cohorte_id&regional&comision&search&estado_actividad&desde_fecha&hasta_fecha`. The service passes these via Axios `params`, omitting empties. (Note: C-22's `academico.service.getMonitor` predates the final contract; the coordination monitor service targets the shipped signature with the required `materia_id`/`cohorte_id`.)

### D3 — CSV export via blob
`GET /equipos/exportar` returns `text/csv`. The service requests `responseType: 'blob'` and the page triggers a browser download with an object URL, matching the backend `Content-Disposition` filename.

### D4 — Mutations invalidate, queries cache
Writes (`POST /masiva`, `POST /clonar`, `PATCH /vigencia`, `POST /avisos`, `POST /ack`, `POST /tareas`, `PATCH /tareas/{id}`, `POST comentarios`) are `useMutation` calls that invalidate the relevant `queryKey` on success, so lists refresh without manual refetch.

### D5 — Role-gated navigation
The "Coordinación" sidebar block renders only when the session roles include `COORDINADOR` or `ADMIN`, consistent with the existing PROFESOR/TUTOR gating in `Layout.tsx`. Route-level authorization remains enforced server-side (fail-closed 403); the UI gate is convenience only.

## Risks / Trade-offs
- **Contract drift**: mitigated by transcribing types directly from routers/schemas; a `tsc` run is part of verification.
- **Light evaluation UI**: coordination can create/list convocatorias later; this change intentionally keeps the surface to team/avisos/tareas/monitor to stay within a reviewable budget.
- **No E2E**: only Vitest unit/integration here, consistent with C-22.

## Migration / Compatibility
Pure additive frontend change. No persisted state, no API changes, no breaking edits to existing features — only additive routes in `App.tsx` and an additive nav block in `Layout.tsx`. Rollback = delete the feature folder and revert the two shell edits.
