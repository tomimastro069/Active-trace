"""Tenant table creation.

Revision ID: 001_tenant
Revises: 
Create Date: 2026-06-02 11:12:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from uuid import UUID


# revision identifiers, used by Alembic.
revision = '001_tenant'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the tenant table - root of multi-tenant isolation."""
    op.create_table(
        'tenant',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_tenant_name')
    )
    
    # Create indexes for common queries
    op.create_index('idx_tenant_created_at', 'tenant', ['created_at'])
    op.create_index('idx_tenant_deleted_at', 'tenant', ['deleted_at'])


def downgrade() -> None:
    """Drop the tenant table."""
    op.drop_index('idx_tenant_deleted_at', table_name='tenant')
    op.drop_index('idx_tenant_created_at', table_name='tenant')
    op.drop_table('tenant')
