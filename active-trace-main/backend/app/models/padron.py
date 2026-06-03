from sqlalchemy import Column, String, Boolean, ForeignKey, UniqueConstraint, Index, text
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy.orm import relationship, validates
from app.models.base import Base, TimestampedTenant
from app.core.types import EncryptedString

class VersionPadron(Base, TimestampedTenant):
    """
    Entidad VersionPadron (E-VP).
    Representa una versión de un padrón de alumnos para una Materia y Cohorte específicas.
    """
    __tablename__ = 'version_padron'

    materia_id = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey('materias.id', ondelete='CASCADE'),
        nullable=False,
        doc="Relación con la Materia."
    )

    cohorte_id = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey('cohortes.id', ondelete='CASCADE'),
        nullable=False,
        doc="Relación con la Cohorte."
    )

    activa = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Indica si esta es la versión activa del padrón para la materia y cohorte."
    )

    materia = relationship("Materia")
    cohorte = relationship("Cohorte")
    entradas = relationship("EntradaPadron", back_populates="version", cascade="all, delete-orphan")

    __table_args__ = (
        # Unique partial index to ensure only one active version per (tenant_id, materia_id, cohorte_id)
        Index(
            'uix_version_padron_active',
            'tenant_id', 'materia_id', 'cohorte_id',
            unique=True,
            postgresql_where=text("activa = true AND deleted_at IS NULL")
        ),
        Index('idx_version_padron_lookup', 'tenant_id', 'materia_id', 'cohorte_id'),
    )

    def __repr__(self):
        return f"<VersionPadron(id={self.id!r}, materia_id={self.materia_id!r}, cohorte_id={self.cohorte_id!r}, activa={self.activa!r})>"


class EntradaPadron(Base, TimestampedTenant):
    """
    Entidad EntradaPadron (E-EP).
    Representa un registro individual de alumno dentro de una versión específica del padrón.
    """
    __tablename__ = 'entrada_padron'

    version_id = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey('version_padron.id', ondelete='CASCADE'),
        nullable=False,
        doc="Relación con la versión del padrón."
    )

    usuario_id = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey('usuario.id', ondelete='SET NULL'),
        nullable=True,
        doc="Relación con el usuario registrado en el sistema, o NULL si aún no tiene cuenta."
    )

    email = Column(
        EncryptedString(255),
        nullable=False,
        doc="Email del estudiante. Cifrado en reposo."
    )

    email_hash = Column(
        String(64),
        nullable=False,
        doc="Hash determinista del email para búsquedas rápidas y unicidad dentro del padrón."
    )

    nombre = Column(
        String(100),
        nullable=False,
        doc="Nombre del estudiante."
    )

    apellidos = Column(
        String(100),
        nullable=False,
        doc="Apellidos del estudiante."
    )

    comision = Column(
        String(100),
        nullable=True,
        doc="Comisión asignada (opcional)."
    )

    regional = Column(
        String(100),
        nullable=True,
        doc="Regional o sede asociada (opcional)."
    )

    version = relationship("VersionPadron", back_populates="entradas")
    usuario = relationship("Usuario")

    @validates("email")
    def validate_email(self, key, value):
        from app.core.security import generate_email_hash
        self.email_hash = generate_email_hash(value)
        return value

    __table_args__ = (
        Index('idx_entrada_padron_lookup', 'tenant_id', 'version_id', 'email_hash'),
        Index('idx_entrada_padron_usuario', 'tenant_id', 'usuario_id'),
    )

    def __repr__(self):
        return f"<EntradaPadron(id={self.id!r}, email_hash={self.email_hash!r}, nombre={self.nombre!r})>"
