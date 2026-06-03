# Monitoreo y Flujos Críticos (C17-4.1)

## Flujos Críticos

### 1. Acceso multi-tenant
- Cada request debe pasar tenant_id (por JWT o X-Tenant-Id). Se inyecta en todas las queries via repository/services.
- Un bug que omite el filtro por tenant es crítico/auditado.
- Ejemplo: ver `core/tenancy.py`, uso en repositorios (`_apply_tenant_scope`).
- **TODO:** Aplicar enforcement global obligatorio vía middleware/decorator (en roadmap).

### 2. Monitoreo y métricas
- Métricas clave: requests totales, latencia (p99), errores, health, recursos.
- Instrumentar los endpoints core vía Prometheus
- Ver ejemplos/guidelines en `monitoring/grafana_alerts_example.md` y `core/observability.py`

### 3. Pipelines y CI/CD
- Toda la battery de tests (unitarios, integración, carga multitenant) debe ejecutarse en CI.
- Si falla algún test o métrica crítica, pipeline hace rollback/notifica.
- Ubicación: `.github/workflows/`, resultados en logs CI.

> Este archivo es un resumen de documentación técnica de operación crítica. Compleméntese con PRD y KB de auditoría/revisión.
