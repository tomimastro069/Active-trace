# syntax=docker/dockerfile:1.4

# ---------- Builder Stage ----------
FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY requirements.txt .

# En lugar de instalar, descargamos y compilamos las dependencias en una carpeta
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ---------- Runtime Stage ----------
FROM python:3.13-slim AS runtime

# Instalar dependencias de ejecución del sistema si las necesitas (ej. libpq para PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID appgroup && \
    useradd -u $UID -g $GID -s /bin/bash -m appuser

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 2. Copiar el código de la aplicación (puedes hacerlo directo de tu contexto local)
COPY ./app ./app
COPY ./migrations ./migrations
COPY ./core ./core
COPY ./infra ./infra
COPY ./monitoring ./monitoring
COPY ./tenancy ./tenancy
COPY ./alembic.ini ./alembic.ini
COPY ./pyproject.toml ./pyproject.toml
COPY ./scripts ./scripts

# Asegurar ejecución sin root
USER appuser

ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]