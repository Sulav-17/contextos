# ContextOS

ContextOS is a private-by-design, multi-user personal knowledge assistant for PDF libraries, citation-backed chat, persistent conversations, and user-controlled long-term memory.

## Current Product Shape

The repository now contains an implemented beta-oriented application:

- Next.js frontend with TypeScript, Tailwind CSS, Quiet Orbit visual direction, PWA shell support, and Supabase session handling.
- FastAPI backend with typed domain boundaries, Supabase JWT verification, PostgreSQL tenant isolation, private document storage paths, Redis/RQ background ingestion, and privacy-safe logging.
- Citation-backed document chat for private PDFs.
- Persistent conversations with archived and active states.
- User-controlled memory surfaces for suggested, approved, disabled, and rejected memories.
- A public interactive demo at `/demo`.

The public demo is a guided portfolio experience. It uses fictional documents, fictional memories, and deterministic prepared responses. It does not access real user accounts, production documents, storage objects, conversations, memories, authenticated APIs, or live AI services.

## Version 1 Scope

Version 1 focuses on:

- public email/password signup with email confirmation;
- private PDF upload and storage;
- citation-backed document chat;
- persistent conversations and summaries;
- user-approved long-term memory controls;
- user and administrator control over access, deletion, and review.

## Non-Goals

Version 1 does not include public open signup, OCR, non-PDF file formats, autonomous external actions, team workspaces, billing, mobile apps, graph databases, LangGraph, Kubernetes, or complex 3D interfaces.

## Approved Stack

- Frontend: Next.js, TypeScript, Tailwind CSS.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic.
- Data: PostgreSQL, pgvector, PostgreSQL full-text search.
- Identity and storage: Supabase Auth and private object storage.
- Background jobs: Redis and RQ.
- AI: internal provider interfaces with deterministic test providers, local adapters, and an optional hosted provider.
- Deployment direction: Vercel for the frontend, Render for the API and worker, and Supabase for managed data services.

These are the approved beta architecture directions. Deployment must still be verified in the target environment before making production-readiness claims.

## Documentation Map

- [Product charter](docs/product/product-charter.md)
- [Version 1 scope](docs/product/version-1-scope.md)
- [System overview](docs/architecture/system-overview.md)
- [Threat model](docs/security/threat-model.md)
- [Security invariants](docs/security/security-invariants.md)
- [Beta technology stack ADR](docs/decisions/0001-beta-technology-stack.md)
- [Tenant isolation strategy ADR](docs/decisions/0002-tenant-isolation-strategy.md)
- [Milestone roadmap](docs/milestones/roadmap.md)

## Local Commands

Backend commands run from `backend/`; frontend commands run from `frontend/`.

```powershell
uv sync --locked --all-groups
uv run pytest
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```
