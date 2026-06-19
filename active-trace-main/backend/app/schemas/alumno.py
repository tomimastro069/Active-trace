from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID

class AlumnoMateriaResponse(BaseModel):
    materia_id: UUID
    materia_nombre: str
    materia_codigo: str
    cohorte_id: UUID
    cohorte_nombre: str
    porcentaje_progreso: float

    model_config = ConfigDict(from_attributes=True)

class AlumnoActividad(BaseModel):
    actividad: str
    nota_numerica: Optional[float] = None
    nota_textual: Optional[str] = None
    aprobado: bool
    finalizado: bool
    origen: str

    model_config = ConfigDict(from_attributes=True)

class AlumnoProgresoResponse(BaseModel):
    materia_id: UUID
    cohorte_id: UUID
    actividades: List[AlumnoActividad]
    porcentaje_progreso: float

    model_config = ConfigDict(from_attributes=True)
