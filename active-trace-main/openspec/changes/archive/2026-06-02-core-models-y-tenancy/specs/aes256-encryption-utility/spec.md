## ADDED Requirements

### Requirement: AES-256 encryption utility for sensitive attributes
The system SHALL provide encryption/decryption utilities for sensitive PII attributes (DNI, CUIL, CBU, email when necessary). Sensitive attributes SHALL be stored encrypted in the database. The encryption key SHALL be managed via `ENCRYPTION_KEY` environment variable (32 bytes exactly). Decryption errors SHALL be logged securely without exposing plaintext or encrypted data in error messages.

#### Scenario: Encrypt attribute before storing
- **WHEN** a sensitive attribute (e.g., DNI) is assigned to a model before saving
- **THEN** the model's `pre_commit` hook or service layer calls `encrypt_attr(value)`
- **AND** the encrypted cipher (not plaintext) is stored in the database column

#### Scenario: Decrypt attribute after retrieving
- **WHEN** a model with encrypted attributes is loaded from the database
- **THEN** the repository or service calls `decrypt_attr(cipher)` on sensitive columns
- **AND** the plaintext is returned only in memory (never in logs or exception messages)

#### Scenario: Encryption roundtrip integrity
- **WHEN** a value is encrypted and then immediately decrypted
- **THEN** the decrypted value matches the original plaintext exactly
- **AND** decryption with a different key fails with a clear error

#### Scenario: PII never exposed in logs
- **WHEN** an encrypted attribute is logged or included in an exception message
- **THEN** only the encrypted cipher is logged, never the plaintext
