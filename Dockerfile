FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

FROM python:3.13-slim-trixie
LABEL org.opencontainers.image.source=https://github.com/mkorthof/solis-to-web
LABEL org.opencontainers.image.description="Solis (MQTT) to Web Client"
RUN groupadd --system --gid 1000 solis && \
    useradd --system --gid 1000 --uid 1000 --create-home solis
COPY --from=builder --chown=solis:solis /app /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
USER solis
WORKDIR /app
ENTRYPOINT ["python3", "main.py"]
