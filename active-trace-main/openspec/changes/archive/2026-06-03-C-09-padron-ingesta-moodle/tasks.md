# Tasks: C-09 padron-ingesta-moodle

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 500 - 700 lines |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (DB) → PR 2 (Service) → PR 3 (API/LMS) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | DB y Repository | PR 1 | Base `main`; Modelos, migraciones, persistencia (incluye tests) |
| 2 | Lógica Service y Schemas | PR 2 | Base PR 1; Reglas de negocio y upsert transaccional |
| 3 | API HTTP e Integración LMS | PR 3 | Base PR 2; Router, cliente Moodle WS y resiliencia con Tenacity |

## Phase 1: Foundation (Models & Persistence)

- [x] 1.1 Crear `backend/app/models/padron.py` con entidades `VersionPadron` (con flag `activa`) y `EntradaPadron`.
- [x] 1.2 Ejecutar Alembic para generar la migración de schema en `backend/alembic/versions/`.
- [x] 1.3 Crear `backend/app/repositories/padron_repository.py` con método para desactivar versión previa y crear la nueva atómicamente (`bulk_insert`).
- [x] 1.4 Escribir Unit Tests para el repository asegurando el correcto manejo transaccional de desactivación.

## Phase 2: Core Implementation (Schemas & Service)

- [x] 2.1 Crear `backend/app/schemas/padron.py` con `EntradaPadronCreate` y `PadronImportRequest`.
- [x] 2.2 Crear `backend/app/services/padron_service.py` con lógica de validación e inyección del repository.
- [x] 2.3 Implementar mapeo de PII y resolución de `usuario_id` en `padron_service.py` de forma performante.
- [x] 2.4 Escribir Unit Tests para el service verificando las reglas de negocio (ej. inserciones sin `usuario_id`).

## Phase 3: Integration (Moodle Client & API Router)

- [x] 3.1 Crear `backend/app/integrations/moodle_ws.py` implementando HTTP requests resilientes con `Tenacity`.
- [x] 3.2 Crear `backend/app/routers/padron.py` exponiendo `/api/padron/import` (archivo local) y `/api/padron/sync` (LMS).
- [x] 3.3 Registrar el nuevo router en `backend/app/main.py`.

## Phase 4: Verification (Integration & E2E)

- [x] 4.1 Escribir Integration Test mockeando fallo HTTP 502 de Moodle WS y verificando retry behavior.
- [x] 4.2 Escribir E2E Test que envíe un CSV al endpoint de carga manual y valide el resultado exitoso en DB y HTTP 200.
