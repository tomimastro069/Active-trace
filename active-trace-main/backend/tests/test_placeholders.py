import pytest

def test_imports(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
    
    from app.core import security
    from app.core import permissions
    from app.core import tenancy
    from app.core import exceptions
    
    assert security is not None
    assert permissions is not None
    assert tenancy is not None
    assert exceptions is not None
