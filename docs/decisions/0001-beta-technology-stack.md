# ADR 0001: Beta Technology Stack

## Status

Accepted

## Context

ContextOS needs a practical stack for a small invite-only beta that can still serve as a strong portfolio project. The repository is intentionally greenfield, and no runtime dependencies or provider versions have been chosen yet.

## Decision

Use the approved beta direction:

- Next.js, TypeScript, and Tailwind CSS for the frontend;
- Python, FastAPI, Pydantic, SQLAlchemy, and Alembic for the backend;
- PostgreSQL, pgvector, and PostgreSQL full-text search for data and retrieval;
- Supabase Auth and private object storage for identity and storage;
- Redis and RQ for background work;
- internal AI provider interfaces with deterministic test providers, local adapters, and an optional hosted provider;
- Vercel for the frontend, Render for the API and worker, and Supabase for managed data services.

Dependency versions and final provider choices will be selected later.

## Alternatives Considered

- A single-language full-stack approach.
- A more complex orchestration framework for AI flows.
- Self-managed infrastructure for all services.
- Broader beta infrastructure before product-market fit signals exist.

## Consequences

- The stack stays familiar, practical, and easy to reason about for a three-user beta.
- The architecture demonstrates modern product and security practices without adding unnecessary operational burden.
- Future migration remains possible because the system is organized around clear service boundaries and provider interfaces.

## Security Implications

- The stack supports explicit application authorization, private storage, and deterministic ownership rules.
- Provider interfaces reduce coupling to any one AI vendor.
- PostgreSQL can enforce defense-in-depth controls alongside application checks.

## Future Migration Path

If beta needs change, providers can be swapped, infrastructure can be rehomed, and runtime dependencies can be finalized later without changing the documented ownership and authorization model.
