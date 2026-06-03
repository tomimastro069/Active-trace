## Exploration: C-09 padron-ingesta-moodle

### Current State
El sistema cuenta con el esquema base de seguridad y autenticación multi-tenant (C-01 a C-04), estructura académica raíz de carreras, materias y cohortes (C-06), así como los usuarios y asignaciones base (C-07) y auditoría inmutable (C-05). Sin embargo, el sistema carece del mecanismo de ingesta de datos principal para alimentar el dominio académico operativo: la importación de padrones de alumnos inscritos desde el LMS (Moodle) o mediante carga manual. Tampoco existen las entidades `VersionPadron` ni `EntradaPadron`.

### Affected Areas
- `backend/app/models/padron.py` (NUEVO) — Para definir los modelos `VersionPadron` y `EntradaPadron`.
- `backend/alembic/versions/` (NUEVO) — Migración para crear las tablas de versión y entradas.
- `backend/app/schemas/padron.py` (NUEVO) — Esquemas Pydantic para validación y carga.
- `backend/app/repositories/padron_repository.py` (NUEVO) — Gestión de persistencia y versionado para mantener solo una versión activa por `materia×cohorte`.
- `backend/app/services/padron_service.py` (NUEVO) — Lógica de negocio para manejar la ingesta, upsert de estudiantes y gestión del versionado.
- `backend/app/routers/padron.py` (NUEVO) — Endpoints de la API para iniciar la carga manual y la sincronización web.
- `backend/app/integrations/moodle_ws.py` (NUEVO) — Módulo para comunicación con los Moodle Web Services (LMS).

### Approaches
1. **Desarrollo completo: Moodle WS + Fallback en bloque** — Implementar `VersionPadron` y la ingesta tanto manual (vía `.csv`/`.xlsx`) como sincrónica usando Moodle WS en paralelo.
   - Pros: Entrega el scope C-09 completo de una sola vez. Cubre a tenants que tienen Moodle con WS activados y aquellos que no.
   - Cons: Mayor riesgo de complejidad al interactuar con bibliotecas para procesar excel/csv (`pandas` o similar) y al mismo tiempo realizar llamadas HTTP externas y manejar reintentos (502).
   - Effort: High

2. **Iterativo: Ingesta manual primero, luego Moodle WS** — Crear los modelos y la estructura de API con la ingesta por CSV/XLSX. Luego, en una iteración posterior del mismo change o un refactor rápido, conectar los Web Services de Moodle.
   - Pros: Disminuye la carga cognitiva. El CSV sirve como "mock" perfecto para definir cómo entran los datos a las entidades. Permite validar los modelos y el versionado antes de incorporar red.
   - Cons: El trabajo se divide y la integración externa podría forzar un pequeño ajuste de mapping posterior.
   - Effort: Medium

### Recommendation
**Iterativo: Ingesta manual primero, luego Moodle WS**. Recomiendo empezar definiendo los modelos `VersionPadron` y `EntradaPadron`, junto al servicio de ingesta desde CSV/XLSX (`pandas` o `csv` estándar). Esto fuerza a resolver el versionado de forma local y predecible. Una vez asegurado que la versión activa desactiva a la anterior, y que las entradas sin `usuario_id` son aceptadas, se construye el cliente HTTP `integrations/moodle_ws.py` que simplemente consumirá la misma lógica de "upsert" que ya fue probada localmente.

### Risks
- Mapeo inestable entre cuentas de usuario del sistema (identificados por e-mail u otros PII) y cuentas de Moodle (que podrían estar usando un e-mail distinto o un legajo).
- Integración Moodle WS puede fallar (502). El fallback de error de Moodle debe ser gestionado graciosamente para no corromper la BD local ni dejar una transacción a medias.
- El cifrado de `email` y PII en el modelo `Usuario` puede requerir transformaciones específicas al hacer lookup o inserción masiva desde el padrón importado.

### Ready for Proposal
Yes — La especificación es sólida y los modelos están bien definidos en la base de conocimientos. Se puede avanzar a `/opsx-propose C-09-padron-ingesta-moodle`.
