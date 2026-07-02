# Beta Release Notes And Checklist

Status: Milestone 11 beta release artifact.

## Release Notes

ContextOS beta is prepared for a real multi-user deployment with production config validation, private Supabase object storage support, structured API and worker logs, readiness checks for database and Redis, explicit ingestion queue configuration, and practical operator runbooks.

## Changelog Summary

- Added production startup validation for secrets, HTTPS URLs, non-local infrastructure, real AI providers, and private storage.
- Added Supabase private storage support for uploaded PDFs.
- Preserved local file storage for local and test environments.
- Added API and worker startup logs, readiness failure logs, ingestion enqueue/failure/completion logs, and request ID propagation.
- Added deployment, environment, beta verification, and operator runbook documentation.
- Added smoke-check script for deployment verification.

## Known Limitations

- PDF extraction supports text-based PDFs only; OCR is out of scope.
- The beta user cap remains intentionally small.
- AI provider outage handling is limited to controlled errors and retry after recovery.
- Production screenshots and manual verification must be completed in the deployed environment.
- Advanced monitoring, billing, enterprise SSO, analytics, and native apps are out of scope.

## Product Demo Checklist

1. Load the public landing page.
2. Sign in from an invited account.
3. Open the dashboard and confirm workspace state.
4. Upload a small text-based PDF.
5. Wait for the document to become ready.
6. Ask a cited question scoped to that document.
7. Ask a general question.
8. Approve a memory candidate.
9. Ask a memory-supported question.
10. Archive, restore, and delete a conversation.
11. Delete the document and confirm it no longer appears in retrieval.
12. Log out, log in as another user, and confirm no cross-user data appears.

## Beta Verification Checklist

1. Public landing loads over HTTPS.
2. Signup/login works for invited users only.
3. Dashboard loads after authentication.
4. PDF upload succeeds.
5. Document reaches ready state.
6. Cited document question works.
7. Memory approval works.
8. Memory-supported question works.
9. General question works.
10. Conversation archive/restore/delete works.
11. Document delete stops retrieval.
12. Second-user login shows no data leakage.
13. PWA install still works.
14. `/health` and `/ready` return expected statuses.
15. API and worker logs are visible and do not contain secrets or private content.

## Screenshot Inventory

Capture final beta screenshots after deployment:

- Public landing page.
- Login page.
- Dashboard/workspace state.
- Document library with a ready document.
- Cited document answer.
- Memory review/approval.
- Conversation controls.
- Mobile/PWA shell.
