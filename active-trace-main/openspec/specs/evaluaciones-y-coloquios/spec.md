# evaluaciones-y-coloquios Specification

## Purpose

Gestión de convocatorias de exámenes orales (coloquios y evaluaciones), permitiendo la asignación de cupos globales, la reserva de turnos por parte de los alumnos, la visualización de métricas de ocupación y el registro de calificaciones finales.

## Requirements

## Requirement: Crear Convocatoria

El sistema MUST permitir a un coordinador crear una convocatoria de evaluación con una fecha límite, un conjunto de días de examen y un cupo de reservas global.

#### Scenario: Creación exitosa de convocatoria
- GIVEN un coordinador autenticado en el tenant
- WHEN crea una evaluación de tipo `Coloquio` con cupo total 10 y días `["2026-07-06", "2026-07-07"]`
- THEN el sistema MUST guardar la evaluación asociada al tenant
- AND el estado inicial MUST ser `Activo`

#### Scenario: Rechazo por rol inválido
- GIVEN un alumno autenticado
- WHEN intenta crear una convocatoria de evaluación
- THEN el sistema MUST rechazar con error `403 Forbidden`

## Requirement: Reservar Turno de Examen

El sistema MUST permitir a un alumno convocado elegir un día de examen disponible y realizar una reserva de turno de forma atómica, reduciendo el cupo disponible de la evaluación.

#### Scenario: Reserva exitosa de turno
- GIVEN un alumno convocado a un coloquio con cupo disponible
- WHEN el alumno realiza la reserva para el día `"2026-07-06"`
- THEN el sistema MUST crear una `ReservaEvaluacion` en estado `Activa`
- AND el cupo disponible de la evaluación MUST disminuir en 1

#### Scenario: Intento de reserva concurrente sin cupo
- GIVEN un coloquio con cupo disponible igual a 0
- WHEN un alumno intenta realizar una reserva
- THEN el sistema MUST rechazar la reserva con un error `400 Bad Request`

#### Scenario: Evitar reserva duplicada
- GIVEN un alumno que ya posee una reserva activa para un coloquio
- WHEN intenta realizar otra reserva para el mismo coloquio en un día diferente
- THEN el sistema MUST rechazar la transacción con un error `400 Bad Request`

## Requirement: Registrar Resultado

El sistema MUST permitir a un docente o coordinador asentar la calificación obtenida por un alumno en su reserva de evaluación.

#### Scenario: Calificación exitosa
- GIVEN un docente autenticado y una reserva en estado `Activa`
- WHEN registra una nota de 8 y resultado `Aprobado`
- THEN el sistema MUST crear el `ResultadoEvaluacion` correspondiente
- AND el estado de la reserva MUST actualizarse a `Evaluada`

## Requirement: Consultar Métricas

El sistema MUST proveer a la coordinación métricas consolidadas sobre el estado de reservas y cupos de cada coloquio en tiempo real.

#### Scenario: Obtener métricas de coloquio
- GIVEN un coordinador autenticado
- WHEN solicita las métricas de un coloquio
- THEN el sistema MUST retornar la cantidad de alumnos convocados, total de reservas realizadas y cupos libres restantes.
