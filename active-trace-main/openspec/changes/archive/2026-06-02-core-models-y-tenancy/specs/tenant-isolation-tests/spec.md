## ADDED Requirements

### Requirement: Multi-tenant isolation tests
The system SHALL include comprehensive tests that verify data isolation between tenants, soft delete behavior, encryption roundtrip, and timestamp derivation. Tests SHALL run against a real test database (not mocks) to validate actual isolation at the database level.

#### Scenario: Tenant A cannot access Tenant B data
- **WHEN** a user from Tenant A performs a query
- **THEN** only records where `tenant_id = Tenant A's id` are returned
- **AND** records from Tenant B are never returned, even if they exist in the database

#### Scenario: Soft delete is transparent to queries
- **WHEN** a record is soft-deleted and a query is performed
- **THEN** the soft-deleted record is not included in results
- **AND** when `deleted_at` is set back to NULL, the record reappears in queries

#### Scenario: Encryption roundtrip preserves data
- **WHEN** an encrypted attribute is stored and retrieved
- **THEN** the decrypted value matches the original plaintext
- **AND** the encrypted value in the database is different from plaintext

#### Scenario: Timestamps are automatically managed
- **WHEN** a model instance is created
- **THEN** `created_at` is automatically set to the current time
- **AND** `updated_at` is also set to creation time
- **WHEN** the model is updated
- **THEN** `updated_at` changes, but `created_at` remains unchanged

#### Scenario: Multi-tenant test isolation
- **WHEN** tests run for different tenants
- **THEN** each test uses a unique tenant context
- **AND** test data from one tenant does not leak into another tenant's tests
