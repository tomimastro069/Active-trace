# Design: C-09 padron-ingesta-moodle

## Technical Approach

Siguiendo Clean Architecture, introduciremos las capas de persistencia y lógica para manejar los Padrones y Entradas. 
El servicio `PadronService` se encargará de validar la coherencia y versionado, consumiendo `PadronRepository` para desactivar iteraciones pasadas de un padrón y crear nuevas dentro de una misma transacción, aislando a nivel base de datos los posibles fallos parciales de inserción de múltiples alumnos. La integración con LMS Moodle se ubicará en el paquete `integrations/moodle_ws.py` que retornará una lista estandarizada (Pydantic `EntradaPadronCreate`) la cual será procesada por `PadronService` de manera indistinta de la carga manual.

## Architecture Decisions

### Decision: Aislamiento del Cliente Moodle (LMS)

**Choice**: Encapsular Moodle WS en `integrations/moodle_ws.py`.
**Alternatives considered**: Hacer llamadas HTTP directo en `PadronService`.
**Rationale**: Moodle WS podría fallar (502). `moodle_ws.py` utilizará `httpx` (o librería de requests) envuelto con resiliencia (`tenacity`) para proveer de reintentos, separando las fallas de red del orquestador de lógica del negocio, previniendo acoplamiento.

### Decision: Control de versión concurrente de Padrones

**Choice**: Utilizar flag booleano `activa` en modelo `VersionPadron` en DB con índice para búsqueda rápida, actualizando la previa de la misma `materia×cohorte` a `activa=False` en una transacción SQL explícita.
**Alternatives considered**: Hacer validaciones en memoria.
**Rationale**: Garantiza que no se asigne temporalmente 2 padrones activos a la vez, y permite rollbacks rápidos en caso de fallo de carga masiva de las Entradas.

## Data Flow

```text
       Ingesta (CSV/XLSX)            Moodle WS Sync
              │                             │
              ▼                             ▼
       [PadronRouter]          [MoodleWSIntegration]
              │                             │
              └──► [PadronService] ◄────────┘
                         │
        (Validación de Schema y Versionado)
                         │
                 [PadronRepository]
                         │
                 (Tx: Desactivar anterior)
                 (Tx: Crear VersionPadron)
                 (Tx: Bulk Insert EntradaPadron)
                         │
                        ▼
                   [PostgreSQL]
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/models/padron.py` | Create | Entidades `VersionPadron` y `EntradaPadron` usando el mixin de `Tenant` y `Timestamp`. |
| `backend/app/schemas/padron.py` | Create | Modelos Pydantic para lectura y validación, ej. `PadronImportRequest`. |
| `backend/app/repositories/padron_repository.py` | Create | Acceso a DB, implementa `desactivar_versiones_activas` y `bulk_insert`. |
| `backend/app/services/padron_service.py` | Create | Lógica de negocio para manejar la importación. Valida PII y orquesta DB. |
| `backend/app/routers/padron.py` | Create | Endpoints `/api/padron/import` (File upload) y `/api/padron/sync` (Trigger Moodle). |
| `backend/app/integrations/moodle_ws.py` | Create | Módulo HTTP para dialogar con Moodle. |
| `backend/alembic/versions/xxx_padron.py` | Create | Script para generar las tablas `version_padron` y `entrada_padron`. |
| `backend/app/main.py` | Modify | Registrar router de `padron`. |

## Interfaces / Contracts

```python
class EntradaPadronCreate(BaseModel):
    usuario_id: Optional[UUID4]
    nombre: str
    apellidos: str
    email: str # Cifrado a nivel DB, texto claro a nivel Request interno
    comision: Optional[str]
    regional: Optional[str]

class PadronImportContext(BaseModel):
    materia_id: UUID4
    cohorte_id: UUID4
    entradas: List[EntradaPadronCreate]
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Lógica de Versionado | Mockear repository; probar que activar nueva desactiva la vieja y lanza eventos de auditoría correctos. |
| Integration | Moodle WS Fallback | Mockear request HTTP a Moodle, responder 502, y verificar retry. |
| E2E | API Importación Manual | Subir un archivo `.csv` dummy mediante TestClient, validar `200 OK` y verificar presencia en base de datos. |

## Migration / Rollout

No migration required. Tablas `version_padron` y `entrada_padron` son nuevas entidades y se desplegarán de forma transparente mediante Alembic.

## Open Questions

- [ ] ¿Cómo mapeamos la coincidencia del alumno en la DB si el email del LMS no coincide con el guardado localmente (ej: personal vs institucional)? (Podría resolverse agregando lookup por legajo o deferir creación de cuenta).
