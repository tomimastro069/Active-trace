# padron-ingesta Specification

## Purpose

Define el mecanismo de importación y versionado de padrones de alumnos inscritos en materias y cohortes. Provee la base de estudiantes sobre los que operan las calificaciones y el seguimiento académico, soportando tanto cargas masivas manuales (CSV/XLSX) como integración sincrónica con el LMS (Moodle).

## Requirements

### Requirement: Versionado Único Activo

The system MUST guarantee that only one version of the padron is active at any given time for a specific combination of Materia and Cohorte.

#### Scenario: Carga de un nuevo padrón

- GIVEN a Materia and Cohorte with an existing active VersionPadron (v1)
- WHEN a new padron is successfully imported for the same Materia and Cohorte (v2)
- THEN v2 MUST be marked as `activa = True`
- AND v1 MUST be marked as `activa = False` atomically in the same transaction.

### Requirement: Soporte a Alumnos sin Cuenta Registrada

The system SHALL allow the ingestion of students who do not yet have a registered `Usuario` account in the system.

#### Scenario: Alumno importado sin cuenta existente

- GIVEN a student record in the imported padron with an email that does not exist in the `Usuario` table
- WHEN the padron is processed
- THEN the system SHALL create an `EntradaPadron` for the student
- AND the `usuario_id` field for that entry MUST be `null`
- AND the system MUST persist the student's email, name, and surname in the `EntradaPadron` for future linkage.

### Requirement: Fallback y Resiliencia en Integración LMS

The system MUST handle transient network failures (e.g., HTTP 502 Bad Gateway) when interacting with external LMS Web Services gracefully.

#### Scenario: Falla transitoria de Moodle WS

- GIVEN a request to synchronize the padron via Moodle WS
- WHEN the Moodle server responds with an HTTP 502 error
- THEN the system MUST retry the request according to a configured retry policy
- AND if all retries fail, the system MUST abort the synchronization without corrupting any local active padron version
- AND the system MUST return a clean error to the caller indicating the upstream failure.

### Requirement: Auditoría de Ingesta y Vaciado

The system MUST generate an immutable audit log entry for every successful padron load and explicitly requested data clearing.

#### Scenario: Auditoría de carga manual de padrón

- GIVEN a user with appropriate permissions
- WHEN the user successfully uploads and processes a CSV/XLSX padron
- THEN the system MUST generate an audit log entry with action `PADRON_CARGAR`.

#### Scenario: Vaciado de datos de materia

- GIVEN an active padron for a Materia and Cohorte
- WHEN an authorized user triggers the "Empty data" action for that subject
- THEN the system MUST mark the current active `VersionPadron` as inactive (`activa = False`)
- AND the system MUST generate an audit log entry with action `PADRON_VACIAR`.
