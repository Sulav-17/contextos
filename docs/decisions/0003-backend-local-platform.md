# ADR 0003: Backend and Local Platform Foundation

- Status: Accepted

## Context

ContextOS needs a reproducible backend foundation before authentication, storage, ingestion, retrieval, or memory features can be implemented safely. The repository started as documentation-only, so the project needed an agreed local execution model, dependency workflow, migration path, and baseline health verification that can be reused in CI and later milestones.

The foundation must keep infrastructure concerns isolated from future domain logic, avoid vendor lock-in for early application code, and preserve the project security invariants around ownership, authorization, secret handling, and testability.

## Decision

We will use:

- Python 3.13, pinned with `.python-version`;
- `uv` with a committed `uv.lock` for deterministic dependency resolution and local/CI synchronization;
- FastAPI for the HTTP API surface and lifespan-managed application resources;
- async SQLAlchemy 2.0 with `asyncpg` for PostgreSQL access;
- PostgreSQL 17 with the `pgvector` extension enabled through Alembic;
- Redis with the asyncio client for readiness-checked infrastructure connectivity;
- Alembic for schema and extension migrations;
- Docker Compose for the local platform with PostgreSQL, Redis, migrations, and the API service;
- Python standard-library logging with structured JSON output and request correlation IDs;
- a plain PostgreSQL and Redis local stack before introducing local Supabase Auth or Storage emulation.

Authentication is intentionally excluded from this milestone. Supabase Auth and private object storage remain planned for the dedicated authentication and storage milestones, where the threat model and authorization tests can be reviewed directly instead of being hidden inside infrastructure setup work.

## Alternatives Considered

- Poetry or pip-tools instead of `uv`: rejected because `uv` provides faster lock/sync workflows with a single lockfile and matches the approved tooling direction.
- Sync database access: rejected because later ingestion, retrieval, and API work will benefit from consistent async infrastructure from the start.
- SQLite for local development: rejected because this milestone must validate PostgreSQL-specific behavior, including `CREATE EXTENSION vector`.
- Local Supabase emulation immediately: rejected because Milestone 2 explicitly excludes authentication and storage behavior, and adding those services now would increase operational scope before the authorization model is implemented.
- Third-party structured logging packages: rejected because the standard library is sufficient for the required JSON and console logging without extra operational dependencies.

## Consequences

- Developers get a deterministic backend workflow with pinned Python and dependency resolution.
- The API can be imported without opening infrastructure connections, while lifespan management still owns startup and shutdown behavior.
- Readiness is tied to actual PostgreSQL and Redis availability, which improves CI and local smoke verification.
- The Docker Compose stack remains intentionally small and production-oriented enough for local validation.
- Redis local authentication is not enabled in this milestone. This is acceptable only for local-only development and must not be treated as a production security posture.

## Security Implications

- Secrets stay in environment configuration and are excluded from normal logs and committed files.
- Request IDs are validated, bounded, and treated strictly as correlation data, never as identity or authorization input.
- Migration and readiness responses do not expose infrastructure credentials or internal exception text.
- Keeping authentication out of this milestone avoids accidental weakening of identity and authorization boundaries during platform setup.
- Using plain PostgreSQL and Redis in Compose keeps local infrastructure minimal while deferring Supabase-specific identity and storage security decisions to the milestones where those controls are implemented and reviewed.

## Future Migration Path

- Add Supabase Auth integration in the authentication and invitation milestone.
- Add private object storage workflows in the storage and document milestones.
- Introduce tenant-owned domain tables and authorization tests through Alembic migrations in later milestones.
- Extend Redis usage to RQ-backed worker infrastructure in the ingestion milestone.
- Expand observability and deployment controls in the deployment and observability milestone.
