from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class MateriaBase(BaseModel):
    codigo: str = Field(..., max_length=100, description="Código de la materia")
    nombre: str = Field(..., max_length=255, description="Nombre de la materia")
    estado: str = Field("Activa", description="Estado de la materia: Activa o Inactiva")

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True
    )

class MateriaCreate(BaseModel):
    codigo: str = Field(..., max_length=100)
    nombre: str = Field(..., max_length=255)
    estado: Optional[str] = Field("Activa")

    model_config = ConfigDict(
        extra="forbid"
    )

class MateriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=255)
    estado: Optional[str] = Field(None, description="Cambiar a Activa o Inactiva")

    model_config = ConfigDict(
        extra="forbid"
    )

class MateriaResponse(MateriaBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
