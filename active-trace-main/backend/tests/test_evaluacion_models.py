import pytest
from uuid import uuid4
from datetime import datetime
from app.models.tenant import Tenant
from app.models.materia import Materia
from app.models.cohorte import Cohorte
from app.models.usuario import Usuario
from app.models.evaluacion import Evaluacion, ReservaEvaluacion, ResultadoEvaluacion, EvaluacionTipoEnum, EstadoReservaEnum

from app.models.carrera import Carrera

@pytest.mark.asyncio
async def test_crear_evaluacion_con_tenant(db_session):
    # Setup dependencies
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    await db_session.flush()

    materia = Materia(tenant_id=tenant.id, codigo="MAT-C14", nombre="Materia C14")
    db_session.add(materia)
    await db_session.flush()

    carrera = Carrera(tenant_id=tenant.id, codigo="CAR", nombre="Carrera")
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(tenant_id=tenant.id, carrera_id=carrera.id, nombre="Cohorte 2026", anio=2026, vig_desde=datetime(2026, 1, 1).date(), vig_hasta=datetime(2026, 12, 31).date())
    db_session.add(cohorte)
    await db_session.flush()

    # Create Evaluacion
    evaluacion = Evaluacion(
        tenant_id=tenant.id,
        materia_id=materia.id,
        cohorte_id=cohorte.id,
        tipo=EvaluacionTipoEnum.COLOQUIO,
        instancia="Coloquio Final Julio",
        dias_disponibles=2,
        cupos_totales=10
    )
    db_session.add(evaluacion)
    await db_session.flush()

    assert evaluacion.id is not None
    assert evaluacion.tipo == EvaluacionTipoEnum.COLOQUIO
    assert evaluacion.cupos_totales == 10

@pytest.mark.asyncio
async def test_crear_reserva_y_resultado(db_session):
    # Setup
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    await db_session.flush()

    materia = Materia(tenant_id=tenant.id, codigo="MAT-C14-2", nombre="Materia 2")
    db_session.add(materia)
    await db_session.flush()

    carrera = Carrera(tenant_id=tenant.id, codigo="CAR2", nombre="Carrera 2")
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(tenant_id=tenant.id, carrera_id=carrera.id, nombre="Cohorte 2", anio=2026, vig_desde=datetime(2026, 1, 1).date(), vig_hasta=datetime(2026, 12, 31).date())
    db_session.add(cohorte)
    await db_session.flush()

    alumno = Usuario(tenant_id=tenant.id, email="alumno@test.com", hashed_password="hash", estado="Activo")
    db_session.add(alumno)
    await db_session.flush()

    evaluacion = Evaluacion(
        tenant_id=tenant.id, materia_id=materia.id, cohorte_id=cohorte.id,
        tipo=EvaluacionTipoEnum.PARCIAL, instancia="1er Parcial", dias_disponibles=1, cupos_totales=5
    )
    db_session.add(evaluacion)
    await db_session.flush()

    # Create Reserva
    reserva = ReservaEvaluacion(
        tenant_id=tenant.id,
        evaluacion_id=evaluacion.id,
        alumno_id=alumno.id,
        fecha_hora=datetime(2026, 7, 6, 10, 0),
        estado=EstadoReservaEnum.ACTIVA
    )
    db_session.add(reserva)
    await db_session.flush()

    assert reserva.id is not None
    assert reserva.estado == EstadoReservaEnum.ACTIVA

    # Create Resultado
    resultado = ResultadoEvaluacion(
        tenant_id=tenant.id,
        evaluacion_id=evaluacion.id,
        alumno_id=alumno.id,
        nota_final="8 (Aprobado)"
    )
    db_session.add(resultado)
    await db_session.flush()

    assert resultado.id is not None
    assert resultado.nota_final == "8 (Aprobado)"
