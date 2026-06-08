# Design: c-22-frontend-academico-docente

## Technical Approach

The change implements the Teacher/Professor frontend capabilities defined in `c-22`. It will follow a feature-based architecture within `frontend/src/features/academico-docente`. The technical strategy relies on React Router for routing (extending `App.tsx` and adding a new `Layout.tsx`), TanStack Query for data fetching and status polling, and standard React Hook Form components for form handling. We will use a unified dashboard approach where a single parent component manages the commission context (`materiaId` and `cohorteId`) and nested tabs manage individual domains (Grades, Delayed Students, Rankings, Communication).

## Architecture Decisions

### Decision: State Management for Commission Context

**Choice**: Use React Router URL parameters (`/comisiones/:materiaId/:cohorteId`) as the source of truth, combined with a local Context provider (`CommissionProvider`) to pass `materiaId`, `cohorteId`, and the configured `umbral` down to the tab components.
**Alternatives considered**: Zustand global store or passing props deeply.
**Rationale**: URL parameters allow deep linking. A local context avoids polluting the global state while easily sharing the active commission data with all nested tabs.

### Decision: Tracking Communication State

**Choice**: Short-polling via TanStack Query (`refetchInterval: 5000`) on the `/comisiones/lotes/:loteId` endpoint when a batch has `PENDIENTE` or `ENVIANDO` status.
**Alternatives considered**: WebSockets or Server-Sent Events (SSE).
**Rationale**: The backend currently implements polling endpoints. Adding WS/SSE would require backend architectural changes outside the scope of C-22. TanStack Query polling handles this efficiently.

## Data Flow

```text
  React UI (Dashboard Tabs)
        │
        ▼ (Mutations & Queries via Axios API Client)
  TanStack Query Cache ───┬───► (GET /api/v1/analisis/*)
        │                 ├───► (POST /api/v1/calificaciones/*)
        ▼                 └───► (POST /api/v1/comunicaciones/*)
  React Router (URL State)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `frontend/src/App.tsx` | Modify | Add private routes for `/comisiones`, `/comisiones/:materiaId/:cohorteId`, and `/monitor-seguimiento`. |
| `frontend/src/shared/components/Layout.tsx` | Create | App shell with sidebar, user profile info, and navigation links. |
| `frontend/src/features/academico-docente/pages/ComisionDashboard.tsx` | Create | Parent view that extracts URL params and renders the tabs. |
| `frontend/src/features/academico-docente/pages/MonitorSeguimientoPage.tsx` | Create | Standalone view for the tutor/teacher monitor filters. |
| `frontend/src/features/academico-docente/components/TabCalificaciones.tsx` | Create | UI for importing grades and configuring umbral. |
| `frontend/src/features/academico-docente/components/TabAtrasados.tsx` | Create | Table component for delayed students. |
| `frontend/src/features/academico-docente/components/TabTrabajosSinCorregir.tsx` | Create | UI for importing LMS completion report, crossing it with grades, and exporting pending corrections to CSV. |
| `frontend/src/features/academico-docente/components/TabComunicaciones.tsx` | Create | UI for enqueueing and polling communications. |
| `frontend/src/features/academico-docente/services/academico.service.ts` | Create | Axios API calls for `analisis` and `calificaciones` modules. |
| `frontend/src/features/academico-docente/services/comunicaciones.service.ts` | Create | Axios API calls for the `comunicaciones` module. |
| `frontend/src/features/academico-docente/types/academico.types.ts` | Create | TypeScript interfaces for analysis and grades responses. |

## Interfaces / Contracts

```typescript
export interface CommissionContextType {
  materiaId: string;
  cohorteId: string;
  umbralPct: number;
  setUmbralPct: (val: number) => void;
}

export interface AlumnoAtrasado {
  padron_id: string;
  nombre: string;
  apellido: string;
  email: string;
  tareas_faltantes: string[];
  nota_actual?: number;
  estado_general: string;
}
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | API service functions | Mock Axios calls to verify correct URL endpoints and payloads. |
| Unit | Context Provider | Render custom hook to verify context values are provided. |
| Integration | Component Render | Use React Testing Library with mocked TanStack Query to test tab rendering and interactions (e.g. file upload simulation). |

## Migration / Rollout

No migration required. The frontend features will become accessible to users with `PROFESOR` or `TUTOR` roles immediately upon deployment.

## Open Questions

- [ ] None.
