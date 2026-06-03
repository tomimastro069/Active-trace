# Ejemplo de configuración de dashboards/alertas en Grafana

## Dashboards sugeridos
- **HTTP request rate**: `app_requests_total` por endpoint y método
- **Latencia**: `app_request_latency_seconds` (p99), bucket para umbrales críticos
- **Errores**: `app_errors_total` por endpoint y tipo de excepción

## Alertas
- **Alta latencia**: dispara si latency p99 > 2s en `/api` durante 5 min
- **Demasiados errores**: alerta si app_errors_total aumenta 10+ en 1 min
- **Caída de servicio**: sin métricas expuestas en /metrics

> Todos los umbrales/base pueden ajustarse luego de la operación inicial.
