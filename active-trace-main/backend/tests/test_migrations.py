import pytest
import os
from pathlib import Path


@pytest.mark.asyncio
async def test_migration_001_exists():
    """RED: Verify that Migration 001: tenant exists"""
    migration_file = Path(
        os.path.dirname(__file__)
    ).parent / "alembic" / "versions" / "001_tenant.py"
    
    assert migration_file.exists(), f"Migration not found at {migration_file}"


def test_migration_001_content():
    """RED: Verify that migration has upgrade and downgrade functions"""
    migration_file = Path(__file__).parent.parent / "alembic" / "versions" / "001_tenant.py"
    
    with open(migration_file, 'r') as f:
        content = f.read()
    
    assert "def upgrade()" in content
    assert "def downgrade()" in content
    assert "CREATE TABLE" in content or "op.create_table" in content
    assert "tenant" in content.lower()
