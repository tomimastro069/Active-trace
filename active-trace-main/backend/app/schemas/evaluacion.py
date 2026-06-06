from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.evaluacion import EvaluacionTipoEnum, EstadoReservaEnum

class ReservaCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    evaluacion_id: UUID
    alumno_id: UUID
    fecha_hora: datetime

class ReservaResponse(BaseModel):
    id: UUID
    evaluacion_id: UUID
    alumno_id: UUID
    fecha_hora: datetime
    estado: EstadoReservaEnum
    
    model_config = ConfigDict(from_attributes=True)
