import pytest
from pydantic import ValidationError

def test_settings_valid_load(monkeypatch):
    # Set valid env variables
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

    from app.core.config import Settings
    settings = Settings(_env_file=None)
    assert settings.DATABASE_URL == "postgresql+asyncpg://user:pass@localhost/db"
    assert settings.SECRET_KEY == "a" * 32
    assert settings.ENCRYPTION_KEY == "b" * 32
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

def test_settings_missing_secret_key(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
    
    from app.core.config import Settings
    with pytest.raises(ValidationError) as excinfo:
        Settings(_env_file=None)
    assert "SECRET_KEY" in str(excinfo.value)

def test_settings_invalid_secret_key_length(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "short")
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
    
    from app.core.config import Settings
    with pytest.raises(ValidationError) as excinfo:
        Settings(_env_file=None)
    assert "SECRET_KEY" in str(excinfo.value)

def test_settings_invalid_encryption_key_length(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 31) # 31 chars instead of 32
    
    from app.core.config import Settings
    with pytest.raises(ValidationError) as excinfo:
        Settings(_env_file=None)
    assert "ENCRYPTION_KEY" in str(excinfo.value)

def test_settings_invalid_expire_minutes_type(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "not-a-number")
    
    from app.core.config import Settings
    with pytest.raises(ValidationError) as excinfo:
        Settings(_env_file=None)
    assert "ACCESS_TOKEN_EXPIRE_MINUTES" in str(excinfo.value)

