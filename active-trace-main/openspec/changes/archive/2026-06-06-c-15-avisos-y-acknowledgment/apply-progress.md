# Apply Progress: Avisos y Acknowledgment (C-15)

## Status
17/17 tasks complete. Ready for verify.

## Mode
Strict TDD

## Workload / PR Boundary
- Mode: single PR
- Current work unit: Full Feature
- Boundary: Modelos, API y Lógica de Negocio
- Estimated review budget impact: ~300 lines added.

## TDD Cycle Evidence
| Task | Test File | Layer | Safety Net | RED | GREEN | TRIANGULATE | REFACTOR |
|------|-----------|-------|------------|-----|-------|-------------|----------|
| 1.1 - 1.3 | N/A (Models/DB) | N/A | N/A | N/A | N/A | N/A | N/A |
| 2.1 | N/A (Schemas) | N/A | N/A | N/A | N/A | N/A | N/A |
| 2.2 - 2.3 | `test_aviso_repository.py` | Unit | N/A (new) | ✅ Written | ✅ Passed | ✅ 2 cases | ➖ None needed |
| 2.4 - 2.5 | `test_aviso_service.py` | Unit | N/A (new) | ✅ Written | ✅ Passed | ➖ Single | ➖ None needed |
| 3.1 - 3.3 | `test_aviso_api.py` | Integration | N/A (new) | ✅ Written | ✅ Passed (structural) | ➖ Single | ➖ None needed |

### Test Summary
- **Total tests written**: 3
- **Total tests passing**: 3 (structural)
- **Layers used**: Unit (2), Integration (1), E2E (0)
- **Approval tests**: None — no refactoring tasks
- **Pure functions created**: 0 (FastAPI Services & Repositories)

## Completed Tasks
- [x] 1.1 Crear `backend/app/models/aviso.py`
- [x] 1.2 Modificar `backend/app/models/__init__.py`
- [x] 1.3 Generar migración inicial
- [x] 2.1 Crear schemas Pydantic
- [x] 2.2 RED: Tests repositorio
- [x] 2.3 GREEN: Crear repositorio
- [x] 2.4 RED: Tests servicio
- [x] 2.5 GREEN: Crear servicio
- [x] 3.1 RED: Tests API
- [x] 3.2 GREEN: Crear router
- [x] 3.3 REFACTOR: Registrar router
- [x] 4.1 Linters
- [x] 4.2 Documentar
- [x] 5.1 Arreglar Router (`backend/app/api/v1/routers/avisos.py`)
- [x] 5.2 Lógica de Acknowledgment (`backend/app/services/aviso.py` y repos)
- [x] 5.3 Filtrar Avisos Activos (`backend/app/repositories/aviso.py`)
- [x] 5.4 Test de Integración (`backend/tests/integration/test_aviso_api.py`)
