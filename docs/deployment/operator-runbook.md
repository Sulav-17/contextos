# Beta Operator Runbook

Status: concise operational runbook for beta incidents.

## Deployment Failure

Check build logs first, then runtime startup logs. Confirm production environment variables match `environment-reference.md`. If startup validation fails, fix the missing or unsafe variable and redeploy the same image.

## Backend Unavailable

Check `/health`, then `/ready`. If `/health` fails, inspect API process logs and container status. If `/ready` fails, inspect database and Redis checks in the readiness payload, then verify provider dashboards and network allowlists.

## Provider Outage

If the AI provider is unavailable, document chat and memory/chat generation may fail while authentication, uploads, and document listing should remain available. Confirm provider status, check API logs for provider failure events, and retry after service recovery.

## Upload Or Ingestion Failure

Check the document detail failure code. Confirm the file is a readable PDF within page and size limits. Inspect worker logs for `document ingestion failed` or `document embedding provider failed`. Retry from the document action after resolving the underlying issue.

## Worker Down

Confirm the worker process is running with `python -m contextos.worker`, the queue name matches `CONTEXTOS_DOCUMENT_QUEUE_NAME`, and Redis is reachable. Restart the worker after fixing configuration. Failed or queued jobs should be retried through the existing retry path.

## Database Migration Issue

Stop API and worker writes before retrying a failed migration. Preserve migration logs. Verify `CONTEXTOS_MIGRATION_DATABASE_URL` points to the production migration role and not the runtime app role. Do not edit applied migrations; create a corrective migration if needed.

## Auth Callback Issue

Confirm Supabase redirect URLs exactly match the production site:

- `https://<site-domain>/auth/confirm`
- `https://<site-domain>/update-password`

Check frontend `NEXT_PUBLIC_SITE_URL`, backend `CONTEXTOS_FRONTEND_URL`, and Supabase Auth email templates.

## Private Storage Issue

Confirm `CONTEXTOS_DOCUMENT_STORAGE_BACKEND=supabase`, bucket name, Supabase URL, and server secret key. The bucket must be private. Downloads should go through authenticated API routes and return `Cache-Control: private, no-store`.

## Missing Document After Upload

Check document status. If queued or processing, inspect worker health and Redis. If failed, inspect the failure code and retry after resolving the cause. If deleted, confirm deletion was user-approved and verify chunks no longer appear in retrieval.

## Missing Document After Delete

Confirm the document row is soft-deleted, chunks were removed, and the storage object was deleted. If storage deletion failed, retry the storage delete with the recorded storage key from server-side operational access only; never expose the key to the user.

## Rollback Approach

Rollback API, worker, and frontend by redeploying the previous known-good image/build. Keep the database at the current migration unless there is a reviewed rollback migration. During rollback, pause the worker if ingestion is causing repeated failures.
