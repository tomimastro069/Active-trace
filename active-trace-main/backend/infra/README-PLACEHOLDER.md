# Infraestructura

Scripts y configuración de infraestructura y despliegue.

## Ubicación actual

- **Docker**: [`docker-compose.yml`](../../docker-compose.yml) — servicios api, worker, postgres, prometheus, grafana
- **CI/CD**: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — pipeline unificado con tests, lint, cobertura, deploy y rollback
- **Monitoreo**: [`monitoring/`](../monitoring/) — configuración de Prometheus, métricas, y alertas Grafana
- **Dockerfile**: [`Dockerfile`](../Dockerfile) — imagen de la API

## Despliegue

El deploy a producción se realiza via GitHub Actions al hacer push a `main`. En caso de fallo, se ejecuta rollback automático (revert del commit).