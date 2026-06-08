# frontend-academico-docente Specification

## Purpose
Establecer las interfaces de usuario del rol PROFESOR y TUTOR para gestionar la comisión, previsualizar e importar calificaciones, configurar umbrales de aprobación, visualizar alertas de atraso, gestionar entregas pendientes de corrección y realizar el envío y seguimiento de las comunicaciones con alumnos.

## Requirements

### Requirement: Importación de Calificaciones y Umbrales
El sistema MUST permitir al docente importar calificaciones subiendo un archivo CSV/hoja de cálculo, mostrar una previsualización de actividades detectadas para su selección, definir el umbral mínimo de aprobación (por defecto 60%) y los valores textuales equivalentes, y permitir vaciar las notas de la materia.

#### Scenario: Previsualización e importación exitosa
- GIVEN un usuario autenticado con rol PROFESOR en la vista de importación
- WHEN sube un archivo de calificaciones CSV y selecciona las actividades
- THEN el sistema renderiza la vista previa de calificaciones y al confirmar persiste las notas en el backend

#### Scenario: Configuración de umbral y limpieza
- GIVEN un PROFESOR gestionando su comisión
- WHEN define el umbral en 70% o solicita vaciar las calificaciones
- THEN el sistema actualiza la configuración del umbral y elimina/actualiza los registros reflejando el cambio de inmediato

---

### Requirement: Visualización de Atrasados, Rankings y Reportes
El sistema MUST calcular y presentar la lista de alumnos atrasados (notas < umbral o tareas faltantes), el ranking de alumnos por tareas aprobadas, y tarjetas de reportes rápidos con métricas consolidadas.

#### Scenario: Visualización de la tabla de atrasados
- GIVEN un docente en la pestaña de alumnos atrasados
- WHEN carga la vista de la comisión
- THEN el sistema muestra la tabla de alumnos atrasados con sus tareas faltantes y permite filtrar la lista

#### Scenario: Consulta del ranking y notas finales
- GIVEN un docente en la pestaña de reportes
- WHEN selecciona ver el ranking
- THEN el sistema presenta una lista ordenada descendentemente por cantidad de tareas aprobadas (mínimo 1) y los promedios finales

---

### Requirement: Detección y Exportación de Trabajos sin Corregir
El sistema MUST permitir subir un reporte de finalización del LMS, cruzarlo con las calificaciones para detectar entregas sin calificar, y exportar dicho listado en un archivo CSV.

#### Scenario: Carga de reporte de finalización y export
- GIVEN un PROFESOR con un reporte de finalización de actividades
- WHEN importa el archivo y hace clic en exportar
- THEN el sistema cruza los datos, muestra las entregas pendientes de corrección y descarga un archivo CSV con el reporte

---

### Requirement: Envío y Seguimiento de Comunicaciones en Tiempo Real
El sistema MUST permitir seleccionar alumnos atrasados, mostrar una previsualización del email personalizado con datos dinámicos, disparar el envío masivo en cola, y monitorear el estado del lote (Pendiente, Enviando, Enviado, Fallido) mediante polling automático cada 5 segundos.

#### Scenario: Previsualización y envío de comunicación
- GIVEN un PROFESOR con alumnos atrasados seleccionados
- WHEN ingresa el template y confirma tras ver la previsualización individual
- THEN el sistema encola los mensajes e inicia el tracking en tiempo real

#### Scenario: Tracking con polling de lotes
- GIVEN un lote de comunicaciones en estado PENDIENTE o ENVIANDO
- WHEN se visualiza la sección de tracking de comunicaciones
- THEN el sistema realiza polling cada 5 segundos al backend hasta que todas las filas alcancen un estado final (Enviado/Fallido/Cancelado)

---

### Requirement: Monitor de Seguimiento de Alumnos (Tutor/Profesor)
El sistema MUST proveer una vista transversal filtrable de alumnos asignados para tutores y profesores, permitiendo acotar por alumno, comisión, regional y porcentaje de cumplimiento.

#### Scenario: Búsqueda filtrada de estudiantes
- GIVEN un TUTOR en la vista del monitor de seguimiento
- WHEN busca por comisión o filtra por porcentaje de avance menor al 50%
- THEN el sistema renderiza únicamente los estudiantes asignados que cumplan con dichos criterios de búsqueda
