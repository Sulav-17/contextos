# Milestone 2 — Backend and Local Platform Foundation

**Status:** Implementation complete — awaiting mentor and user review
**Project:** ContextOS — Personal Knowledge Assistant  
**Execution mode:** Fast-tracked merged milestone

## Completion Notes

- Implemented the FastAPI backend foundation, validated settings, request correlation, structured logging, async PostgreSQL/Redis resources, Alembic migration support, Docker packaging, Compose services, backend CI workflow, focused tests, and milestone documentation updates required by this specification.
- Actual files changed:
  - `AGENTS.md`, `.env.example`, `.gitignore`, `compose.yaml`
  - `.github/workflows/backend-ci.yml`
  - `backend/.dockerignore`, `backend/.python-version`, `backend/Dockerfile`, `backend/pyproject.toml`, `backend/uv.lock`, `backend/alembic.ini`
  - `backend/alembic/env.py`, `backend/alembic/script.py.mako`, `backend/alembic/versions/0001_enable_vector_extension.py`
  - `backend/src/contextos/__init__.py`, `backend/src/contextos/main.py`
  - `backend/src/contextos/api/__init__.py`, `backend/src/contextos/api/router.py`, `backend/src/contextos/api/routes/__init__.py`, `backend/src/contextos/api/routes/system.py`
  - `backend/src/contextos/core/__init__.py`, `backend/src/contextos/core/config.py`, `backend/src/contextos/core/logging.py`, `backend/src/contextos/core/request_id.py`
  - `backend/src/contextos/infrastructure/__init__.py`, `backend/src/contextos/infrastructure/database.py`, `backend/src/contextos/infrastructure/redis_client.py`
  - `backend/tests/__init__.py`, `backend/tests/conftest.py`, `backend/tests/api/__init__.py`, `backend/tests/api/test_system_routes.py`, `backend/tests/integration/__init__.py`, `backend/tests/integration/test_infrastructure.py`, `backend/tests/integration/test_migrations.py`, `backend/tests/unit/__init__.py`, `backend/tests/unit/test_config.py`, `backend/tests/unit/test_logging.py`, `backend/tests/unit/test_request_id.py`
  - `docs/decisions/0003-backend-local-platform.md`, `docs/milestones/roadmap.md`, `docs/milestones/milestone-02.md`
