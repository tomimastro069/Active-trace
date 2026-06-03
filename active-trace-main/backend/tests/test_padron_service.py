import pytest
import uuid
from datetime import date
from sqlalchemy import select
from app.models.tenant import Tenant
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.usuario import Usuario
from app.models.audit_log import AuditLog
from app.schemas.padron import EntradaPadronCreate
from app.services.padron_service import PadronService

@pytest.mark.asyncio
async def test_padron_service_import_validation_and_linking(db_session):
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    # 1. Setup entities
    tenant = Tenant(id=tenant_id, name="Test Tenant")
    actor = Usuario(
        id=actor_id,
        tenant_id=tenant_id,
        email="actor@example.com",
        hashed_password="password",
        nombre="Admin",
        apellidos="User"
    )
    # Existing student who has a registered account
    registered_student = Usuario(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email="registered@example.com",
        hashed_password="password",
        nombre="Juan",
        apellidos="Perez"
    )
    carrera = Carrera(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        codigo="ISI",
        nombre="Ingeniería en Sistemas",
        estado="Activa"
    )
    db_session.add_all([tenant, actor, registered_student, carrera])
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
        nombre="Algoritmos",
        estado="Activa"
    )
    db_session.add_all([cohorte, materia])
    await db_session.flush()

    # Instantiate service
    service = PadronService(db_session, tenant_id)

    # 2. Test Inactive Materia Validation
    inactive_materia = Materia(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        codigo="AED-INACT",
        nombre="Algoritmos Inactiva",
        estado="Inactiva"
    )
    db_session.add(inactive_materia)
    await db_session.flush()

    entradas = [
        EntradaPadronCreate(
            email="registered@example.com",
            nombre="Juan",
            apellidos="Perez",
            comision="3K1"
        )
    ]

    with pytest.raises(ValueError, match="La materia no existe o está Inactiva."):
        await service.importar_padron(inactive_materia.id, cohorte.id, entradas, actor_id)

    # 3. Test Inactive Cohorte Validation
    inactive_cohorte = Cohorte(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        carrera_id=carrera.id,
        nombre="Cohorte Inactiva",
        anio=2026,
        vig_desde=date(2026, 3, 1),
        estado="Inactiva"
    )
    db_session.add(inactive_cohorte)
    await db_session.flush()

    with pytest.raises(ValueError, match="La cohorte no existe o está Inactiva."):
        await service.importar_padron(materia.id, inactive_cohorte.id, entradas, actor_id)

    # 4. Import padron successfully with student account linkage
    student_unregistered_email = "unregistered@example.com"
    entradas_full = [
        EntradaPadronCreate(
            email="registered@example.com",
            nombre="Juan",
            apellidos="Perez",
            comision="3K1",
            regional="Campus"
        ),
        EntradaPadronCreate(
            email=student_unregistered_email,
            nombre="Carlos",
            apellidos="Gomez",
            comision="3K2"
        )
    ]

    v1 = await service.importar_padron(materia.id, cohorte.id, entradas_full, actor_id)
    await db_session.flush()

    assert v1.activa is True

    # Retrieve and verify entries mapping
    entries = await service.get_entradas(v1.id)
    assert len(entries) == 2

    # Map by email
    entry_map = {e.email: e for e in entries}

    # Verify registered student links to their Usuario id
    assert entry_map["registered@example.com"].usuario_id == registered_student.id
    assert entry_map["registered@example.com"].nombre == "Juan"

    # Verify unregistered student does NOT have a usuario_id (is null)
    assert entry_map["unregistered@example.com"].usuario_id is None
    assert entry_map["unregistered@example.com"].nombre == "Carlos"

    # Verify audit log PADRON_CARGAR exists
    query_audit_cargar = select(AuditLog).where(
        AuditLog.tenant_id == tenant_id,
        AuditLog.accion == "PADRON_CARGAR"
    )
    res_cargar = await db_session.execute(query_audit_cargar)
    audit_cargar = res_cargar.scalars().first()
    assert audit_cargar is not None
    assert audit_cargar.actor_id == actor_id
    assert audit_cargar.materia_id == materia.id
    assert audit_cargar.filas_afectadas == 2

    # 5. Empty/Clear padron data (vaciar_padron)
    await service.vaciar_padron(materia.id, cohorte.id, actor_id)
    await db_session.flush()

    # Verify active version is now None
    active_now = await service.get_active_version(materia.id, cohorte.id)
    assert active_now is None

    # Verify audit log PADRON_VACIAR exists
    query_audit_vaciar = select(AuditLog).where(
        AuditLog.tenant_id == tenant_id,
        AuditLog.accion == "PADRON_VACIAR"
    )
    res_vaciar = await db_session.execute(query_audit_vaciar)
    audit_vaciar = res_vaciar.scalars().first()
    assert audit_vaciar is not None
    assert audit_vaciar.actor_id == actor_id
    assert audit_vaciar.materia_id == materia.id
