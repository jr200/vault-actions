FROM vault:1.13.3 AS vault-cli

FROM python:3.12-slim-bullseye

ARG POETRY_VERSION=1.8.3

RUN useradd -d /app -m -s /bin/bash app_user

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=vault-cli /bin/vault /bin/vault

USER app_user

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=${POETRY_VERSION} python3 - 

# Add Poetry to PATH
ENV POETRY_VIRTUALENVS_CREATE="true"
ENV POETRY_VIRTUALENVS_IN_PROJECT="true"
ENV PATH="/app/.venv/bin:/app/.local/bin:${PATH}"

# # Copy the pyproject.toml (and optionally poetry.lock) file into the container
COPY ./docker/docker-entrypoint.sh pyproject.toml poetry.lock* ./

# Install dependencies using Poetry
RUN poetry install --only main --no-root --no-interaction --no-directory

# # Copy the package files into the container
COPY ./vault_actions /app/vault_actions

ENTRYPOINT ["/app/docker-entrypoint.sh"]