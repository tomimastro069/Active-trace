from sqlalchemy import Column, String, UniqueConstraint, Index
from app.models.base import Base, TimestampedTenant

class Carrera(Base, TimestampedTenant):
    """
    Entidad Carrera (E1).
    Representa un programa académico ofrecido por un Tenant.
    """
    __tablename__ = 'carreras'

    codigo = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Código único de la carrera dentro de un tenant."
    )

    nombre = Column(
        String(255),
        nullable=False,
        doc="Nombre de la carrera."
    )

    estado = Column(
        String(50),
        default="Activa",
        nullable=False,
        doc="Estado de la carrera: Activa | Inactiva"
    )

    __table_args__ = (
        UniqueConstraint('tenant_id', 'codigo', name='uix_carrera_tenant_codigo'),
        Index('idx_carrera_tenant_codigo', 'tenant_id', 'codigo'),
    )

    def __repr__(self):
        return f"<Carrera(id={self.id!r}, codigo={self.codigo!r}, nombre={self.nombre!r})>"
