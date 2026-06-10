# Tasks: fix-02-enum-estadocomunicacion

## 1. Backend

- [x] 1.1 Auditar todos los enums de `app/models/*` contra los tipos creados por Alembic en la DB
      (solo `estadocomunicacion` diverge).
- [x] 1.2 Agregar `values_callable` al `SAEnum` de `Comunicacion.estado`.

## 2. Verificación

- [x] 2.1 Round-trip ORM (insert + query por estado) contra la DB provisionada por Alembic.
- [x] 2.2 El worker arranca y consulta la cola sin `InvalidTextRepresentationError` contra esa DB.
- [x] 2.3 Tests de comunicaciones (repository, service, worker) en verde.
