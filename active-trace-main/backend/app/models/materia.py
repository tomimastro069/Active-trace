from sqlalchemy import Column, String, UniqueConstraint, Index
from app.models.base import Base, TimestampedTenant

class Materia(Base, TimestampedTenant):
    """
    Entidad Materia (E3).
    Representa una asignatura de catálogo única dentro de un Tenant.
    """
    __tablename__ = 'materias'

    codigo = Column(
        String(100),
        nullable=False,
        index=True,
        doc="Código único de la materia dentro de un tenant."
    )

    nombre = Column(
        String(255),
        nullable=False,
        doc="Nombre de la materia."
    )

    estado = Column(
        String(50),
        default="Activa",
        nullable=False,
        doc="Estado de la materia: Activa | Inactiva"
    )

    __table_args__ = (
        UniqueConstraint('tenant_id', 'codigo', name='uix_materia_tenant_codigo'),
        Index('idx_materia_tenant_codigo', 'tenant_id', 'codigo'),
    )

    def __repr__(self):
        return f"<Materia(id={self.id!r}, codigo={self.codigo!r}, nombre={self.nombre!r})>"
