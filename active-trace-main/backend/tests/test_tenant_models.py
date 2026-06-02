import pytest
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from app.models.base import TimestampedTenant
from app.models.tenant import Tenant
from app.core.database import Base, get_session


@pytest.mark.asyncio
async def test_tenant_instantiation(db_session):
    """RED: Tenant can be instantiated with UUID and name"""
    tenant = Tenant(name="Test Institution")
    assert isinstance(tenant.id, (UUID, type(None)))  # Will be UUID after INSERT
    assert tenant.name == "Test Institution"


@pytest.mark.asyncio
async def test_tenant_persistence(db_session):
    """RED: Tenant can be created and retrieved from database"""
    tenant = Tenant(name="Universidad Test")
    db_session.add(tenant)
    await db_session.flush()
    
    assert tenant.id is not None
    assert isinstance(tenant.id, UUID)
    assert tenant.name == "Universidad Test"
    assert tenant.created_at is not None
    assert isinstance(tenant.created_at, datetime)


@pytest.mark.asyncio
async def test_timestamped_tenant_mixin_fields():
    """RED: TimestampedTenant mixin provides required fields"""
    # This is a class-level test to verify the mixin structure
    from sqlalchemy import inspect
    
    # Check that Tenant has all required fields from mixin
    mapper = inspect(Tenant)
    columns = {col.name for col in mapper.columns}
    
    required_fields = {'id', 'tenant_id', 'created_at', 'updated_at', 'deleted_at'}
    assert required_fields.issubset(columns), f"Missing fields: {required_fields - columns}"


@pytest.mark.asyncio
async def test_created_at_immutable_after_creation(db_session):
    """RED: created_at should be immutable after creation"""
    tenant = Tenant(name="Test 1")
    db_session.add(tenant)
    await db_session.flush()
    
    original_created_at = tenant.created_at
    tenant.name = "Test 1 Updated"
    await db_session.flush()
    
    assert tenant.created_at == original_created_at, "created_at should not change on update"


@pytest.mark.asyncio
async def test_updated_at_changes_on_flush(db_session):
    """RED: updated_at should change when record is modified and flushed"""
    import asyncio
    
    tenant = Tenant(name="Test Initial")
    db_session.add(tenant)
    await db_session.flush()
    
    original_updated_at = tenant.updated_at
    await asyncio.sleep(0.01)  # Ensure time has passed
    
    tenant.name = "Test Modified"
    await db_session.flush()
    
    assert tenant.updated_at > original_updated_at, "updated_at should change on modification"


@pytest.mark.asyncio
async def test_soft_delete_sets_deleted_at(db_session):
    """RED: Soft delete should set deleted_at timestamp"""
    tenant = Tenant(name="To Delete")
    db_session.add(tenant)
    await db_session.flush()
    
    tenant_id = tenant.id
    
    # Mark as deleted
    tenant.deleted_at = datetime.utcnow()
    await db_session.flush()
    
    # Query should not return it by default (handled by repository)
    # This test just verifies the field can be set
    assert tenant.deleted_at is not None


@pytest.mark.asyncio
async def test_multiple_tenants_isolation(db_session):
    """RED: Different tenants can exist independently"""
    tenant_a = Tenant(name="Institution A")
    tenant_b = Tenant(name="Institution B")
    
    db_session.add(tenant_a)
    db_session.add(tenant_b)
    await db_session.flush()
    
    assert tenant_a.id != tenant_b.id
    assert tenant_a.name == "Institution A"
    assert tenant_b.name == "Institution B"
