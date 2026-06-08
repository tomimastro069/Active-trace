## Exploration: c-22-frontend-academico-docente

### Current State
- The frontend shell (`C-21`) is initialized with React 19, Vite, TailwindCSS v4, TanStack Query, and a central HTTP/API client with transparent token refresh.
- Routing exists for `/login`, `/unauthorized`, and a `/dashboard` placeholder.
- The backend contains fully functional APIs for:
  - `calificaciones`: Preview CSV, Import CSV, Import Completion CSV, Clear grades, configure/retrieve threshold.
  - `analisis`: Fetch delayed students, ranking, quick reports, final grades, TPs pending correction, and general monitor.
  - `comunicaciones`: Send bulk messages, template preview, list communications, get summary of batches, approve/cancel batches.

### Affected Areas
- `frontend/src/App.tsx` — Add routing for `/comisiones/:materiaId/:cohorteId` (Management of commission), `/comisiones` (List of commissions), and `/monitor-seguimiento` (Tutor tracking view).
- `frontend/src/features/academico-docente/` [NEW] — Create all page layouts, components, and services under this feature folder.
- `frontend/src/shared/components/Layout.tsx` [NEW] — Create a dashboard layout wrapper with responsive sidebar navigation, logout action, user profile info, and permissions-based routing guards.

### Approaches
1. **Unified Dashboard View with Tabs** — Create a single dashboard page for a commission (`/comisiones/:materiaId/:cohorteId`) structured with interactive tabs: Calificaciones (Import & Umbral), Alumnos Atrasados, Ranking & Reportes, Entregas sin Corregir, and Comunicaciones.
   - Pros: Highly integrated, easy to share state, low navigation friction, clear dashboard aesthetic.
   - Cons: Large page component if not separated cleanly into modular children.
   - Effort: Medium

2. **Multi-page/Split Route Navigation** — Separate each function into distinct routes (e.g., `/comisiones/:id/import`, `/comisiones/:id/atrasados`, etc.).
   - Pros: Isolated pages, smaller components.
   - Cons: High navigation overhead, redundant fetching of commission/subject details across route changes, suboptimal user experience.
   - Effort: Medium-High

### Recommendation
**Approach 1 (Unified Dashboard View with Tabs)** is recommended. It matches premium dashboard design patterns, provides a smoother user experience, and allows sub-components to react directly to shared context (like the active `materiaId`, `cohorteId`, and the configured threshold values) without extra network requests or complex route structures.

### Risks
- **Data payload volume**: If imports or student list files are very large, rendering tables of hundreds of students in React could cause minor lag. *Mitigation*: Implement virtualized lists or clean paginated table components.
- **WebSocket/Real-time tracking of communications**: The requirement mentions "tracking of state in real time". The backend currently exposes polling endpoints for batch statuses. *Mitigation*: Implement short-polling (e.g., TanStack Query `refetchInterval` of 3–5 seconds) when active messages are in the `PENDIENTE` or `ENVIANDO` states.

### Ready for Proposal
Yes. The requirements and backend integrations are clear. We can proceed to generate the change proposal (`/opsx:propose c-22-frontend-academico-docente`).
