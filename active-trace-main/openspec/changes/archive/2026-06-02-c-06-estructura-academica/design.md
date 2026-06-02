# Diseño Técnico: C-06 Estructura Académica

## Arquitectura de Datos (SQLAlchemy)

Los 3 modelos heredarán de `Base` y `TimestampedTenant`.

### Enums
Para evitar el lock-in del motor (ej. Postgres `CREATE TYPE`), usaremos el patrón de la base de código actual `ChoiceType` o bien columnas `String` con validación Pydantic y Constraints check de SQLAlchemy si se considera oportuno.
Se definirá la constante o clase enum de Python:
```python
class EstadoActivoInactivo(str, enum.Enum):
    ACTIVA = "Activa"
    INACTIVA = "Inactiva"
```
Y en los modelos:
```python
estado = Column(String, default=EstadoActivoInactivo.ACTIVA, nullable=False)
```

### Tabla `carreras`
```python
class Carrera(Base, TimestampedTenant):
    __tablename__ = 'carreras'

    codigo = Column(String, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    estado = Column(String, default="Activa", nullable=False)

    __table_args__ = (
        UniqueConstraint('tenant_id', 'codigo', name='uix_carrera_tenant_codigo'),
    )
```

### Tabla `materias`
```python
class Materia(Base, TimestampedTenant):
    __tablename__ = 'materias'

    codigo = Column(String, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    estado = Column(String, default="Activa", nullable=False)

    __table_args__ = (
        UniqueConstraint('tenant_id', 'codigo', name='uix_materia_tenant_codigo'),
    )
```

### Tabla `cohortes`
```python
class Cohorte(Base, TimestampedTenant):
    __tablename__ = 'cohortes'

    carrera_id = Column(UUID(as_uuid=True), ForeignKey('carreras.id', ondelete='CASCADE'), nullable=False)
    nombre = Column(String, nullable=False)
    anio = Column(Integer, nullable=False)
    vig_desde = Column(Date, nullable=False)
    vig_hasta = Column(Date, nullable=True)
    estado = Column(String, default="Activa", nullable=False)

    __table_args__ = (
        UniqueConstraint('tenant_id', 'carrera_id', 'nombre', name='uix_cohorte_tenant_carrera_nombre'),
    )
```

## Capa Repository & Service

Se aplicará el patrón `Repository` estándar del proyecto, proveyendo métodos `get_by_id`, `get_all` filtrados por tenant, y `create`.

Para `CohorteService`:
```python
async def create(self, cohorte_create: CohorteCreateDTO):
    # Verificar estado de la carrera
    carrera = await self.carrera_repo.get_by_id(cohorte_create.carrera_id)
    if not carrera or carrera.estado == "Inactiva":
        raise ValueError("No se puede crear cohorte en carrera Inactiva o inexistente.")
    # Log de auditoría
    # ...
```

## API Routers
- `/api/v1/admin/carreras`
- `/api/v1/admin/cohortes`
- `/api/v1/admin/materias`

Dependencias: `current_user = Depends(require_permission("estructura:gestionar"))`

## Generación de Migraciones
Una vez implementados los modelos:
`alembic revision --autogenerate -m "005 estructura academica"`
Y verificar los constraints en el upgrade.
