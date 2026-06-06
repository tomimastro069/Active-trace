from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.aviso import AlcanceEnum

class AvisoBase(BaseModel):
    alcance: AlcanceEnum
    materia_id: Optional[UUID] = None
    cohorte_id: Optional[UUID] = None
    rol_destino: Optional[str] = None
    severidad: str
    titulo: str
    cuerpo: str
    inicio_en: datetime
    fin_en: datetime
    orden: int = 0
    activo: bool = True
    requiere_ack: bool = False

class AvisoCreate(AvisoBase):
    pass

class AvisoResponse(AvisoBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AcknowledgmentAvisoCreate(BaseModel):
    aviso_id: UUID

class AcknowledgmentAvisoResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    aviso_id: UUID
    usuario_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
