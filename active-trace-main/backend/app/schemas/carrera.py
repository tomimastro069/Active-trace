from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class CarreraBase(BaseModel):
    codigo: str = Field(..., max_length=100, description="Código de la carrera")
    nombre: str = Field(..., max_length=255, description="Nombre de la carrera")
    estado: str = Field("Activa", description="Estado de la carrera: Activa o Inactiva")

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True
    )

class CarreraCreate(BaseModel):
    codigo: str = Field(..., max_length=100)
    nombre: str = Field(..., max_length=255)
    estado: Optional[str] = Field("Activa")

    model_config = ConfigDict(
        extra="forbid"
    )

class CarreraUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=255)
    estado: Optional[str] = Field(None, description="Cambiar a Activa o Inactiva")

    model_config = ConfigDict(
        extra="forbid"
    )

class CarreraResponse(CarreraBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
