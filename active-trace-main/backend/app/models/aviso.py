from sqlalchemy import Column, String, DateTime, Integer, Boolean, Enum as SQLAlchemyEnum, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum
from .base import Base, TimestampedTenant


class AlcanceEnum(str, Enum):
    GLOBAL = "GLOBAL"
    POR_MATERIA = "POR_MATERIA"
    POR_COHORTE = "POR_COHORTE"
    POR_ROL = "POR_ROL"


class Aviso(TimestampedTenant, Base):
    __tablename__ = 'avisos'

    alcance = Column(SQLAlchemyEnum(AlcanceEnum), nullable=False)
    materia_id = Column(UUID(as_uuid=True), nullable=True)
    cohorte_id = Column(UUID(as_uuid=True), nullable=True)
    rol_destino = Column(String, nullable=True)
    
    severidad = Column(String, nullable=False)
    titulo = Column(String, nullable=False)
    cuerpo = Column(Text, nullable=False)
    
    inicio_en = Column(DateTime, nullable=False)
    fin_en = Column(DateTime, nullable=False)
    
    orden = Column(Integer, default=0, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    requiere_ack = Column(Boolean, default=False, nullable=False)


class AcknowledgmentAviso(TimestampedTenant, Base):
    __tablename__ = 'acknowledgment_avisos'

    aviso_id = Column(UUID(as_uuid=True), ForeignKey('avisos.id'), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (
        UniqueConstraint('aviso_id', 'usuario_id', name='uq_aviso_usuario_ack'),
    )
