FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.6.16 /uv /uvx /bin/

WORKDIR  /app

COPY pyproject.toml uv.lock /app/

RUN uv sync --all-groups --no-cache --compile-bytecode --frozen

COPY . /app

ENV PATH="/app/.venv/bin:$PATH"