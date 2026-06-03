from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
import csv
import codecs

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import CurrentUser
from app.schemas.padron import (
    EntradaPadronCreate,
    PadronImportRequest,
    PadronSyncRequest,
    VersionPadronResponse,
    EntradaPadronResponse
)
from app.services.padron_service import PadronService
from app.integrations.moodle_ws import MoodleWSClient

router = APIRouter(prefix="/padron", tags=["padron"])

@router.post("/import", response_model=VersionPadronResponse, status_code=status.HTTP_201_CREATED)
async def import_padron_json(
    payload: PadronImportRequest,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = PadronService(db, current_user.tenant_id)
    try:
        version = await service.importar_padron(
            materia_id=payload.materia_id,
            cohorte_id=payload.cohorte_id,
            entradas_schema=payload.entradas,
            actor_id=current_user.id
        )
        await db.commit()
        return version
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/import-csv", response_model=VersionPadronResponse, status_code=status.HTTP_201_CREATED)
async def import_padron_csv(
    materia_id: UUID = Form(...),
    cohorte_id: UUID = Form(...),
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    # Parse CSV file
    try:
        first_line = await file.read(2048)
        content = first_line.decode('utf-8')
        delimiter = ';' if ';' in content.split('\n')[0] else ','
        await file.seek(0)

        csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'), delimiter=delimiter)
        entradas = []
        for row in csv_reader:
            email = row.get('email', '').strip()
            nombre = row.get('nombre', '').strip()
            apellidos = row.get('apellidos', '').strip()
            if not email or not nombre or not apellidos:
                continue
            
            entradas.append(
                EntradaPadronCreate(
                    email=email,
                    nombre=nombre,
                    apellidos=apellidos,
                    comision=row.get('comision', '').strip() or None,
                    regional=row.get('regional', '').strip() or None
                )
            )
            
        if not entradas:
            raise ValueError("El archivo CSV no contiene registros válidos o faltan campos obligatorios (email, nombre, apellidos).")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al procesar el archivo CSV: {str(e)}"
        )

    service = PadronService(db, current_user.tenant_id)
    try:
        version = await service.importar_padron(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            entradas_schema=entradas,
            actor_id=current_user.id
        )
        await db.commit()
        return version
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/sync", response_model=VersionPadronResponse)
async def sync_padron_moodle(
    payload: PadronSyncRequest,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    import os
    moodle_url = os.getenv("MOODLE_WS_URL", "http://localhost:8080")
    moodle_token = os.getenv("MOODLE_WS_TOKEN", "test-token")
    
    course_id = payload.moodle_course_id if payload.moodle_course_id else 2

    # Instantiate Moodle WS client
    moodle_client = MoodleWSClient(moodle_url, moodle_token)
    
    try:
        # Fetch from Moodle WS (handles tenacity retries internally)
        entradas = await moodle_client.get_enrolled_students(course_id)
    except Exception as e:
        # Fail gracefully without corrupting DB
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al sincronizar con Moodle WS: {str(e)}"
        )

    service = PadronService(db, current_user.tenant_id)
    try:
        version = await service.importar_padron(
            materia_id=payload.materia_id,
            cohorte_id=payload.cohorte_id,
            entradas_schema=entradas,
            actor_id=current_user.id
        )
        await db.commit()
        return version
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/vaciar")
async def vaciar_padron(
    payload: PadronSyncRequest,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = PadronService(db, current_user.tenant_id)
    try:
        await service.vaciar_padron(
            materia_id=payload.materia_id,
            cohorte_id=payload.cohorte_id,
            actor_id=current_user.id
        )
        await db.commit()
        return {"status": "success", "detail": "Padrón vaciado correctamente."}
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/active", response_model=Optional[VersionPadronResponse])
async def get_active_version(
    materia_id: UUID,
    cohorte_id: UUID,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = PadronService(db, current_user.tenant_id)
    return await service.get_active_version(materia_id, cohorte_id)

@router.get("/entries/{version_id}", response_model=List[EntradaPadronResponse])
async def get_entries(
    version_id: UUID,
    current_user: CurrentUser = Depends(require_permission("estructura:gestionar")),
    db: AsyncSession = Depends(get_db)
):
    service = PadronService(db, current_user.tenant_id)
    return await service.get_entradas(version_id)
