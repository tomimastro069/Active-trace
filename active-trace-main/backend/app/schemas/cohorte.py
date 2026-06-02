from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import date, datetime
from typing import Optional

class CohorteBase(BaseModel):
    carrera_id: UUID = Field(..., description="ID de la carrera asociada")
    nombre: str = Field(..., max_length=255, description="Nombre de la cohorte")
    anio: int = Field(..., description="Año de cursado")
    vig_desde: date = Field(..., description="Fecha de inicio de vigencia")
    vig_hasta: Optional[date] = Field(None, description="Fecha de fin de vigencia")
    estado: str = Field("Activa", description="Estado de la cohorte: Activa o Inactiva")

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True
    )

class CohorteCreate(BaseModel):
    carrera_id: UUID
    nombre: str = Field(..., max_length=255)
    anio: int
    vig_desde: date
    vig_hasta: Optional[date] = None
    estado: Optional[str] = Field("Activa")

    model_config = ConfigDict(
        extra="forbid"
    )

class CohorteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=255)
    anio: Optional[int] = None
    vig_desde: Optional[date] = None
    vig_hasta: Optional[date] = None
    estado: Optional[str] = Field(None, description="Cambiar a Activa o Inactiva")

    model_config = ConfigDict(
        extra="forbid"
    )

class CohorteResponse(CohorteBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
