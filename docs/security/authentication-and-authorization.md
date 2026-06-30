# Authentication and Authorization

Status: Milestone 4 implementation pending security review.

## Boundary

Supabase Auth owns email/password sessions and invite/recovery links. ContextOS owns application authorization.

- The frontend uses Supabase SSR cookies for user experience redirects and session refresh.
- The frontend never queries ContextOS domain tables through Supabase.
- All ContextOS domain reads and writes go through FastAPI.
- FastAPI independently verifies Supabase access tokens against JWKS.
- Application role and account status come from PostgreSQL, not JWT metadata.

## FastAPI Authentication

Protected API routes require `Authorization: Bearer <access-token>`.

The verifier checks:

- allowed asymmetric algorithm;
- JWKS `kid`;
- signature;
- exact issuer;
- audience;
- expiration and issued-at with bounded clock skew;
- UUID subject;
- authenticated Supabase role;
- optional UUID session ID.

Authentication errors return stable safe JSON and never include tokens, claims dumps, keys, or provider bodies.

## Application Authorization

The authenticated subject is loaded as `users.id`. A valid Supabase token without a matching application user is denied.

Statuses:

- `invited`: activated on first accepted invite login;
- `active`: may use protected routes;
- `disabled`: denied even with a valid token.

Roles:

- `user`: can read and update only own preferences;
- `admin`: can access invitation administration.

## Invitation Boundary

Admins create invitations through FastAPI. The Supabase server secret is backend-only and must never use a
`NEXT_PUBLIC_` prefix. Invitation tokens and email links are not stored by ContextOS.

## Bootstrap

The first administrator is created by CLI only:

```powershell
uv run python -m contextos.cli bootstrap-admin --auth-user-id <uuid> --email <email>
```

There is no public bootstrap endpoint and no test authentication bypass.
