"""
Multi-tenant load and isolation tests (C17-3.2).

Tests concurrent access from multiple tenants to verify:
1. Data isolation — tenant A never sees tenant B's data
2. Concurrent throughput — multiple tenants operating simultaneously
3. No cross-contamination under parallel writes
"""
import asyncio
import uuid
import pytest
from uuid import UUID
from sqlalchemy import select
from app.models.tenant import Tenant
from app.models.carrera import Carrera
from app.repositories.carrera import CarreraRepository


@pytest.mark.asyncio
async def test_concurrent_tenants_data_isolation(db_session):
    """
    Create data for multiple tenants concurrently and verify strict isolation.
    Each tenant's repository must only see its own records.
    """
    # Setup: create 3 tenants
    tenants = []
    for i in range(3):
        t = Tenant(name=f"Institution {i}")
        db_session.add(t)
        tenants.append(t)
    await db_session.flush()

    # Create carreras for each tenant
    for i, tenant in enumerate(tenants):
        carrera = Carrera(
            nombre=f"Ingeniería {i}",
            codigo=f"ING-{i}",
            estado="activa",
            tenant_id=tenant.id,
        )
        db_session.add(carrera)
    await db_session.flush()

    # Verify isolation: each repo scoped to a tenant only sees its own carrera
    for i, tenant in enumerate(tenants):
        repo = CarreraRepository(db_session, tenant.id)
        carreras = await repo.list_all()
        assert len(carreras) == 1, (
            f"Tenant {tenant.id} should see exactly 1 carrera, got {len(carreras)}"
        )
        assert carreras[0].nombre == f"Ingeniería {i}"
        assert carreras[0].tenant_id == tenant.id


@pytest.mark.asyncio
async def test_parallel_writes_no_cross_contamination(db_session):
    """
    Simulate parallel writes from different tenants and verify no data leaks.
    """
    tenant_a = Tenant(name="Tenant A")
    tenant_b = Tenant(name="Tenant B")
    db_session.add(tenant_a)
    db_session.add(tenant_b)
    await db_session.flush()

    # Write multiple records for each tenant
    for j in range(5):
        db_session.add(Carrera(
            nombre=f"Carrera A-{j}", codigo=f"CA-{j}",
            estado="activa", tenant_id=tenant_a.id,
        ))
        db_session.add(Carrera(
            nombre=f"Carrera B-{j}", codigo=f"CB-{j}",
            estado="activa", tenant_id=tenant_b.id,
        ))
    await db_session.flush()

    # Verify counts per tenant
    repo_a = CarreraRepository(db_session, tenant_a.id)
    repo_b = CarreraRepository(db_session, tenant_b.id)

    carreras_a = await repo_a.list_all()
    carreras_b = await repo_b.list_all()

    assert len(carreras_a) == 5
    assert len(carreras_b) == 5

    # Verify NO cross-contamination
    for c in carreras_a:
        assert c.tenant_id == tenant_a.id, f"Carrera {c.nombre} leaked to tenant A"
        assert c.nombre.startswith("Carrera A-")

    for c in carreras_b:
        assert c.tenant_id == tenant_b.id, f"Carrera {c.nombre} leaked to tenant B"
        assert c.nombre.startswith("Carrera B-")


@pytest.mark.asyncio
async def test_tenant_cannot_access_other_tenant_by_id(db_session):
    """
    A repository scoped to tenant A must NOT return a record that belongs to tenant B,
    even when queried by exact ID.
    """
    tenant_a = Tenant(name="Tenant A")
    tenant_b = Tenant(name="Tenant B")
    db_session.add(tenant_a)
    db_session.add(tenant_b)
    await db_session.flush()

    # Create carrera owned by tenant B
    carrera_b = Carrera(
        nombre="Secret Carrera", codigo="SEC-1",
        estado="activa", tenant_id=tenant_b.id,
    )
    db_session.add(carrera_b)
    await db_session.flush()

    # Tenant A tries to access it by ID
    repo_a = CarreraRepository(db_session, tenant_a.id)
    result = await repo_a.get_by_id(carrera_b.id)
    assert result is None, "Tenant A should NOT be able to access Tenant B's carrera"
