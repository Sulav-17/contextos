# ADR 0005: Authentication and Session Boundary

- Status: Accepted for Milestone 4 security review

## Context

ContextOS needs invite-only authentication, cookie-based frontend sessions, and deterministic backend
authorization before any private document features exist.

## Decision

Use Supabase Auth for email/password identity, invitation links, recovery links, and SSR session cookies. Use
FastAPI as the only ContextOS domain authorization boundary.

The browser may use the Supabase publishable key for auth sessions only. ContextOS domain data is fetched through
server-side FastAPI calls with a bearer token. FastAPI verifies JWTs independently and maps the verified subject
to an application user row.

## Consequences

- Public signup remains disabled.
- Backend tests can validate forged and invalid tokens without a live Supabase project.
- Application roles cannot be self-promoted through JWT metadata.
- Manual Supabase redirect and email-template configuration is required.
