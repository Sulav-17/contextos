# ContextOS

ContextOS is a private, invite-only personal knowledge assistant for PDF libraries, citation-backed chat, persistent conversations, and user-approved long-term memory.

## Problem

People who manage private document collections need a system that can find evidence, answer questions with citations, and preserve useful context without giving up ownership, privacy, or control.

## Version 1

Version 1 is a focused beta with:

- secure invite-only entry;
- private PDF upload and storage;
- citation-backed document chat;
- persistent conversations and summaries;
- user-approved long-term memory;
- user and administrator control over access, deletion, and review.

## Non-Goals

Version 1 does not include public signup, OCR, non-PDF file formats, autonomous external actions, team workspaces, billing, mobile apps, graph databases, LangGraph, Kubernetes, or complex 3D interfaces.

## Proposed Stack

- Frontend: Next.js, TypeScript, Tailwind CSS.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic.
- Data: PostgreSQL, pgvector, PostgreSQL full-text search.
- Identity and storage: Supabase Auth and private object storage.
- Background jobs: Redis and RQ.
- AI: internal provider interfaces with deterministic test providers, local adapters, and an optional hosted provider.
- Deployment direction: Vercel for the frontend, Render for the API and worker, and Supabase for managed data services.

These are the approved beta architecture directions, not claims that the services are already configured.

## Current Status

Milestone 1 establishes the documentation foundation only. Application implementation has not started yet.

## Documentation Map

- [Product charter](docs/product/product-charter.md)
- [Version 1 scope](docs/product/version-1-scope.md)
- [System overview](docs/architecture/system-overview.md)
- [Threat model](docs/security/threat-model.md)
- [Security invariants](docs/security/security-invariants.md)
- [Beta technology stack ADR](docs/decisions/0001-beta-technology-stack.md)
- [Tenant isolation strategy ADR](docs/decisions/0002-tenant-isolation-strategy.md)
- [Milestone roadmap](docs/milestones/roadmap.md)
- [Milestone 1 spec](docs/milestones/milestone-01.md)

## Warning

Application implementation has not started. This repository currently contains documentation only.

## Notes

No setup or run commands are defined yet.
