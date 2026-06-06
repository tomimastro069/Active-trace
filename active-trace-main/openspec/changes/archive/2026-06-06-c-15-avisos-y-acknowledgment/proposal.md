# Proposal: Avisos y Acknowledgment (C-15)

## Intent
Resolver la necesidad de comunicación interna masiva y segmentada dentro del sistema, permitiendo a coordinadores y administradores publicar novedades institucionales relevantes y permitiendo al alumnado y otros roles realizar acuses de recibo (acknowledgments) obligatorios o informativos.

## Scope

### In Scope
- Creación de modelos `Aviso` y `AcknowledgmentAviso` con soporte multi-tenant y soft delete.
- Endpoint ABM `/api/v1/avisos` para publicación y gestión de avisos (COORDINADOR / ADMIN).
- Endpoint `/api/v1/avisos/activos` para obtener los avisos vigentes y visibles para el usuario en curso según su rol, cohorte y materias (con soporte de filtrado para no mostrar avisos ya confirmados).
- Endpoint `/api/v1/avisos/{id}/ack` para registrar el acuse de recibo de un aviso por parte del usuario.
- Obtención de estadísticas agregadas por aviso (vistas y confirmados) derivadas dinámicamente de `AcknowledgmentAviso`.

### Out of Scope
- Integración de notificaciones push o envío de emails asociados a los avisos (eso pertenece a `C-12`/Mensajería externa).
- Sistema de mensajería interna bidireccional (Inbox/Inbox de mensajería, FL-10).

## Capabilities

### New Capabilities
- `avisos-y-acknowledgments`: Publicación, segmentación y acuse de recibo de avisos del sistema.

### Modified Capabilities
None

## Approach
1. **Modelos y Migración:** Crear modelos `Aviso` y `AcknowledgmentAviso` heredando de `TimestampedTenant`. Generar migración Alembic.
2. **Repositorio:** Diseñar consulta en `AvisoRepository` que cruce el alcance y las asignaciones del usuario (rol, materia, cohorte) filtrando por la ventana temporal de vigencia y excluyendo si `requiere_ack=True` y ya posee acuse.
3. **Servicio y API:** Desarrollar `AvisoService` para control de lógica, validar permisos mediante `require_permission("avisos:publicar")`, y exponer los endpoints en `backend/app/api/v1/routers/avisos.py`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/models/aviso.py` | New | Modelos SQLAlchemy de Aviso y Acknowledgment |
| `backend/app/models/__init__.py` | Modified | Importación y exposición de nuevos modelos |
| `backend/app/schemas/aviso.py` | New | Pydantic schemas para validación de datos |
| `backend/app/repositories/aviso.py` | New | Consultas scoped y lógicas de agregación de acuses |
| `backend/app/services/aviso.py` | New | Lógica de negocio de avisos |
| `backend/app/api/v1/routers/avisos.py` | New | Endpoints de la API `/api/v1/avisos` |
| `backend/app/main.py` | Modified | Inclusión del nuevo router |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Query de segmentación compleja y lenta | Medium | Utilizar índices en `(tenant_id, activo, inicio_en, fin_en)` y en la tabla de asignaciones |
| Fuga de datos entre tenants | Low | Todos los repositorios heredan de `BaseRepository` aplicando `tenant_id` por defecto |

## Rollback Plan
- Revertir la migración de Alembic: `alembic downgrade -1` (o la versión previa a la migración generada).
- Deshacer cambios en `main.py` y `models/__init__.py`.
- Borrar archivos nuevos creados en `backend/app/`.

## Dependencies
- `C-06` (Estructura académica de asignaciones y roles cargada en base de datos).

## Success Criteria
- [ ] Creación de avisos restringida únicamente a roles autorizados con `avisos:publicar`.
- [ ] Retorno exacto de avisos activos por segmentación y rango temporal.
- [ ] Ocultamiento del aviso en `/activos` inmediatamente después de registrar el `/ack` (cuando `requiere_ack=True`).
- [ ] Cobertura de tests unitarios e integración ≥ 90% para las reglas de negocio críticas.