- Validation performed:
  - `uv lock --check`
  - `uv sync --locked --all-groups`
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run mypy src tests`
  - `uv run pytest tests/unit tests/api`
  - `docker compose config`
  - `docker compose up -d postgres redis`
  - `docker compose ps`
  - `uv run alembic upgrade head`
  - `uv run pytest tests/integration`
  - `uv run pytest --cov=contextos --cov-report=term-missing`
  - `docker compose up --build -d`
  - `docker compose ps -a`
  - endpoint checks for `/health`, `/ready`, and `X-Request-ID`
  - `docker exec contextos-api-1 id`
  - `git diff --check`
  - `git status --short`
- Deviations and unresolved issues:
  - Added a secondary published PostgreSQL host port `15432` and pointed the example host database URL there because this workstation already had a separate host PostgreSQL process bound to IPv4 `5432`; the required `5432` publish remains in Compose.
  - No remaining code or test failures were left unresolved at the end of implementation.

## Goal

Create a production-oriented backend foundation and reproducible local platform for ContextOS.

At the end of this milestone, the repository must contain:

- a typed FastAPI application;
- validated environment settings;
- privacy-safe structured logging;
- request correlation IDs;
- asynchronous PostgreSQL and Redis clients;
- Alembic migrations;
- the pgvector extension;
- liveness and readiness endpoints;
- a Docker image;
- a Docker Compose development stack;
- focused unit, API, and integration tests;
- backend linting, formatting, type-checking, and test commands;
- a GitHub Actions backend CI workflow.

This milestone stops before authentication, users, tenant-owned domain records, document storage, ingestion, retrieval, chat, or memory.

## Why This Milestone Is Merged

This milestone combines the original backend foundation and local infrastructure setup because the pieces are tightly coupled:

- settings determine database and Redis connections;
- readiness requires working infrastructure clients;
- migrations require the database;
- integration tests require reproducible services;
- CI must run the same checks;
- Docker must run the same application and lockfile.

Splitting these into several tiny milestones would create extra review overhead without creating a meaningful security boundary.

Authentication and tenant isolation remain separate because they require their own threat review and adversarial authorization tests.

## Recommended Codex Settings

- **Model:** GPT-5.4
- **Reasoning:** Medium
- **Fast mode:** Off
- **Subagents:** Off
- **Web access:** Off

## Current Repository State

The repository is documentation-only after approved Milestone 1.

Codex must inspect only:

- `AGENTS.md`;
- this milestone specification;
- the existing root configuration and documentation files directly affected by this milestone.

Do not recursively read all documentation.

## Approved Technical Decisions

Use:

- **Python:** 3.13, pinned by `.python-version`;
- **Project manager:** `uv`;
- **API:** FastAPI;
- **Validation/settings:** Pydantic and `pydantic-settings`;
- **Database:** PostgreSQL 17;
- **Vector extension:** pgvector;
- **ORM:** SQLAlchemy 2 stable API;
- **Database driver:** `asyncpg`;
- **Migrations:** Alembic;
- **Redis client:** `redis` with its asyncio API;
- **Application server:** Uvicorn;
- **Testing:** pytest, pytest-asyncio, HTTPX;
- **Quality:** Ruff and mypy;
- **Containers:** Docker and Docker Compose;
- **CI:** GitHub Actions.

Use compatible stable dependency releases resolved by `uv` and commit `uv.lock`.

Do not use a SQLAlchemy 2.1 beta release. Use the current stable SQLAlchemy 2.0 line unless 2.1 has become a stable general release in the resolver; do not opt into prereleases.

## Pinned Infrastructure Images

Use these explicit image tags:

```text
pgvector/pgvector:0.8.3-pg17-trixie
redis:8.8.0-alpine
python:3.13-slim-trixie
ghcr.io/astral-sh/uv:0.11.25
```

Do not use `latest` tags.

## In Scope

1. Python backend package initialization.
2. Dependency and lockfile management with `uv`.
3. Application factory and lifespan management.
4. Validated settings.
5. Structured logging.
6. Safe request correlation IDs.
7. Async PostgreSQL infrastructure.
8. Async Redis infrastructure.
9. Alembic initialization.
10. Initial migration enabling pgvector.
11. `/health` and `/ready` endpoints.
12. Dockerfile and Compose stack.
13. Unit, API, and integration tests.
14. Ruff, mypy, and pytest configuration.
15. GitHub Actions backend CI.
16. Stable command documentation in `AGENTS.md`.
17. A concise ADR for the backend/local platform.
18. Updating the roadmap to the approved fast-tracked sequence.
19. Updating `.env.example` and `.gitignore` only as needed.

## Out of Scope

Do not implement:

- Supabase Auth;
- login, registration, invitations, sessions, or JWT verification;
- users or tenant-owned domain tables;
- Row-Level Security policies;
- object storage or signed URLs;
- workspaces or libraries;
- document upload or PDF validation;
- background RQ workers or job models;
- chunking or embeddings;
- retrieval or chat;
- memory;
- quotas;
- frontend code;
- CORS configuration for a deployed frontend;
- production deployment;
- cloud provisioning;
- Sentry or external observability services;
- rate limiting;
- a task scheduler;
- README expansion;
- benchmark or performance claims.

Redis is connected and health-checked in this milestone, but RQ worker behavior begins in the ingestion milestone.

## Required File Boundaries

Codex may create or update only the following paths.

```text
AGENTS.md
.env.example
.gitignore
compose.yaml

.github/workflows/backend-ci.yml

backend/.dockerignore
backend/.python-version
backend/Dockerfile
backend/pyproject.toml
backend/uv.lock
backend/alembic.ini

backend/alembic/env.py
backend/alembic/script.py.mako
backend/alembic/versions/0001_enable_vector_extension.py

backend/src/contextos/__init__.py
backend/src/contextos/main.py

backend/src/contextos/api/__init__.py
backend/src/contextos/api/router.py
backend/src/contextos/api/routes/__init__.py
backend/src/contextos/api/routes/system.py

backend/src/contextos/core/__init__.py
backend/src/contextos/core/config.py
backend/src/contextos/core/logging.py
backend/src/contextos/core/request_id.py

backend/src/contextos/infrastructure/__init__.py
backend/src/contextos/infrastructure/database.py
backend/src/contextos/infrastructure/redis_client.py

