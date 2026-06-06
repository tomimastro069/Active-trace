# Tasks: Avisos y Acknowledgment (C-15)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 250 - 350 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Modelos, API y Lógica de Negocio (Full Feature) | PR 1 | Se mantendrá en un solo PR ya que es un alcance acotado y seguro. |

## Phase 1: Database & Models (Strict TDD)
- [x] 1.1 Crear `backend/app/models/aviso.py` definiendo `Aviso` y `AcknowledgmentAviso` heredando de `TimestampedTenant`.
- [x] 1.2 Modificar `backend/app/models/__init__.py` exportando los nuevos modelos.
- [x] 1.3 Generar migración inicial con `alembic revision --autogenerate -m "create_aviso_tables"`.

## Phase 2: Core Implementation (Strict TDD)
- [x] 2.1 Crear schemas Pydantic en `backend/app/schemas/aviso.py` (`AvisoBase`, `AvisoCreate`, `AvisoResponse`, `AlcanceEnum`).
- [x] 2.2 RED: Escribir tests en `backend/tests/unit/test_aviso_repository.py` validando el filtrado cruzado de asignaciones vs alcance.
- [x] 2.3 GREEN/REFACTOR: Crear `backend/app/repositories/aviso.py` y lograr que los tests del repositorio pasen.
- [x] 2.4 RED: Escribir tests en `backend/tests/unit/test_aviso_service.py` validando RBAC (publicación) y contadores de Ack.
- [x] 2.5 GREEN/REFACTOR: Crear `backend/app/services/aviso.py` orquestando repositorio y validaciones, y hacer pasar los tests.

## Phase 3: Integration & API (Strict TDD)
- [x] 3.1 RED: Escribir tests E2E en `backend/tests/integration/test_aviso_api.py` para los endpoints POST, GET `/activos` y POST `/ack`.
- [x] 3.2 GREEN: Crear `backend/app/api/v1/routers/avisos.py` con los endpoints.
- [x] 3.3 GREEN/REFACTOR: Registrar el router en `backend/app/main.py` y verificar que la suite completa pase.

## Phase 4: Cleanup & Doc
- [x] 4.1 Verificar linters y formateo de código en todos los archivos modificados.
- [x] 4.2 Documentar dependencias de migración o consideraciones en el CHANGELOG si fuera necesario.

## Phase 5: Post-Verification Fixes (Strict TDD)
- [x] 5.1 Arreglar Router (`backend/app/api/v1/routers/avisos.py`): Reemplazar `get_db` y `get_current_user` mockeados por dependencias reales de `app.core.dependencies`.
- [x] 5.2 Lógica de Acknowledgment (`backend/app/services/aviso.py` y repos): Implementar la inserción real en la tabla `AcknowledgmentAviso`.
- [x] 5.3 Filtrar Avisos Activos (`backend/app/repositories/aviso.py`): Modificar `obtener_activos_para_usuario` para que excluya los avisos con acuse ya registrado.
- [x] 5.4 Test de Integración (`backend/tests/integration/test_aviso_api.py`): Eliminar dependencias de fixtures inexistentes (`client`, `token_docente`) e instanciar `AsyncClient` usando `app.dependency_overrides` correctamente.
