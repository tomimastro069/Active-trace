## Exploration: C-15 Avisos y Acknowledgment

### Current State
El sistema actualmente no cuenta con soporte en backend ni en base de datos para la publicación de Avisos y sus correspondientes acuses de recibo (Acknowledgments). Los modelos `Aviso` y `AcknowledgmentAviso` definidos en `04_modelo_de_datos.md` §E13 no se encuentran implementados aún. Tampoco existen rutas de API en `/api/v1/avisos/*`.

### Affected Areas
- `backend/app/models/aviso.py` [NEW] — Modelos SQLAlchemy para `Aviso` y `AcknowledgmentAviso`.
- `backend/app/models/__init__.py` [MODIFY] — Registro de nuevos modelos en el módulo general.
- `backend/app/schemas/aviso.py` [NEW] — Schemas Pydantic para creación, actualización y respuestas.
- `backend/app/repositories/aviso.py` [NEW] — Operaciones de base de datos para consultar avisos vigentes por destinatario y registrar acuses.
- `backend/app/repositories/__init__.py` [MODIFY] — Registro del repositorio.
- `backend/app/services/aviso.py` [NEW] — Lógica de negocio (verificación de ventanas de vigencia, filtros por rol/cohorte/materia y cálculo de estadísticas).
- `backend/app/api/v1/routers/avisos.py` [NEW] — Endpoints `/api/v1/avisos` para la publicación de avisos (coordinadores/admins) y la lectura/ack (alumnos y otros roles).
- `backend/app/main.py` [MODIFY] — Registro del router en la aplicación FastAPI.
- `backend/alembic/versions/` [NEW] — Archivo de migración de Alembic para crear las tablas correspondientes.
- `backend/tests/` [NEW] — Tests de integración para verificar el correcto filtrado por rol, cohorte, materia, vigencia temporal y acuses de recibo.

### Approaches
1. **Filtrado Dinámico en Consulta (Recomendado)** — Obtener los avisos legibles cruzando dinámicamente en una sola query de base de datos el alcance del aviso (Global, PorMateria, PorCohorte, PorRol) con las asignaciones vigentes del usuario en curso. Los avisos con acuse ya realizado se omiten de la lista activa pero se conservan para estadísticas.
   - Pros: Mantiene consistencia total, se adapta al instante a cambios de rol o cohorte del usuario y evita redundancia de datos.
   - Cons: Requiere una consulta SQL más estructurada con múltiples cláusulas condicionales (OR/AND).
   - Effort: Medium

2. **Tabla de Destinatarios Desnormalizada** — Registrar explícitamente qué usuarios deben recibir cada aviso al momento de su publicación.
   - Pros: La consulta de avisos activos por usuario es extremadamente simple.
   - Cons: Muy ineficiente para avisos globales o por cohorte (genera miles de filas redundantes). Dificulta la gestión cuando un usuario cambia de sección o cohorte de forma tardía.
   - Effort: High

### Recommendation
Implementar la **Opción 1 (Filtrado Dinámico en Consulta)**. Se alinea con el principio de diseño relacional del proyecto y garantiza que no haya retrasos ni inconsistencias ante cambios en los equipos docentes o padrones de alumnos. Se usará SQLAlchemy para construir una consulta eficiente basada en la identidad y asignaciones de la sesión del usuario.

### Risks
- **Complejidad de la query de visibilidad**: Combinar las reglas de segmentación (Global, por Materia, por Cohorte, por Rol) y evitar mostrar avisos que ya tienen confirmación de lectura en un solo endpoint requiere diseñar cuidadosamente la query utilizando operadores `or_` y `and_` en SQLAlchemy.
- **Rendimiento de los contadores**: Para cumplir con la regla de no desnormalizar los contadores de lectura (RN-18/19/20), se deben calcular al vuelo a través de agregaciones sobre la tabla de confirmaciones. Se optimizará mediante índices adecuados en la base de datos.

### Ready for Proposal
Yes — Proceeding to the proposal phase.
