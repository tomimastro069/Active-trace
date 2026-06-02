from typing import TypeVar, Generic, Type, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.base import TimestampedTenant

T = TypeVar('T', bound=TimestampedTenant)


class BaseRepository(Generic[T]):
    """
    Generic repository with automatic tenant scope.
    
    All queries automatically filter by tenant_id. A query without tenant scope
    is a defect that code review should catch.
    
    Usage:
        class UserRepository(BaseRepository[User]):
            pass
        
        repo = UserRepository(User, session, tenant_id)
        users = await repo.list_all(skip=0, limit=10)
    """
    
    def __init__(self, model: Type[T], session: AsyncSession, tenant_id: UUID):
        """
        Initialize repository with model, session, and tenant context.
        
        Args:
            model: ORM model class (must inherit from TimestampedTenant)
            session: AsyncSession instance
            tenant_id: UUID of the current tenant (ALL queries scoped to this)
        """
        self.model = model
        self.session = session
        self.tenant_id = tenant_id
    
    def _apply_tenant_scope(self, query):
        """
        Apply tenant filter to a query.
        
        This ensures that ALL queries are scoped to the current tenant.
        A query without this scope is a bug.
        """
        if self.tenant_id is None:
            raise ValueError(
                "tenant_id is None. Cannot execute query without tenant scope. "
                "Ensure get_current_tenant() is working and session has tenant context."
            )
        
        # Filter by tenant_id AND deleted_at IS NULL (active records only)
        return query.where(
            and_(
                self.model.tenant_id == self.tenant_id,
                self.model.deleted_at.is_(None)
            )
        )
    
    async def get_by_id(self, record_id: UUID) -> Optional[T]:
        """
        Retrieve a single record by ID, scoped to current tenant.
        
        Returns None if record not found or belongs to another tenant.
        """
        query = select(self.model).where(self.model.id == record_id)
        query = self._apply_tenant_scope(query)
        
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        List all active records for the current tenant.
        
        Returns only records where deleted_at IS NULL (soft-deleted excluded).
        """
        query = select(self.model).offset(skip).limit(limit)
        query = self._apply_tenant_scope(query)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create(self, obj: T) -> T:
        """
        Create and persist a new record.
        
        The record's tenant_id is automatically set to the current tenant.
        """
        if obj.tenant_id is None:
            obj.tenant_id = self.tenant_id
        
        self.session.add(obj)
        await self.session.flush()
        return obj
    
    async def update(self, obj: T) -> T:
        """
        Update an existing record.
        
        The record is merged into the session and flushed.
        updated_at is automatically updated by the ORM.
        """
        # Verify that the record belongs to the current tenant
        existing = await self.get_by_id(obj.id)
        if existing is None:
            raise ValueError(
                f"Record {obj.id} not found or belongs to another tenant. "
                f"Cannot update a record from a different tenant."
            )
        
        # Merge and flush
        await self.session.merge(obj)
        await self.session.flush()
        return obj
    
    async def delete_logical(self, record_id: UUID) -> None:
        """
        Soft delete: mark deleted_at timestamp, do NOT physically delete.
        
        The record remains in the database (for audit trail) but is
        excluded from queries by default.
        """
        record = await self.get_by_id(record_id)
        if record is None:
            raise ValueError(
                f"Record {record_id} not found or belongs to another tenant."
            )
        
        from datetime import datetime
        record.deleted_at = datetime.utcnow()
        await self.session.flush()
    
    async def count(self) -> int:
        """Count active records for the current tenant."""
        query = select(self.model)
        query = self._apply_tenant_scope(query)
        
        result = await self.session.execute(query)
        return len(result.scalars().all())
