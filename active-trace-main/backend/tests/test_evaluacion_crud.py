import pytest
from uuid import uuid4
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.carrera import Carrera
from app.models.materia import Materia
from app.models.cohorte import Cohorte
from app.models.usuario import Usuario
from app.models.evaluacion import Evaluacion, EvaluacionTipoEnum, EstadoReservaEnum
from app.crud.crud_evaluacion import CRUDEvaluacion
from app.schemas.evaluacion import ReservaCreate

@pytest.fixture
async def crud_evaluacion_setup(db_session: AsyncSession):
    # Setup Tenant and dependencies
    tenant = Tenant(name="Tenant CRUD")
    db_session.add(tenant)
    await db_session.flush()

    carrera = Carrera(tenant_id=tenant.id, codigo="CAR", nombre="Carrera")
    db_session.add(carrera)
    await db_session.flush()

    materia = Materia(tenant_id=tenant.id, codigo="MAT", nombre="Materia")
    db_session.add(materia)
    await db_session.flush()

    cohorte = Cohorte(tenant_id=tenant.id, carrera_id=carrera.id, nombre="Cohorte", anio=2026, vig_desde=datetime(2026, 1, 1).date(), vig_hasta=datetime(2026, 12, 31).date())
    db_session.add(cohorte)
    await db_session.flush()

    # Create Evaluacion with 2 cupos
    evaluacion = Evaluacion(
        tenant_id=tenant.id,
        materia_id=materia.id,
        cohorte_id=cohorte.id,
        tipo=EvaluacionTipoEnum.PARCIAL,
        instancia="1er Parcial",
        dias_disponibles=2,
        cupos_totales=2
    )
    db_session.add(evaluacion)
    await db_session.flush()

    # Create 3 Alumnos
    alumnos = []
    for i in range(3):
        alumno = Usuario(tenant_id=tenant.id, email=f"alumno{i}@test.com", hashed_password="hash", estado="Activo")
        db_session.add(alumno)
        alumnos.append(alumno)
    await db_session.flush()

    return {
        "tenant_id": tenant.id,
        "evaluacion_id": evaluacion.id,
        "alumnos": alumnos,
    }

@pytest.mark.asyncio
async def test_reserva_evaluacion_success(db_session: AsyncSession, crud_evaluacion_setup):
    setup = crud_evaluacion_setup
    crud = CRUDEvaluacion(db_session, setup["tenant_id"])
    
    reserva_in = ReservaCreate(
        evaluacion_id=setup["evaluacion_id"],
        alumno_id=setup["alumnos"][0].id,
        fecha_hora=datetime(2026, 7, 10, 10, 0)
    )

    reserva = await crud.reservar_evaluacion(reserva_in)
    
    assert reserva is not None
    assert reserva.id is not None
    assert reserva.estado == EstadoReservaEnum.ACTIVA

@pytest.mark.asyncio
async def test_reserva_evaluacion_cupos_excedidos(db_session: AsyncSession, crud_evaluacion_setup):
    setup = crud_evaluacion_setup
    crud = CRUDEvaluacion(db_session, setup["tenant_id"])
    
    # Rellenamos los 2 cupos
    for i in range(2):
        res_in = ReservaCreate(
            evaluacion_id=setup["evaluacion_id"],
            alumno_id=setup["alumnos"][i].id,
            fecha_hora=datetime(2026, 7, 10, 10, 0)
        )
        await crud.reservar_evaluacion(res_in)

    # Intento del tercer alumno (debe fallar por falta de cupo)
    with pytest.raises(ValueError, match="No hay cupos disponibles"):
        res3_in = ReservaCreate(
            evaluacion_id=setup["evaluacion_id"],
            alumno_id=setup["alumnos"][2].id,
            fecha_hora=datetime(2026, 7, 10, 10, 0)
        )
        await crud.reservar_evaluacion(res3_in)

@pytest.mark.asyncio
async def test_reserva_evaluacion_duplicada(db_session: AsyncSession, crud_evaluacion_setup):
    setup = crud_evaluacion_setup
    crud = CRUDEvaluacion(db_session, setup["tenant_id"])
    
    alumno_id = setup["alumnos"][0].id
    res_in = ReservaCreate(
        evaluacion_id=setup["evaluacion_id"],
        alumno_id=alumno_id,
        fecha_hora=datetime(2026, 7, 10, 10, 0)
    )
    
    await crud.reservar_evaluacion(res_in)

    # Intento de reserva duplicada del mismo alumno a la misma evaluación
    with pytest.raises(ValueError, match="El alumno ya tiene una reserva activa"):
        await crud.reservar_evaluacion(res_in)
