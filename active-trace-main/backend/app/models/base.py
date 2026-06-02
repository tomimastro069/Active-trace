from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy import Column, DateTime, UUID as SQLAlchemyUUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class TimestampedTenant:
    """
    Mixin base for all domain models.
    
    Provides:
    - id: UUID primary key (unique per system)
    - tenant_id: UUID foreign key (scopes data isolation)
    - created_at: Timestamp of creation (immutable)
    - updated_at: Timestamp of last modification
    - deleted_at: Timestamp of soft delete (NULL if active)
    
    All domain models inherit from this mixin.
    """
    
    id = Column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )
    
    tenant_id = Column(
        SQLAlchemyUUID(as_uuid=True),
        nullable=True  # Will be set by parent Tenant model
    )
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        update_expression=None  # Immutable after creation
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    deleted_at = Column(
        DateTime,
        nullable=True  # NULL = active, not NULL = soft deleted
    )
    
    @hybrid_property
    def is_deleted(self):
        """Property to check if record is soft-deleted"""
        return self.deleted_at is not None
