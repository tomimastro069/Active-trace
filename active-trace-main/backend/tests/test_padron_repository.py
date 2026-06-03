import pytest
import uuid
from datetime import date, datetime
from sqlalchemy import select
from app.models.tenant import Tenant
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.padron import VersionPadron, EntradaPadron
from app.repositories.padron_repository import PadronRepository

@pytest.mark.asyncio
async def test_padron_repository_operations(db_session):
    tenant_id = uuid.uuid4()
    
    # 1. Setup Tenant, Carrera, Cohorte, Materia
    tenant = Tenant(id=tenant_id, name="UTN FRBA")
    carrera = Carrera(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        codigo="ISI",
        nombre="Ingeniería en Sistemas",
        estado="Activa"
    )
    db_session.add_all([tenant, carrera])
    await db_session.flush()

    cohorte = Cohorte(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        carrera_id=carrera.id,
        nombre="Cohorte 2026",
        anio=2026,
        vig_desde=date(2026, 3, 1),
        estado="Activa"
    )
    materia = Materia(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        codigo="AED",
        nombre="Algoritmos y Estructuras de Datos",
        estado="Activa"
    )
    db_session.add_all([cohorte, materia])
    await db_session.flush()

    # 2. Instantiate repository
    repo = PadronRepository(db_session, tenant_id)

    # Test get_active_version on empty DB -> returns None
    active = await repo.get_active_version(materia.id, cohorte.id)
    assert active is None

    # 3. Create Version 1 with entries
    entradas_v1 = [
        {
            "email": "student1@example.com",
            "nombre": "Juan",
            "apellidos": "Perez",
            "comision": "3K1",
            "regional": "Campus"
        },
        {
            "email": "student2@example.com",
            "nombre": "Maria",
            "apellidos": "Gomez",
            "comision": "3K2",
            "regional": "Medrano"
        }
    ]

    v1 = await repo.crear_version_con_entradas(materia.id, cohorte.id, entradas_v1)
    await db_session.flush()

    # Verify Version 1 is active
    assert v1.activa is True
    assert v1.tenant_id == tenant_id
    
    # Verify active version is v1
    active_v1 = await repo.get_active_version(materia.id, cohorte.id)
    assert active_v1 is not None
    assert active_v1.id == v1.id

    # Retrieve and verify entries
    entries_v1 = await repo.get_entradas_by_version(v1.id)
    assert len(entries_v1) == 2
    
    emails = {e.email for e in entries_v1}
    assert "student1@example.com" in emails
    assert "student2@example.com" in emails
    
    # Verify email hashes exist
    assert entries_v1[0].email_hash is not None
    assert len(entries_v1[0].email_hash) == 64

    # 4. Create Version 2 (this should atomically deactivate v1)
    entradas_v2 = [
        {
            "email": "student1@example.com",
            "nombre": "Juan",
            "apellidos": "Perez",
            "comision": "3K1",
            "regional": "Campus"
        },
        {
            "email": "student3@example.com",
            "nombre": "Carlos",
            "apellidos": "Lopez",
            "comision": "3K3"
        }
    ]

    v2 = await repo.crear_version_con_entradas(materia.id, cohorte.id, entradas_v2)
    await db_session.flush()

    # Re-fetch v1 and v2 to verify active flags
    await db_session.refresh(v1)
    await db_session.refresh(v2)

    assert v1.activa is False
    assert v2.activa is True

    # Verify active version is now v2
    active_now = await repo.get_active_version(materia.id, cohorte.id)
    assert active_now.id == v2.id

    # Verify entries of v2
    entries_v2 = await repo.get_entradas_by_version(v2.id)
    assert len(entries_v2) == 2
    emails_v2 = {e.email for e in entries_v2}
    assert "student3@example.com" in emails_v2
    assert "student2@example.com" not in emails_v2

    # 5. Test manual deactivation via desactivar_versiones_activas
    deactivated_count = await repo.desactivar_versiones_activas(materia.id, cohorte.id)
    await db_session.flush()
    assert deactivated_count == 1

    await db_session.refresh(v2)
    assert v2.activa is False

    active_final = await repo.get_active_version(materia.id, cohorte.id)
    assert active_final is None
