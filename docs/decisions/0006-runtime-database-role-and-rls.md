# ADR 0006: Runtime Database Role and RLS

- Status: Accepted for Milestone 4 security review

## Context

Milestone 4 introduces tenant-owned rows. Runtime API requests must not connect as a table owner or superuser.

## Decision

Use separate migration/admin and runtime PostgreSQL credentials. Migrations create tables, policies, and grants.
Runtime requests use a restricted login role and set transaction-local context:

```text
request.jwt.claim.sub
app.actor_role
```

Application authorization remains primary. RLS is defense in depth and defaults to deny when context is absent.

## Consequences

- Existing local PostgreSQL volumes need a one-time role creation step or a new initialized volume.
- Tests must exercise direct runtime-role access.
- Repositories must continue explicit owner filtering rather than relying only on RLS.
