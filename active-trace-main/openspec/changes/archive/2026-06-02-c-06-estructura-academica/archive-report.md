# Archive Report: C-06 Estructura Académica

## 1. Resumen Ejecutivo
**Estado:** COMPLETO y ARCHIVADO
Se completó la implementación de las entidades fundamentales de la estructura académica del proyecto (`Carrera`, `Materia`, y `Cohorte`). Esto provee soporte para la gestión de planes académicos aislados por tenant y sus correspondientes restricciones de negocio complejas.

## 2. Decisiones Técnicas y Arquitectura Consolidada
* **Multi-Tenancy y Unicidad:** Se garantizó a nivel de base de datos el aislamiento por `tenant_id` y las restricciones compuestas (`tenant_id`, `codigo`) para `Carrera`/`Materia` y (`tenant_id`, `carrera_id`, `nombre`) para `Cohorte`.
* **Soft Delete:** Se implementó mediante el campo `estado = 'Inactiva'` (las entidades no se borran físicamente de la base de datos).
* **Validación de Lógica de Negocio (Servicios):**
  - La creación y actualización de Cohortes valida en tiempo de ejecución si la Carrera asociada está activa.
  - El campo `carrera_id` en `Cohorte` es estrictamente inmutable tras su creación.
  - Almacenamiento de enums como `VARCHAR` en la DB con validación en la capa de esquemas y lógica de negocio.
* **Integración de Auditoría:** Cada cambio de estado, creación, o actualización genera un registro en `AuditLog` detallando el cambio de manera estructurada (`CARRERA_CREAR`, `CARRERA_MODIFICAR`, `MATERIA_CREAR`, etc.).

## 3. Pruebas y Validación
Se ejecutaron y pasaron exitosamente los tests de integración en `tests/test_carreras.py`, `tests/test_materias.py` y `tests/test_cohortes.py` con una cobertura robusta:
* Creación de registros y validación de unicidad por tenant.
* Aislamiento: comprobación de que un tenant no puede leer ni modificar carreras o materias de otro tenant.
* Pruebas de borde para inmutabilidad del ID de carrera en cohortes.
* Validación del bloqueo de creación de cohortes en carreras inactivas.

## 4. Archivos Clave Modificados/Creados
* **Modelos**:
  - `backend/app/models/carrera.py` (Nuevo)
  - `backend/app/models/materia.py` (Nuevo)
  - `backend/app/models/cohorte.py` (Nuevo)
* **Esquemas (DTOs)**:
  - `backend/app/schemas/carrera.py` (Nuevo)
  - `backend/app/schemas/materia.py` (Nuevo)
  - `backend/app/schemas/cohorte.py` (Nuevo)
* **Repositorios**:
  - `backend/app/repositories/carrera.py` (Nuevo)
  - `backend/app/repositories/materia.py` (Nuevo)
  - `backend/app/repositories/cohorte.py` (Nuevo)
* **Servicios**:
  - `backend/app/services/carrera.py` (Nuevo)
  - `backend/app/services/materia.py` (Nuevo)
  - `backend/app/services/cohorte.py` (Nuevo)
* **Routers**:
  - `backend/app/api/v1/routers/carreras.py` (Nuevo)
  - `backend/app/api/v1/routers/materias.py` (Nuevo)
  - `backend/app/api/v1/routers/cohortes.py` (Nuevo)
* **Configuración e Inicialización**:
  - `backend/app/main.py` (Modificado para registrar routers)
  - `backend/alembic/versions/005_estructura_academica.py` (Migración)

## 5. Cierre
El change cumple con todas las directivas de Clean Architecture y las restricciones de seguridad. Las entidades fundamentales de negocio quedan consolidadas para las siguientes fases de desarrollo (usuarios y asignaciones).
