## ADDED Requirements

### Requirement: Generic repository with automatic tenant scope
The system SHALL provide a `BaseRepository[T]` generic class that implements standard CRUD operations. All queries executed through a repository SHALL automatically filter by the current tenant's `tenant_id`. No query may bypass this scope; a query without tenant scope is a defect.

#### Scenario: Automatic tenant filtering on list operation
- **WHEN** code calls `repository.list_all(skip=0, limit=10)`
- **THEN** the repository executes `SELECT * FROM model WHERE tenant_id = :tenant_id AND deleted_at IS NULL LIMIT 10 OFFSET 0`
- **AND** tenant_id is resolved from the current session context (via `get_current_tenant()`)

#### Scenario: CRUD operations respect tenant scope
- **WHEN** a repository method (create, update, get_by_id, delete_logical) is called
- **THEN** all operations automatically include the tenant filter
- **AND** if a record belongs to a different tenant, it is treated as not found (404, not permission error)

#### Scenario: Cross-tenant query prevention
- **WHEN** code attempts to query without tenant scope (using raw SQL or ORM without repository)
- **THEN** unit tests SHALL catch this during development
- **AND** code review SHALL require repository pattern for all DB access
