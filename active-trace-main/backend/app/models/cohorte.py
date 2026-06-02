from sqlalchemy import Column, String, Integer, Date, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampedTenant

class Cohorte(Base, TimestampedTenant):
    """
    Entidad Cohorte (E2).
    Representa una cohorte o periodo académico específico para una Carrera.
    """
    __tablename__ = 'cohortes'

    carrera_id = Column(
        UUID(as_uuid=True),
        ForeignKey('carreras.id', ondelete='CASCADE'),
        nullable=False,
        doc="Relación con la Carrera."
    )

    nombre = Column(
        String(255),
        nullable=False,
        doc="Nombre de la cohorte."
    )

    anio = Column(
        Integer,
        nullable=False,
        doc="Año de cursado."
    )

    vig_desde = Column(
        Date,
        nullable=False,
        doc="Inicio de la vigencia de la cohorte."
    )

    vig_hasta = Column(
        Date,
        nullable=True,
        doc="Fin de la vigencia de la cohorte (opcional)."
    )

    estado = Column(
        String(50),
        default="Activa",
        nullable=False,
        doc="Estado de la cohorte: Activa | Inactiva"
    )

    __table_args__ = (
        UniqueConstraint('tenant_id', 'carrera_id', 'nombre', name='uix_cohorte_tenant_carrera_nombre'),
        Index('idx_cohorte_tenant_carrera_nombre', 'tenant_id', 'carrera_id', 'nombre'),
    )

    def __repr__(self):
        return f"<Cohorte(id={self.id!r}, nombre={self.nombre!r}, anio={self.anio!r})>"
