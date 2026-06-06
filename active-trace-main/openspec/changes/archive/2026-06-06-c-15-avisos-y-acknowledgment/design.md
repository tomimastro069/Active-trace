# Design: Avisos y Acknowledgment (C-15)

## Technical Approach
Implementación de los modelos de base de datos `Aviso` y `AcknowledgmentAviso` heredando de `TimestampedTenant` para brindar soporte multi-tenant y soft delete nativo. La estrategia central será desarrollar un repositorio (`AvisoRepository`) que extienda `BaseRepository` y construya dinámicamente las condiciones en SQLAlchemy para calcular la visibilidad (cruzando el alcance con las asignaciones vigentes del usuario autenticado). El router publicará los endpoints protegidos bajo estricto control de RBAC y consumirá la lógica delegada al servicio de dominio.

## Architecture Decisions

### Decision: Filtrado Dinámico de Avisos vs. Tablas Desnormalizadas
**Choice**: Filtrado dinámico en caliente (Query SQLAlchemy que cruza las reglas de alcance con las asignaciones del usuario).
**Alternatives considered**: Desnormalizar destinatarios explícitos guardando filas en una tabla puente `aviso_destinatario` al momento de publicarse el aviso.
**Rationale**: El filtrado dinámico es consistente con la base de datos normalizada, no genera inconsistencias al cambiar el equipo docente o los padrones de forma tardía, y previene un crecimiento exponencial de datos ante envíos de alcance masivo (ej: globales o de cohorte entera).

### Decision: Contadores de Acknowledgment en Tiempo Real
**Choice**: Derivar vistas y acuses a partir de conteos (`COUNT()`) de la tabla transaccional `AcknowledgmentAviso`.
**Alternatives considered**: Contadores incrementables (`vistas`, `confirmaciones`) guardados dentro del modelo `Aviso`.
**Rationale**: Siguiendo explícitamente la regla de negocio `RN-18/19/20` que estipula no denormalizar para mantener integridad transaccional estricta. El cálculo en tiempo real previene condiciones de carrera o pérdida de coherencia.

## Data Flow
     [Cliente] ── (GET /activos) ──→ [AvisosRouter] ──→ [AvisoService]
                                                               │
                                                       [AvisoRepository]
                                                               │ (JOIN Dinámico + Filtro Vigencia)
                                         [DB: Avisos + Asignaciones + Acks]

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `backend/app/models/aviso.py` | Create | Define SQLAlchemy models (`Aviso` y `AcknowledgmentAviso`) |
| `backend/app/models/__init__.py` | Modify | Expone los nuevos modelos |
| `backend/app/schemas/aviso.py` | Create | Pydantic DTOs para Request/Response |
| `backend/app/repositories/aviso.py` | Create | Lógica de queries (scope tenant, visibilidad cruzada, contadores) |
| `backend/app/services/aviso.py` | Create | Reglas de validación, orquestación de DB y manejo de permisos |
| `backend/app/api/v1/routers/avisos.py` | Create | Endpoints `/api/v1/avisos` (ABM, listar activos, acuse) |
| `backend/app/main.py` | Modify | Inclusión del router `avisos_router` |
| `backend/alembic/versions/` | Create | Script de migración inicial de la estructura |

## Interfaces / Contracts

```python
class AlcanceEnum(str, Enum):
    GLOBAL = "Global"
    POR_MATERIA = "PorMateria"
    POR_COHORTE = "PorCohorte"
    POR_ROL = "PorRol"

class AvisoBase(BaseModel):
    alcance: AlcanceEnum
    materia_id: Optional[UUID] = None
    cohorte_id: Optional[UUID] = None
    rol_destino: Optional[str] = None
    severidad: str
    titulo: str
    cuerpo: str
    inicio_en: datetime
    fin_en: datetime
    orden: int = 0
    activo: bool = True
    requiere_ack: bool = False

class AvisoResponse(AvisoBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Filtros de alcance | Test en base SQLite efímera comprobando la consulta SQL base, validando que el alumno solo obtenga avisos globales, de su materia o de su cohorte, en base a asignaciones ficticias. |
| Unit | Ventana de vigencia | Confirmar que si `now()` está fuera del rango `inicio_en` y `fin_en`, el aviso no se incluye. |
| Integration | Seguridad / ABM | Validar endpoint POST con JWT válido; confirmar HTTP 403 si el usuario carece del permiso `avisos:publicar`. |
| Integration | Ack Lifecycle | Completar el acuse mediante POST `/ack` y verificar que el aviso desaparezca de la ruta `/activos` y que el contador global sume +1. |

## Migration / Rollout
Generación estándar mediante `alembic revision --autogenerate`. Al tratarse de entidades huérfanas o puramente aditivas, no existen conflictos destructivos, pero la migración depende de las tablas `usuarios`, `materias` y `cohortes` (foreign keys preexistentes).

## Open Questions
- Ninguna.