backend/tests/__init__.py
backend/tests/conftest.py
backend/tests/api/__init__.py
backend/tests/api/test_system_routes.py
backend/tests/integration/__init__.py
backend/tests/integration/test_infrastructure.py
backend/tests/integration/test_migrations.py
backend/tests/unit/__init__.py
backend/tests/unit/test_config.py
backend/tests/unit/test_logging.py
backend/tests/unit/test_request_id.py

docs/decisions/0003-backend-local-platform.md
docs/milestones/milestone-02.md
docs/milestones/roadmap.md
```

Do not modify `README.md` in this milestone.

Do not create additional files unless absolutely required by a tool-generated Alembic structure. If an extra file is required, state the reason in the completion report.

## Backend Package Requirements

Use a `src` layout:

```text
backend/
├── src/
│   └── contextos/
├── tests/
├── alembic/
├── pyproject.toml
└── uv.lock
```

The installed package name may be `contextos`, while the distribution/project name should clearly identify the backend, such as `contextos-backend`.

The application must be importable as:

```python
from contextos.main import app, create_app
```

## `pyproject.toml` Requirements

Configure:

- project metadata;
- `requires-python = ">=3.13,<3.14"`;
- runtime dependencies;
- a development dependency group;
- pytest;
- pytest-asyncio;
- Ruff;
- mypy;
- package discovery for the `src` layout.

Runtime dependencies should include only what this milestone needs:

- FastAPI;
- Uvicorn;
- Pydantic settings;
- SQLAlchemy async support;
- asyncpg;
- Alembic;
- Redis;
- any small required dependency used by those integrations.

Development dependencies should include:

- pytest;
- pytest-asyncio;
- pytest-cov;
- HTTPX;
- Ruff;
- mypy.

Do not add application libraries for future features.

Use strict but practical mypy settings for the new code. Do not silence typing errors globally.

## Settings Requirements

Implement a Pydantic settings model with an explicit `CONTEXTOS_` environment-variable prefix.

Required settings:

- application name;
- application version;
- environment: `local`, `test`, `staging`, or `production`;
- log level;
- log format: `json` or `console`;
- database URL;
- Redis URL;
- readiness timeout in seconds.

Requirements:

- safe local defaults are allowed only for non-secret metadata;
- database and Redis URLs must be supplied through environment configuration;
- production must not silently fall back to local credentials;
- settings validation errors must be clear;
- settings must be testable without modifying process-wide environment permanently;
- cached settings, if used, must have an explicit test reset mechanism;
- settings representations and logs must not expose credentials.

Use connection URLs in these forms:

```text
postgresql+asyncpg://...
redis://...
```

## `.env.example` Requirements

Update the existing root `.env.example`.

Include placeholder development values for:

- PostgreSQL database name;
- PostgreSQL user;
- PostgreSQL password;
- application database URL for host execution;
- Redis URL for host execution;
- application environment;
- log level;
- log format;
- readiness timeout.

Use obvious placeholders such as:

```text
replace-with-local-only-password
```

Do not include realistic secrets, cloud URLs, tokens, Supabase keys, or hosted-provider credentials.

The developer may copy this file to `.env`, but `.env` must remain ignored.

## FastAPI Application Requirements

Implement an application factory:

```python
def create_app(...) -> FastAPI:
    ...
