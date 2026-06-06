# Tasks: C-14 Evaluaciones y Coloquios

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 450 - 550 lines |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (Modelos/Migración) → PR 2 (CRUD/Lógica) → PR 3 (Routers/Seguridad) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Modelos y migración base | PR 1 | Base para base de datos y aislamiento tenant. |
| 2 | Lógica de CRUD y control de cupos concurrentes | PR 2 | Transacciones con row lock y validación de duplicados. |
| 3 | Routers API con separación de roles | PR 3 | Endpoints en `/admin` y `/reservas` con RBAC. |

---

## Phase 1: Modelos y Base de Datos (PR 1)

- [x] 1.1 Crear modelos en `backend/app/models/evaluacion.py` heredando de `TimestampedTenantMixin`.
- [x] 1.2 Importar modelos en `backend/app/models/__init__.py`.
- [x] 1.3 Generar migración con `alembic revision --autogenerate -m "crear_tablas_evaluaciones"`.
- [x] 1.4 RED: Escribir tests para validación de claves foráneas y tenant isolation en `backend/tests/test_evaluacion_models.py`.
- [x] 1.5 GREEN: Correr tests de modelos y ajustar para que pasen exitosamente.
- [x] 1.6 REFACTOR: Simplificar definición de relaciones y constraints de base de datos.

## Phase 2: Esquemas y Lógica CRUD (PR 2)

- [x] 2.1 Definir esquemas Pydantic con `extra='forbid'` en `backend/app/schemas/evaluacion.py`.
- [x] 2.2 Implementar CRUD en `backend/app/crud/crud_evaluacion.py` con transacciones de bloqueo de fila (`with_for_update`).
- [x] 2.3 RED: Escribir tests de concurrencia en `backend/tests/test_evaluacion_crud.py` simulando solicitudes concurrentes.
- [x] 2.4 GREEN: Codificar la lógica del CRUD para validar cupos y reservas duplicadas en base a los tests.
- [x] 2.5 REFACTOR: Modularizar las comprobaciones de estado de reserva y limpieza de excepciones de SQLAlchemy.

## Phase 3: Rutas de API y Control de Acceso (PR 3)

- [x] 3.1 Crear router en `backend/app/api/v1/routers/evaluaciones.py` separando `/admin` y `/reservas`.
- [x] 3.2 Registrar el router en la aplicación principal en `backend/app/main.py`.
- [x] 3.3 RED: Escribir tests de integración de API y seguridad RBAC en `backend/tests/test_evaluacion_endpoints.py`.
- [x] 3.4 GREEN: Implementar endpoints y validaciones de token de sesión e impersonación legítima.
- [x] 3.5 REFACTOR: Eliminar lógica redundante en la comprobación de pertenencia al tenant.

## Phase 4: Documentación y Cierre (PR 3)

- [x] 4.1 Actualizar documentación de APIs de la Épica 7 en `CHANGES.md` pasando el estado a completo.
- [x] 4.2 Verificar que el reporte de cobertura de tests cumpla con el target del 80% de líneas.
