## ADDED Requirements

### Requirement: Alembic async migration framework setup
The system SHALL initialize Alembic for database schema migrations. The configuration SHALL support async SQLAlchemy engine. Alembic's `env.py` SHALL be configured to use the async engine from `core/database.py`. The first migration (Migration 001) SHALL create the `Tenant` table and establish the multi-tenant foundation.

#### Scenario: Alembic initialization with async engine
- **WHEN** the backend initializes for the first time
- **THEN** `alembic/versions/` directory exists and is ready for migration files
- **AND** `alembic/env.py` is configured to work with async SQLAlchemy
- **AND** running `alembic upgrade head` applies migrations to the test database

#### Scenario: First migration creates tenant table
- **WHEN** `alembic upgrade head` is executed
- **THEN** Migration 001 creates table `tenant` with columns: `id` (UUID PK), `name` (text), `created_at`, `updated_at`, `deleted_at`
- **AND** subsequent tables will have `tenant_id` foreign key to this table

#### Scenario: Rollback capability
- **WHEN** `alembic downgrade -1` is executed
- **THEN** the most recent migration is reversed
- **AND** the database schema returns to the state before that migration
