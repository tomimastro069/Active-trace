## ADDED Requirements

### Requirement: Tenant model as root entity
The system SHALL provide a `Tenant` model that represents each institutional client. Every table in the database SHALL reference a tenant via `tenant_id` foreign key. A tenant is the root scope for data isolation.

#### Scenario: Tenant creation and retrieval
- **WHEN** a new tenant is created with a unique name
- **THEN** the system assigns a UUID `id` and stores the tenant record
- **AND** when a query accesses that tenant's data, other tenants cannot be visible

#### Scenario: Tenant identity isolation
- **WHEN** two tenants exist (Tenant A and Tenant B)
- **AND** Tenant A attempts to query data belonging to Tenant B
- **THEN** the query returns empty or 403 Forbidden
