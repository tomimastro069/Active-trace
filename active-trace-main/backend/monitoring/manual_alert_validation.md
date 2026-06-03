# Manual/demo validación de alertas críticas (C17-4.2)

Este script/manual asume entorno con Prometheus y Grafana configurados.

## Pasos para validar disparo de alertas:

1. Fuerza un error HTTP 500 multiplicado (ej. vía endpoint fake `/api/v1/fail-fast`)
2. Verifica que la métrica `app_errors_total` sube al menos +10 en 1 min:
   - Accede a Prometheus UI, consulta:
     
     `app_errors_total{service="activia-trace"}`
3. En Grafana, verifica que surge alerta "Demasiados errores" (config ejemplo en `grafana_alerts_example.md`).
4. Simula caída de servicio:
   - Mata el proceso de api/backend temporalmente
   - La alerta "Caída de servicio" debe activarse (sin métricas expuestas en `/metrics`)
5. Simula alta latencia:
   - Fuerza requests con sleep artificial >2s en endpoint crítico
   - Chequea alerta de "Alta latencia".

> **Observación:** Puedes automatizar estos pasos con scripts de carga + kill process.
