## ADDED Requirements

### Requirement: Timestamped tenant mixin for reusable model base
The system SHALL provide a `TimestampedTenant` mixin class that all domain models inherit from. The mixin SHALL include: `id` (UUID primary key), `tenant_id` (UUID foreign key to Tenant), `created_at` (datetime, set at creation), `updated_at` (datetime, updated on modification), `deleted_at` (datetime nullable, for soft delete).

#### Scenario: Model inherits mixin correctly
- **WHEN** a new domain model (e.g., `Usuario`) inherits from `TimestampedTenant`
- **THEN** the model automatically has all five fields without duplication
- **AND** timestamps are automatically managed (created_at immutable, updated_at on save)

#### Scenario: Soft delete marking
- **WHEN** a record is marked as deleted via the repository
- **THEN** `deleted_at` is set to the current timestamp
- **AND** the record is NOT physically removed from the database
- **AND** subsequent queries exclude records where `deleted_at IS NOT NULL` by default
