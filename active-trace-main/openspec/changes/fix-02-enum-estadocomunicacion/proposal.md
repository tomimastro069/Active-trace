# Fix 02 — Enum `estadocomunicacion`: el worker de C-12 crashea contra la DB de Alembic

## Why

La migración `bc500c50d1fd_c12_comunicacion` crea el tipo `estadocomunicacion` con los **valores**
del dominio (`Pendiente, Enviando, Enviado, Error, Cancelado` — RN-15), pero el modelo declara
`SAEnum(EstadoComunicacion, name="estadocomunicacion")` sin `values_callable`, por lo que
SQLAlchemy envía los **nombres** de los miembros (`PENDIENTE, ENVIANDO, ...`).

Resultado contra una base provisionada por Alembic (producción):

```
asyncpg.exceptions.InvalidTextRepresentationError:
  invalid input value for enum estadocomunicacion: "ENVIANDO"
```

El worker (`python -m app.workers.main`) crashea en su primer query y todo el módulo de
comunicaciones queda inoperable. Los tests no lo detectan porque el conftest provisiona el schema
con `Base.metadata.create_all` (que crea el enum a partir de los nombres), no con las migraciones.

Auditoría del resto de los enums (`alcanceenum`, `diasemanaenum`, `estado_reserva_enum`,
`estadoencuentroenum`, `estadoguardiaenum`, `estadotareaenum`, `evaluacion_tipo_enum`): todos
fueron creados en la DB con los nombres de los miembros, que coincide con lo que SQLAlchemy
envía por defecto. Solo `estadocomunicacion` está afectado.

## What Changes

- El modelo `Comunicacion.estado` declara `values_callable` para que SQLAlchemy envíe los
  valores del enum (los labels del dominio que ya viven en la DB). La DB no cambia: los valores
  de la migración son los canónicos.
- Sin migración nueva, sin cambios de API.

## Impact

- `backend/app/models/comunicacion.py`
- Worker y endpoints de comunicaciones funcionan contra la DB real.
- Tests de C-12 siguen en verde (create_all ahora también genera el enum con valores, igual que
  la migración — se elimina además esa divergencia silenciosa entre ambos esquemas).
