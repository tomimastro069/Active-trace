from pydantic import BaseModel, ConfigDict, Field, EmailStr
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class EntradaPadronCreate(BaseModel):
    usuario_id: Optional[UUID] = Field(None, description="ID del usuario si ya está registrado en el sistema")
    nombre: str = Field(..., max_length=100, description="Nombre del estudiante")
    apellidos: str = Field(..., max_length=100, description="Apellidos del estudiante")
    email: EmailStr = Field(..., description="Email del estudiante")
    comision: Optional[str] = Field(None, max_length=100, description="Comisión asignada")
    regional: Optional[str] = Field(None, max_length=100, description="Regional o sede")

    model_config = ConfigDict(
        extra="forbid"
    )

class EntradaPadronResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    version_id: UUID
    usuario_id: Optional[UUID] = None
    email: str = Field(..., description="Email del estudiante (desencriptado)")
    nombre: str
    apellidos: str
    comision: Optional[str] = None
    regional: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True
    )

class VersionPadronResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    materia_id: UUID
    cohorte_id: UUID
    activa: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True
    )

class PadronImportRequest(BaseModel):
    materia_id: UUID = Field(..., description="ID de la materia")
    cohorte_id: UUID = Field(..., description="ID de la cohorte")
    entradas: List[EntradaPadronCreate] = Field(..., min_length=1, description="Lista de entradas de estudiantes a importar")

    model_config = ConfigDict(
        extra="forbid"
    )

class PadronSyncRequest(BaseModel):
    materia_id: UUID = Field(..., description="ID de la materia")
    cohorte_id: UUID = Field(..., description="ID de la cohorte")
    moodle_course_id: Optional[int] = Field(None, description="ID del curso en Moodle (opcional)")

    model_config = ConfigDict(
        extra="forbid"
    )