```

Requirements:

- application metadata comes from settings;
- lifespan creates and closes database and Redis resources;
- no network connection is required merely to import the application module;
- infrastructure failures do not leak credentials;
- app state or explicit dependencies provide access to infrastructure;
- avoid hidden mutable global clients;
- no deprecated startup/shutdown event decorators;
- no authentication placeholders or fake users.

Expose:

```python
app = create_app()
```

for Uvicorn and container startup.

## Logging Requirements

Use the Python standard logging library unless a compelling need for another dependency is demonstrated.

Support:

- structured JSON logs;
- readable console logs for local development;
- timestamp;
- level;
- logger name;
- message;
- request ID when available;
- safe exception metadata.

Requirements:

- no raw environment dumps;
- no database URLs;
- no Redis URLs;
- no passwords;
- no request or response bodies;
- no arbitrary untrusted fields promoted into log keys;
- initialization must be idempotent and avoid duplicate handlers;
- tests must prove sensitive connection strings are not present in normal configuration/log output.

## Request Correlation Requirements

Implement middleware using a context variable.

Behavior:

1. Read optional `X-Request-ID`.
2. Accept it only when it:
   - is within a conservative maximum length;
   - contains only a conservative safe character set.
3. Generate a UUID-based request ID when missing or invalid.
4. Return the final value in the `X-Request-ID` response header.
5. Make it available to application logs during the request.
6. Clear/reset context after the request.
7. Do not treat the request ID as authentication or authorization data.

Test:

- generated ID;
- accepted safe ID;
- rejected unsafe/oversized ID;
- response header;
- no cross-request context leakage.

## Database Infrastructure Requirements

Implement an async database resource that owns:

- SQLAlchemy async engine;
- async session factory;
- health-check method;
- disposal/close method.

Requirements:

- use SQLAlchemy 2-style APIs;
- use `pool_pre_ping=True`;
- do not create sessions at import time;
- one `AsyncSession` must not be shared across concurrent tasks;
- health check executes a minimal `SELECT 1`;
- health check respects the readiness timeout;
- errors are translated to safe internal results;
- no domain models are created in this milestone.

Provide a dependency or resource method for obtaining one session per request/task, but it does not need to be consumed by a domain route yet.

## Redis Infrastructure Requirements

Implement an async Redis resource that owns:

- Redis client creation;
- `PING` health check;
- close method.

Requirements:

- no client creation at import time;
- decode responses where practical;
- health check respects timeout;
- errors are translated to safe internal results;
- do not configure RQ or queues yet.

## Health Endpoints

### `GET /health`

Purpose: liveness.

Requirements:

- does not call PostgreSQL or Redis;
- returns HTTP 200 when the process can serve requests;
- returns a small stable response such as:

```json
{
  "status": "ok",
  "service": "contextos-api",
  "version": "..."
}
```

### `GET /ready`

Purpose: dependency readiness.

Requirements:

- checks PostgreSQL and Redis;
- checks may run concurrently;
- each check has a timeout;
- returns HTTP 200 only when all required dependencies are healthy;
- returns HTTP 503 when either dependency is unavailable;
- uses a stable response shape;
- names failing dependencies without exposing exception text, hosts, ports, usernames, or credentials;
- includes the request ID response header through middleware.

Example healthy shape:

```json
{
  "status": "ready",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

Example unavailable shape:

```json
{
  "status": "not_ready",
  "checks": {
    "database": "unavailable",
    "redis": "ok"
  }
}
```

## Alembic Requirements

Initialize Alembic under `backend/alembic`.

Requirements:

- migration environment reads the configured database URL;
- use the async-compatible Alembic pattern;
- do not hardcode credentials in `alembic.ini`;
- importing Alembic configuration must not print secrets;
- initial migration ID/name must be deterministic and readable;
- the initial migration enables the PostgreSQL `vector` extension;
- downgrade removes the extension only when safe for this empty foundation database;
- migration has no user or domain tables;
- migration can upgrade from an empty database and downgrade back to base;
- migration tests verify upgrade, extension presence, downgrade, and re-upgrade.

Do not enable unrelated extensions.

## Dockerfile Requirements

Create `backend/Dockerfile`.

Requirements:

- use a pinned Python 3.13 slim base;
- copy the pinned `uv` binary from the pinned official uv image;
- use `uv.lock`;
- install only runtime dependencies in the final runtime image;
- use build layers that avoid reinstalling all dependencies for every source change;
- do not bake `.env` or secrets into the image;
- run as a non-root user;
- expose port 8000;
- use an exec-form command;
- start Uvicorn without `--reload`;
- include a suitable health check only if it does not require extra operating-system packages;
- keep the image simple; no premature multi-platform or distroless complexity.

## Docker Compose Requirements

Create root `compose.yaml` with:

- `postgres`;
- `redis`;
- `migrate`;
- `api`.

### PostgreSQL

- use the pinned pgvector PostgreSQL 17 image;
- use a named data volume;
- read local credentials from environment variables;
- publish port 5432 for local development;
- include `pg_isready` health check;
- do not hardcode a production password.

### Redis

- use the pinned Redis image;
- use a named data volume if persistence is enabled;
- publish port 6379 for local development;
- include `redis-cli ping` health check;
- use a bounded local persistence configuration if enabled;
- authentication is deferred for local-only development, and this limitation must be documented in the ADR.

### Migration service

- build from the backend Dockerfile;
- wait for PostgreSQL health;
- run `alembic upgrade head`;
- exit successfully;
- not restart endlessly.

### API service

- build from the backend Dockerfile;
- wait for:
  - successful migration completion;
  - healthy PostgreSQL;
  - healthy Redis;
- use container-internal database and Redis hostnames;
- publish port 8000;
- include a health check against `/health`;
- not mount the source tree in the production-like Compose service;
- use no embedded secrets.

Use modern Compose syntax. Do not add a top-level obsolete `version` key.

Use dependency conditions such as `service_healthy` and `service_completed_successfully` where appropriate.

## Test Requirements

### Unit tests

Test:

- valid settings;
- missing required connection settings;
- invalid environment/log format/timeout;
- settings do not reveal connection secrets;
- logging initialization is idempotent;
- JSON log structure;
- request ID validation and generation;
- request context cleanup.

### API tests

Test:

- `/health` response and status;
- `/health` does not require infrastructure;
- `/ready` healthy response;
- `/ready` database failure;
- `/ready` Redis failure;
- `/ready` both failures;
- response does not leak exception or connection details;
- request ID response behavior.

Use explicit test dependencies or injected resources. Do not make unit/API tests require live Docker services.

### Integration tests

Against real PostgreSQL and Redis:

- database `SELECT 1`;
- Redis `PING`;
- application readiness with both services;
- initial migration upgrade;
- `vector` extension exists;
- downgrade to base;
- re-upgrade to head.

Tests must be deterministic and must not depend on execution order.

Do not use SQLite as a substitute for PostgreSQL integration tests.

## Quality Commands

Configure and make these commands pass from `backend/`:

```powershell
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

Also support formatting locally:

```powershell
uv run ruff format .
```

Configure pytest markers for integration tests if markers are used. Unknown markers must be errors.

Do not set a coverage percentage gate yet, but generate a useful coverage report during final validation.

## `AGENTS.md` Command Update

Replace the placeholder command section with stable commands for:

- dependency synchronization;
- running the API;
- formatting;
- linting;
- type-checking;
- focused tests;
- full backend tests;
- migrations;
- Docker Compose startup;
- Docker Compose status;
- Docker Compose logs;
- Docker Compose shutdown without deleting volumes;
- full local smoke verification.

Do not add commands that were not actually validated.

## GitHub Actions Requirements

Create `.github/workflows/backend-ci.yml`.

Use current official action generations and pin third-party actions to immutable commit SHAs where practical.

The workflow must:

1. trigger on pull requests and pushes affecting backend/platform files;
2. check out the repository;
3. install pinned `uv`;
4. install Python 3.13 based on `.python-version`;
5. sync from the lockfile;
6. start PostgreSQL with pgvector and Redis service containers;
7. run Alembic upgrade;
8. run Ruff formatting check;
9. run Ruff lint;
10. run mypy;
11. run the full pytest suite;
12. validate `docker compose config`;
13. build the backend Docker image.

Use test-only environment values. Do not add repository secrets.

The CI database must support `CREATE EXTENSION vector`.

Do not deploy from this workflow.

## ADR Requirements

Create:

```text
docs/decisions/0003-backend-local-platform.md
```

Use the project ADR format:

- Status;
- Context;
- Decision;
- Alternatives considered;
- Consequences;
- Security implications;
- Future migration path.

Document:

- Python 3.13;
- `uv` and lockfile;
- async FastAPI/SQLAlchemy;
- PostgreSQL 17 with pgvector;
- Redis;
- Alembic;
- Docker Compose;
- standard-library structured logging;
- why plain PostgreSQL/Redis Compose is used before introducing local Supabase Auth/Storage;
- that Supabase integration remains planned for the authentication/storage milestones;
- local Redis authentication limitation;
- why authentication is intentionally excluded.

## Fast-Tracked Roadmap Update

Update `docs/milestones/roadmap.md` to preserve traceability to the original plan while presenting this approved fast-tracked execution sequence:

1. Product and architecture foundation — approved.
2. Backend and local platform foundation.
3. Frontend experience design.
4. Authentication, invitations, and tenant isolation.
5. Workspaces, private storage, quotas, and background PDF ingestion.
6. Chunking, embeddings, hybrid retrieval, citation-backed chat, and persistent conversations.
7. Memory approval, conflict handling, retrieval, and combined context.
8. User data controls, administrator controls, export, and verified deletion.
9. Evaluation harness and security hardening.
10. Deployment and observability.
11. Private beta testing and remediation.
12. Documentation, case study, and release packaging.

Requirements:

- show which original milestones each merged milestone absorbs;
- retain security review gates;
- do not imply later milestones are implemented;
- do not expand the README.

## Milestone Document Update

Store this specification at:

```text
docs/milestones/milestone-02.md
```

After implementation:

- set status to `Implementation complete — awaiting mentor and user review`;
- add concise completion notes;
- list actual files changed;
- list validation performed;
- list deviations and unresolved issues;
- do not mark it approved.

## Required Validation Sequence

Codex must use focused checks during implementation, then perform final validation.

### 1. Static validation

From `backend/`:

```powershell
uv lock --check
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
```

### 2. Focused non-integration tests

```powershell
uv run pytest tests/unit tests/api
```

### 3. Compose configuration

From repository root with safe test environment variables or a local ignored `.env`:

```powershell
docker compose config
```

### 4. Infrastructure and migrations

Start only PostgreSQL and Redis first:

```powershell
docker compose up -d postgres redis
docker compose ps
```

Then from `backend/`:

```powershell
uv run alembic upgrade head
uv run pytest tests/integration
```

### 5. Full backend suite with coverage output

```powershell
uv run pytest --cov=contextos --cov-report=term-missing
```

### 6. Container stack smoke test

From repository root:

```powershell
docker compose up --build -d
docker compose ps
```

Verify:

- migration container exited successfully;
- PostgreSQL is healthy;
- Redis is healthy;
- API is healthy;
- `GET /health` returns 200;
- `GET /ready` returns 200;
- both include no sensitive connection details;
- `X-Request-ID` is present.

On Windows PowerShell, manual endpoint checks may use:

```powershell
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/ready
```

Inspect headers with:

```powershell
Invoke-WebRequest http://localhost:8000/health
```

### 7. Image and repository checks

- confirm API container runs as non-root;
- confirm no `.env` is tracked;
- run `git diff --check`;
- inspect `git status --short`;
- scan the diff for secrets and connection strings;
- confirm no frontend, auth, user, document, retrieval, or memory implementation was added;
- stop containers without deleting named volumes:

```powershell
docker compose down
```

Do not run `docker compose down -v` unless explicitly requested.

## Manual Verification for the User

After Codex completes and the mentor reviews the report, the user will manually verify:

1. `uv sync --locked --all-groups`.
2. Docker Desktop is running.
3. `docker compose up --build -d`.
4. `docker compose ps`.
5. `/health`.
6. `/ready`.
7. request ID header.
8. `docker compose logs --no-log-prefix api`.
9. `uv run pytest`.
10. `docker compose down`.

Codex must not claim these user checks were completed by the user.

## Completion Report

Return a concise report containing:

- files created and updated;
- architecture implemented;
- tests added;
- exact validation commands and results;
- test count if genuinely reported by pytest;
- Docker service status;
- migration status;
- CI workflow summary;
- deviations;
- unresolved issues;
- any ignored local files created for validation;
- suggested commit message.

Do not commit, push, deploy, or begin Milestone 3.

## Suggested Commit Message

```text
feat: establish ContextOS backend and local platform
```

## Acceptance Criteria

Milestone 2 is ready for mentor and user review only when:

- Python 3.13 and `uv` are configured;
- `uv.lock` is committed and current;
- FastAPI imports without connecting to infrastructure;
- application resources are managed by lifespan;
- structured logging and request IDs work;
- `/health` works without dependencies;
- `/ready` accurately reports PostgreSQL and Redis;
- asynchronous clients are cleanly closed;
- Alembic upgrades an empty PostgreSQL database;
- the `vector` extension is enabled;
- migration downgrade and re-upgrade pass;
- unit, API, and integration tests pass;
- Ruff formatting and lint pass;
- mypy passes;
- Docker Compose brings up a healthy stack;
- the API container runs as non-root;
- CI validates the backend and builds the image;
- the roadmap reflects the approved fast-tracked sequence;
- no authentication or later product feature was introduced;
- no README expansion occurred;
- no secrets were committed;
- Codex stops without beginning the next milestone.
