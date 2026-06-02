## ADDED Requirements

### Requirement: Soft delete append-only pattern
The system SHALL never perform hard deletes (DELETE SQL command) on any domain model. All deletes SHALL mark `deleted_at` timestamp. Queries by default SHALL exclude soft-deleted records. The soft-delete pattern enables append-only audit logging: all changes (creation, modification, deletion) are recorded and recoverable.

#### Scenario: Logical delete marks timestamp, preserves data
- **WHEN** a record is deleted via the application (e.g., `repository.delete_logical(id)`)
- **THEN** the record's `deleted_at` column is set to the current timestamp
- **AND** the record is NOT removed from the database
- **AND** the record can be recovered by setting `deleted_at = NULL`

#### Scenario: Default queries exclude deleted records
- **WHEN** any query (e.g., `list_all()`, `get_by_id()`) is executed
- **THEN** the query automatically adds `WHERE deleted_at IS NULL`
- **AND** soft-deleted records are not visible to normal application flows

#### Scenario: Hard delete rejection
- **WHEN** code attempts to execute `DELETE FROM model WHERE ...` directly
- **THEN** code review SHALL reject it
- **AND** only soft delete via repository is permitted

#### Scenario: Audit trail preservation
- **WHEN** a record is soft-deleted, an audit entry is created (in C-05)
- **THEN** the audit log records the deletion action with actor, timestamp, and reason
- **AND** the original record remains queryable by audit/admin processes
