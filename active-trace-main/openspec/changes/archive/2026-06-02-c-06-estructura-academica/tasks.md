# Tasks: C-06 Estructura Académica

- `[x]` 1. **Modelos y Migraciones**
  - `[x]` 1.1 Crear `backend/app/models/carrera.py` con `Carrera`.
  - `[x]` 1.2 Crear `backend/app/models/materia.py` con `Materia`.
  - `[x]` 1.3 Crear `backend/app/models/cohorte.py` con `Cohorte`.
  - `[x]` 1.4 Agregar importaciones en `backend/app/models/__init__.py`.
  - `[x]` 1.5 Generar migración Alembic `005_estructura_academica` y revisarla.

- `[x]` 2. **Esquemas (Pydantic)**
  - `[x]` 2.1 Crear `backend/app/schemas/carrera.py`.
  - `[x]` 2.2 Crear `backend/app/schemas/materia.py`.
  - `[x]` 2.3 Crear `backend/app/schemas/cohorte.py`.

- `[x]` 3. **Repositorios**
  - `[x]` 3.1 Crear `backend/app/repositories/carrera.py`.
  - `[x]` 3.2 Crear `backend/app/repositories/materia.py`.
  - `[x]` 3.3 Crear `backend/app/repositories/cohorte.py`.

- `[x]` 4. **Servicios (Capa de Lógica)**
  - `[x]` 4.1 Crear `backend/app/services/carrera.py` (Manejo de Auditoría y Estado).
  - `[x]` 4.2 Crear `backend/app/services/materia.py` (Manejo de Auditoría y Estado).
  - `[x]` 4.3 Crear `backend/app/services/cohorte.py` (Validación de estado de Carrera y Auditoría).

- `[x]` 5. **Routers (Endpoints)**
  - `[x]` 5.1 Crear `backend/app/api/v1/routers/carreras.py`.
  - `[x]` 5.2 Crear `backend/app/api/v1/routers/materias.py`.
  - `[x]` 5.3 Crear `backend/app/api/v1/routers/cohortes.py`.
  - `[x]` 5.4 Registrar los routers en `backend/app/main.py` (en lugar de api.py).

- `[x]` 6. **Testing**
  - `[x]` 6.1 Crear override de dependencias en los tests en lugar de conftest.py.
  - `[x]` 6.2 Crear `backend/tests/test_carreras.py` (CRUD, validación de estado, aislamiento de tenant).
  - `[x]` 6.3 Crear `backend/tests/test_materias.py` (CRUD, unicidad tenant_id + codigo).
  - `[x]` 6.4 Crear `backend/tests/test_cohortes.py` (Apertura bloqueada si carrera inactiva, creación exitosa, soft-delete).
