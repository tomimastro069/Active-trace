from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class DailyActivity(BaseModel):
    date: str
    count: int

class TeacherStatusCount(BaseModel):
    teacher_id: UUID
    status: str
    count: int

class TeacherSubjectInteraction(BaseModel):
    teacher_id: UUID
    subject_id: Optional[UUID]
    count: int

class AuditMetricsResponse(BaseModel):
    daily_activity: List[DailyActivity]
    teacher_communications: List[TeacherStatusCount]
    teacher_subject_interactions: List[TeacherSubjectInteraction]

class AuditLogQuerySchema(BaseModel):
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    materia_id: Optional[UUID] = None
    actor_id: Optional[UUID] = None
    limit: int = Field(default=200, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

class AuditLogResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    fecha_hora: datetime
    actor_id: UUID
    impersonado_id: Optional[UUID]
    materia_id: Optional[UUID]
    accion: str
    detalle: Optional[Any]
    filas_afectadas: Optional[int]
    ip: Optional[str]
    user_agent: Optional[str]

    class Config:
        orm_mode = True
