import os
import logging
from fastapi import FastAPI

logger = logging.getLogger(__name__)

def setup_observability(app: FastAPI, service_name: str = "activia-trace") -> None:
    enable_otel = os.getenv("ENABLE_OTEL", "false").lower() in ("true", "1", "yes")
    if not enable_otel:
        return
        
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        # If opentelemetry sdk or api is installed, we can set up tracing.
        # But if the SDK is not present, importing TracerProvider will raise ImportError.
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.resources import Resource
            
            provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
            trace.set_tracer_provider(provider)
        except ImportError:
            logger.warning("OpenTelemetry SDK not installed, using default API provider")
            
        FastAPIInstrumentor.instrument_app(app)
    except Exception as e:
        logger.warning(f"Failed to initialize OpenTelemetry: {e}")
