from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logging import setup_logging
from app.core.observability import setup_observability
from app.api.v1.routers.health import router as health_router
from app.core.database import engine

# Initialize logging at startup
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup OpenTelemetry
    setup_observability(app)
    yield
    # Dispose database engine resources
    await engine.dispose()

app = FastAPI(
    title="Activia Trace API",
    version="0.1.0",
    lifespan=lifespan
)

# Register routers
app.include_router(health_router)
