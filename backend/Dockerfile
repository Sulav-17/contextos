FROM ghcr.io/astral-sh/uv:0.11.25 AS uv

FROM python:3.13-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=uv /uv /usr/local/bin/uv

RUN addgroup --system app && adduser --system --ingroup app app \
    && mkdir -p /var/lib/contextos/private-documents \
    && chown -R app:app /var/lib/contextos

COPY pyproject.toml uv.lock alembic.ini ./
COPY alembic ./alembic

RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src

RUN uv sync --frozen --no-dev

USER app

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "contextos.main:app", "--host", "0.0.0.0", "--port", "8000"]
