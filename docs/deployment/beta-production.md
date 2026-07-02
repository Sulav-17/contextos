# Beta Production Deployment

Status: operator-run deployment guide for Milestone 11.

## Architecture

The beta production shape is:

- Next.js frontend on Vercel or an equivalent HTTPS web host.
- FastAPI API on Render or an equivalent container host.
- RQ worker on the same backend image as the API, started with `python -m contextos.worker`.
- PostgreSQL with pgvector through Supabase or another managed PostgreSQL provider.
- Redis through a managed Redis service.
- Supabase Auth for verified user identity and invitation handling.
- Supabase private Storage for uploaded PDFs.

All public traffic must terminate through HTTPS. The API, worker, database, Redis, and storage credentials are server-side only. Frontend configuration may contain only publishable Supabase values and public site URLs.

## Deployment Steps

1. Create production Supabase Auth, PostgreSQL, and private Storage resources.
2. Create a private storage bucket, for example `contextos-private-documents`.
3. Configure Supabase Auth redirect URLs:
   - `https://<site-domain>/auth/confirm`
   - `https://<site-domain>/update-password`
4. Provision managed Redis.
5. Set backend API environment variables from `environment-reference.md`.
6. Run `uv run alembic upgrade head` against the production migration database URL.
7. Deploy the API container with `CONTEXTOS_ENVIRONMENT=production`.
8. Deploy the worker container from the same image and command `python -m contextos.worker`.
9. Deploy the frontend with only frontend-safe environment variables.
10. Run `scripts/deployment-smoke.ps1` against the public site and API.
11. Complete the beta verification checklist in `beta-release.md`.

## Storage Rules

Production must use `CONTEXTOS_DOCUMENT_STORAGE_BACKEND=supabase`. Uploaded files are stored under tenant-scoped object paths and remain private. Downloads are proxied through authenticated API routes and keep `Cache-Control: private, no-store`.

## Logging

Use JSON logs in production. API and worker logs include request IDs where available and operational fields such as environment, queue name, storage backend, dependency readiness failures, and ingestion failure codes. Logs must not include tokens, connection strings, signed URLs, raw document text, prompts, memories, or provider keys.

## Rollback

Prefer a blue/green or previous-image rollback for API/frontend/worker changes. Do not roll back database migrations without an explicit reverse plan. If a migration caused the incident, stop the API and worker first, preserve logs, and follow the database migration runbook.
