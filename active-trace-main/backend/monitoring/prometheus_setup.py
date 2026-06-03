"""
Prometheus integration for FastAPI

- Exposes /metrics endpoint for Prometheus scraping
- PrometheusMiddleware: captures latency, request count, and error rate
- To use: add middleware to app and include metrics router
"""
from fastapi import APIRouter, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

# METRICS DEFINITIONS
REQUEST_COUNT = Counter(
    'app_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds', 'Request latency', ['endpoint'])
ERROR_COUNT = Counter(
    'app_errors_total', 'Total errors', ['endpoint', 'exception_type'])


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that instruments every request with Prometheus metrics."""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        try:
            response = await call_next(request)
        except Exception as e:
            ERROR_COUNT.labels(
                endpoint=request.url.path,
                exception_type=type(e).__name__
            ).inc()
            raise
        elapsed = time.time() - start
        REQUEST_LATENCY.labels(endpoint=request.url.path).observe(elapsed)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            http_status=response.status_code
        ).inc()
        return response


router = APIRouter(tags=["monitoring"])


@router.get("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
