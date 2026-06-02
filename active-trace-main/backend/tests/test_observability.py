import pytest
import json
import logging
from io import StringIO

def test_json_logging(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
    
    from app.core.logging import setup_logging
    
    log_stream = StringIO()
    setup_logging(stream=log_stream)
    
    logger = logging.getLogger("test_logger")
    logger.info("Test message")
    
    log_output = log_stream.getvalue().strip()
    # It must be a valid JSON
    log_data = json.loads(log_output)
    assert log_data["message"] == "Test message"
    assert log_data["level"] == "INFO"
    assert "timestamp" in log_data

def test_observability_initialization(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    monkeypatch.setenv("ENABLE_OTEL", "true")
    
    from fastapi import FastAPI
    from app.core.observability import setup_observability
    
    app = FastAPI()
    setup_observability(app, service_name="test-service")
    # Just verify that the setup completes and no exceptions are raised

