FROM vault:1.13.3 AS vault-cli

FROM python:3.12-slim-bullseye AS builder

ARG POETRY_VERSION=1.8.3

RUN useradd -d /app -m -s /bin/bash app_user
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER app_user

ENV POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PATH="/app/.venv/bin:/app/.local/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION}

COPY --chown=app_user:app_user pyproject.toml poetry.lock* ./

RUN poetry install --no-interaction --no-root

COPY --chown=app_user:app_user ./vault_actions /app/vault_actions

# build slim image

FROM python:3.12-slim-bullseye

RUN useradd -d /app -m -s /bin/bash app_user
WORKDIR /app

COPY --from=vault-cli /bin/vault /bin/vault

USER app_user
ENV PATH="/app/.venv/bin:/app/.local/bin:$PATH"

COPY --from=builder --chown=app_user:app_user /app/vault_actions /app/vault_actions
COPY --from=builder --chown=app_user:app_user /app/.venv /app/.venv
COPY --chown=app_user:app_user ./docker/docker-entrypoint.sh /app/docker-entrypoint.sh

RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
