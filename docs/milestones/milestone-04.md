# Milestone 4 — Quiet Orbit Frontend, Authentication, Invitations, and Tenant Isolation

**Status:** Ready for implementation  
**Project:** ContextOS — Personal Knowledge Assistant  
**Execution mode:** Fast-tracked implementation with mandatory security review

## Goal

Implement the approved Quiet Orbit frontend foundation and the first complete security boundary for ContextOS.

At the end of this milestone:

- the Next.js frontend exists and implements the approved responsive Quiet Orbit application shell;
- Supabase Auth supports invite acceptance, password login, logout, password reset, and cookie-based SSR sessions;
- public signup is unavailable;
- FastAPI independently verifies Supabase access tokens;
- authenticated users are mapped to application users;
- an administrator can invite the remaining beta users;
- the three-user beta cap is enforced transactionally;
- protected FastAPI routes use deterministic application authorization;
- PostgreSQL RLS provides defense in depth;
- users can read and change only their own profile preferences;
- administrators alone can access invitation administration;
- automated tests prove cross-user isolation and reject invalid tokens;
- the frontend remains a shell with honest empty states rather than fake product data.

This milestone stops before document storage, PDF ingestion, retrieval, chat, and long-term memory implementation.

## Why These Areas Are Merged

The frontend shell and authentication flow are tightly coupled:

- protected layouts need real session handling;
- the entry experience needs invitation acceptance and login;
- the frontend needs a real `/me` boundary;
- administrator invitation screens need backend authorization;
- tenant-isolation tests require actual application users;
- user greeting and motion settings provide a small real tenant-owned resource for proving isolation.

The milestone retains a dedicated security review gate. No document or memory feature may begin until this milestone passes adversarial authentication and authorization tests.

## Recommended Codex Settings

- **Model:** GPT-5.5
- **Reasoning:** Medium
- **Fast mode:** Off
- **Subagents:** Off
- **Web access:** Off

Use GPT-5.5 because this milestone combines session handling, JWT verification, administrator invitations, database roles, RLS, tenant context, a new frontend, and cross-user security testing.

## Required Reading

Read only:

1. `AGENTS.md`
2. `docs/milestones/milestone-04.md`
3. `docs/frontend/frontend-implementation-spec.md`
4. `docs/frontend/design-system.md`
5. `docs/frontend/layouts-and-wireframes.md`
6. `docs/frontend/accessibility-strategy.md`
7. `docs/frontend/performance-strategy.md`
8. `docs/security/security-invariants.md`
9. `docs/decisions/0002-tenant-isolation-strategy.md`
10. `docs/decisions/0004-frontend-experience-direction.md`
11. directly affected Milestone 2 backend and platform files

Do not recursively read the repository or all documentation.

## Approved Product Decisions

- Visual concept: **Quiet Orbit**
- Returning-user greeting: minimized by default
- Full greeting and direct-workspace entry remain selectable
- Mobile primary navigation excludes Projects; Projects appears in More
- Dark presentation is implemented first
- Semantic tokens must remain theme-ready
- Full light mode is deferred
- CSS-first motion
- No WebGL, heavy animation runtime, or large visual assets
- No direct browser access to ContextOS domain tables
- FastAPI remains the deterministic authorization boundary
- PostgreSQL RLS is defense in depth

## In Scope

### Frontend

1. Next.js App Router application.
2. Strict TypeScript.
3. Tailwind-based semantic design system.
4. Approved Quiet Orbit shell and assistant identity.
5. Responsive desktop, tablet, and mobile navigation.
6. Public login, invitation acceptance, password reset, and auth-error pages.
7. Protected home and placeholder feature routes.
8. Settings for greeting and motion preferences.
9. Administrator invitation view.
10. Accessible loading, empty, error, offline, and unauthorized states.
11. SSR Supabase clients using cookies.
12. Next.js `proxy.ts` for session refresh and UX redirects.
13. Server-only FastAPI client.
14. Frontend unit/component tests.
15. Public-route Playwright smoke tests.
16. Frontend lint, type-check, test, and build validation.

### Backend

1. Supabase JWT verification using asymmetric signing keys and JWKS.
2. Authenticated principal dependency.
3. Current application-user resolution.
4. Role and account-status authorization.
5. Users, invitations, preferences, and minimal audit-event models.
6. Transaction-scoped tenant context.
7. RLS policies and a non-owner runtime database role.
8. `/api/v1/me` and `/api/v1/me/preferences`.
9. Administrator invitation endpoints.
10. Three-user beta cap.
11. Supabase administrator invitation provider abstraction.
12. Explicit first-administrator bootstrap command.
13. Authentication, authorization, RLS, invitation, and concurrency tests.
14. Migration upgrade/downgrade/re-upgrade coverage.
15. CI and Compose updates required by the new frontend and database roles.

## Out of Scope

Do not implement:

- public signup;
- social login;
- passkeys or MFA;
- account deletion;
- account disabling UI;
- document or workspace domain models;
- object storage;
- uploads;
- PDF processing;
- RQ jobs;
- embeddings;
- retrieval;
- conversations;
- memory;
- usage quotas other than the three-user beta cap;
- billing;
- production deployment;
- full admin analytics;
- direct frontend access to PostgreSQL or Supabase Data API;
- fake recent conversations, documents, memories, or usage metrics;
- full light mode;
- README expansion.

## Frontend Technology

Use compatible stable releases resolved by the package manager.

Required:

- Next.js 16 stable App Router
- React 19 stable
- TypeScript strict mode
- Tailwind CSS 4
- `@supabase/supabase-js`
- `@supabase/ssr`
- Zod
- required Radix UI primitives only
- one restrained icon package
- Vitest
- Testing Library
- Playwright
- ESLint using the current Next.js flat-config direction
- pnpm with a pinned `packageManager` field

Do not add TanStack Query yet. The current shell can use Server Components, Server Actions, and narrow client components. Add it later when document and conversation data justify client-side server-state caching.

Do not add React Hook Form unless ordinary form handling becomes unreasonably complex.

Do not add a motion library. Use CSS transitions and lightweight SVG only.

## Frontend Structure

Use a clear structure similar to:

```text
frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   ├── forgot-password/
│   │   ├── update-password/
│   │   └── invite/accept/
│   ├── (workspace)/
│   │   ├── home/
│   │   ├── conversations/
│   │   ├── libraries/
│   │   ├── projects/
│   │   ├── memories/
│   │   ├── uploads/
│   │   ├── settings/
│   │   └── admin/invitations/
│   ├── auth/confirm/
│   ├── auth/error/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── assistant/
│   ├── auth/
│   ├── navigation/
│   ├── shell/
│   ├── status/
│   └── ui/
├── features/
│   ├── invitations/
│   ├── preferences/
│   └── profile/
├── lib/
│   ├── api/
│   ├── auth/
│   ├── env/
│   └── supabase/
├── tests/
├── public/
├── proxy.ts
├── package.json
├── pnpm-lock.yaml
└── ...
```

Codex may make small justified naming adjustments while preserving the boundaries.

## Quiet Orbit Requirements

Implement the approved design, not a generic dashboard.

### Visual direction

- deep navy or near-black base;
- restrained blue/violet atmosphere;
- cyan intelligence accent;
- subtle warm human accent;
- off-white primary text;
- layered surfaces with restrained transparency;
- soft borders;
- sparse decorative connection lines;
- no excessive glassmorphism.

### Assistant identity

Create a lightweight ambient node/orbit identity using CSS and accessible SVG where appropriate.

Support visible and textual states:

- idle;
- checking session;
- ready;
- saving preference;
- sending invitation;
- success;
- error;
- backend unavailable.

The feature-specific retrieving-document and memory states may be represented in the component API but do not need fake runtime demonstrations.

Every state must have text. Animation is supplemental.

### Greeting

- first authenticated entry may show the short approved welcome;
- returning users see a minimized greeting by default;
- settings support:
  - full greeting;
  - minimized greeting;
  - direct workspace entry;
- no cinematic delay;
- user can immediately continue;
- reduced-motion users receive static transitions.

### Responsive navigation

Desktop:

- left navigation;
- main content;
- reserved future context-inspector region without fake source content.

Tablet:

- collapsible navigation;
- reduced atmosphere.

Mobile:

- primary navigation for Home, Conversations, Libraries, and Memories;
- Projects, Uploads, Settings, and Admin under More;
- no horizontal overflow;
- touch targets at least 44 by 44 CSS pixels;
- safe-area support.

### Honest placeholder pages

Protected feature routes may show polished empty states explaining that the capability will arrive in a later milestone.

Do not fabricate:

- uploaded documents;
- saved memories;
- conversations;
- citations;
- usage totals;
- processing jobs.

## Accessibility Requirements

Target WCAG 2.2 AA.

Required:

- semantic landmarks;
- skip link;
- one logical H1 per page;
- full keyboard operation;
- visible focus;
- correct dialog/drawer focus trapping and restoration;
- accessible form labels and errors;
- status messages using appropriate live regions;
- reduced-motion support;
- no information by color alone;
- assistant states exposed as text;
- sufficient contrast;
- meaningful page titles;
- touch targets;
- no focus loss after server actions;
- password-error messages that do not expose account existence unnecessarily.

Run automated accessibility checks where practical, but do not claim complete WCAG conformance from automated tooling alone.

## Performance Targets

Treat Milestone 3 budgets as acceptance targets, not guaranteed measurements.

At minimum:

- unauthenticated initial JavaScript target: under 170 KB gzip;
- authenticated shell target: under 260 KB gzip;
- LCP target: under 2.2 seconds desktop and 2.8 seconds mobile under the agreed test profile;
- INP target: under 200 ms;
- CLS target: under 0.05;
- CSS/SVG assistant identity without large media;
- no autoplay video;
- no large background imagery;
- no WebGL;
- dynamically load secondary mobile drawers or admin features where useful.

Record measured build output when available. Do not invent browser performance measurements.

## Supabase Frontend Authentication

Use cookie-based SSR clients through `@supabase/ssr`.

Create separate browser and server client factories.

Use Next.js 16 `proxy.ts` to:

- refresh authentication tokens;
- copy refreshed cookies to the response;
- perform route-level UX redirects;
- avoid relying on proxy redirects as the security boundary.

Rules:

- use the Supabase publishable key in frontend-safe configuration;
- never expose a Supabase secret key to the browser;
- do not use deprecated auth-helper packages;
- do not trust the user object from an unverified local session alone;
- use verified claims or a server-confirmed user for protected server rendering;
- obtain the access token only when required to call FastAPI;
- never log tokens or session cookies.

### Public routes

- `/login`
- `/forgot-password`
- `/update-password`
- `/invite/accept`
- `/auth/confirm`
- `/auth/error`

### Protected routes

All workspace routes require a valid Supabase session for UX.

FastAPI still verifies the bearer token independently.

### Login

- email and password;
- generic invalid-credentials response;
- redirect only to validated internal paths;
- preserve no open redirect parameter;
- clear pending/error state;
- accessible form.

### Logout

- server action;
- Supabase sign-out;
- redirect to login;
- no sensitive data retained in rendered client state.

### Invitation acceptance

Support a secure email-link flow through an auth-confirmation route.

Requirements:

- token hash and auth type are validated;
- next destination is allow-listed;
- successful confirmation leads to password setup;
- password setup requires a valid authenticated invite session;
- failed, expired, or reused links show an actionable error;
- no invite token is logged or persisted by ContextOS;
- acceptance activates the matching application user.

Document required Supabase Site URL, redirect allow-list, and invite-email template configuration.

### Password reset

- request form uses a generic response regardless of account existence;
- reset callback validates the auth flow;
- password update requires a valid recovery session;
- successful update redirects safely;
- no password strength claims beyond provider configuration.

## Frontend-to-Backend Boundary

The browser must not query ContextOS domain tables through Supabase.

All ContextOS domain operations go through FastAPI.

Prefer:

- Server Components for initial protected reads;
- Server Actions for narrow mutations;
- a server-only API client that forwards the current Supabase access token to FastAPI;
- narrow client components only for interaction requiring browser state.

Do not create an unrestricted catch-all backend proxy.

The API client must:

- use a validated server-only API base URL;
- attach `Authorization: Bearer <access-token>`;
- attach or propagate `X-Request-ID`;
- set timeouts;
- parse stable error responses;
- never log access tokens;
- map 401, 403, 409, 422, 429, and 503 to safe UI states.

## Backend Authentication Settings

Add validated settings for:

- Supabase project URL;
- expected JWT issuer;
- expected audience, default `authenticated`;
- JWKS URL, derived safely when omitted;
- allowed asymmetric JWT algorithms;
- JWKS cache TTL;
- JWT clock-skew allowance;
- Supabase server secret key for administrator invitations;
- frontend public URL;
- beta maximum users, default 3;
- runtime database URL;
- migration database URL if not already separated.

Production must reject:

- missing auth configuration;
- wildcard issuers;
- HTTP hosted issuer URLs;
- HS256-only validation;
- missing server secret when invitations are enabled.

Sensitive values must be redacted from representations and logs.

## JWT Verification

Implement an authentication provider interface and a Supabase JWT verifier.

The verifier must:

1. Require a bearer token.
2. Parse only an allow-listed asymmetric algorithm such as ES256 or RS256.
3. Resolve the signing key by `kid` from the configured JWKS endpoint.
4. Cache JWKS with bounded TTL.
5. Refresh once when a valid `kid` is not found.
6. Validate signature.
7. Validate exact issuer.
8. Validate audience.
9. Validate expiration.
10. Validate issued-at when present.
11. Apply only a small configured clock skew.
12. Validate `sub` as UUID.
13. Require the authenticated role.
14. Validate session ID format when present.
15. Return a typed immutable principal.
16. Produce generic 401 responses.
17. Never include raw token, claims dump, or key material in logs.

Tests must cover:

- valid token;
- missing token;
- malformed token;
- wrong signature;
- unknown `kid`;
- disallowed algorithm;
- expired token;
- not-yet-valid token if applicable;
- wrong issuer;
- wrong audience;
- missing or invalid subject;
- wrong role;
- JWKS timeout;
- cache hit;
- key rotation refresh;
- no secret leakage.

Use deterministic test keys generated for tests. Never commit production keys.

## Application User Model

Create an application `users` table.

Recommended fields:

- `id` UUID primary key equal to verified Supabase subject;
- normalized unique email;
- display name nullable;
- role: `user` or `admin`;
- status: `invited`, `active`, or `disabled`;
- memory enabled boolean;
- created timestamp;
- updated timestamp;
- activated timestamp nullable;
- last authenticated timestamp nullable;
- disabled timestamp nullable.

Rules:

- application role comes from the database, not user-editable JWT metadata;
- a valid Supabase user without a matching application user is denied;
- invited users become active only through the accepted invitation flow;
- disabled users receive 403 even with a valid token;
- email changes are not silently trusted from JWT and must be reconciled explicitly later;
- no password or refresh token is stored.

## User Preferences

Create a small tenant-owned `user_preferences` table to prove isolation.

Fields:

- `user_id` UUID primary key and owner;
- greeting mode: `full`, `minimized`, or `direct`;
- motion mode: `system` or `reduced`;
- theme mode: `dark` or `system`;
- welcome completed boolean;
- created and updated timestamps.

Defaults:

- returning greeting minimized;
- motion follows system;
- dark presentation;
- welcome not completed.

Expose:

```text
GET   /api/v1/me
GET   /api/v1/me/preferences
PATCH /api/v1/me/preferences
```

Rules:

- no owner ID in request bodies;
- authenticated owner comes from the principal;
- repository queries still filter explicitly by actor ID;
- RLS also restricts the row;
- unknown fields rejected;
- PATCH accepts only documented preference fields;
- response contains no auth token or secret metadata.

## Invitations

Create an `invitations` table.

Recommended fields:

- ID;
- normalized unique email for active invitations;
- requested role;
- status: `pending`, `sent`, `accepted`, `failed`, `revoked`, or `expired`;
- invited-by administrator ID;
- provider user ID nullable;
- safe provider error code nullable;
- expiration;
- sent, accepted, created, and updated timestamps.

Never store:

- invitation tokens;
- email-link URLs;
- provider secret keys;
- raw provider error bodies.

### Administrator endpoints

Provide a narrow API such as:

```text
GET  /api/v1/admin/invitations
POST /api/v1/admin/invitations
```

Optional resend/revoke endpoints may be included only if the milestone implementation remains focused and tests are complete.

Rules:

- admin role required by application code;
- RLS reinforces admin-only access;
- ordinary users receive 403;
- emails are normalized;
- duplicate active invitations produce a stable conflict;
- existing application users cannot be re-invited;
- the configured beta maximum counts invited and active users;
- the cap is enforced transactionally with an advisory lock or equivalent database serialization;
- concurrent invite attempts cannot create a fourth beta account;
- invitation provider failures leave an auditable failed state;
- provider messages are translated to safe errors;
- administrator action is audited.

### Provider abstraction

Create a small interface for sending an email invitation.

Implement a Supabase adapter using server-only credentials.

The service must:

- never expose the secret key to frontend code;
- send the configured allow-listed redirect destination;
- use bounded timeout;
- translate provider errors;
- avoid retry storms;
- avoid logging email-link tokens or response bodies;
- support a deterministic fake provider for tests.

## First Administrator Bootstrap

Do not add an authentication backdoor.

Provide an explicit backend CLI command using the migration/admin database connection, for example:

```text
uv run python -m contextos.cli bootstrap-admin --auth-user-id <uuid> --email <email>
```

Requirements:

- requires explicit UUID and normalized email;
- creates or idempotently confirms the first administrator;
- refuses to replace an existing different administrator silently;
- records an audit event;
- prints no database URL or secret;
- cannot run through a public HTTP endpoint;
- documented manual sequence:
  1. create/invite the first auth user through the Supabase Dashboard;
  2. obtain the auth user UUID;
  3. run the CLI once;
  4. sign in through ContextOS;
  5. use ContextOS to invite the remaining beta users.

Tests must cover idempotency and conflicting bootstrap attempts.

## Database Runtime Role

Milestone 2 used the database foundation. This milestone must ensure runtime requests do not operate as the PostgreSQL superuser or table owner.

Introduce:

- migration/admin connection;
- non-superuser runtime login role;
- separate local passwords supplied through ignored environment variables;
- grants limited to required schema, tables, sequences, and functions.

For local Docker, an initialization script may create the runtime login role using environment variables.

Rules:

- no role password in migrations;
- no password committed;
- migrations run with the migration/admin connection;
- FastAPI runtime uses the non-owner runtime connection;
- CI uses separate test migration and runtime credentials;
- hosted migration notes explain how to create equivalent roles safely.

## Transaction-Scoped Tenant Context

Create a single safe mechanism used by authenticated repositories.

For each authenticated transaction:

1. begin transaction;
2. set the verified subject using transaction-local PostgreSQL configuration;
3. load the application user by explicit ID filter;
4. verify account status;
5. set the trusted application role using transaction-local configuration;
6. perform domain queries;
7. commit or roll back;
8. ensure context disappears after transaction.

Recommended settings:

```text
request.jwt.claim.sub
app.actor_role
```

Use parameterized `set_config(..., true)` or an equivalent safe mechanism.

Never use string interpolation.

Never set tenant context globally on a pooled connection.

Tests must prove:

- context is transaction local;
- context resets after commit and rollback;
- pooled connections do not leak the prior user;
- missing context causes default deny;
- an ordinary user cannot set an administrator role through request data.

## Row-Level Security

Create RLS policies for:

- users;
- user preferences;
- invitations;
- audit events where appropriate.

Requirements:

- enable RLS;
- force RLS where appropriate;
- runtime role does not own the tables;
- default deny when context is missing;
- users may read only their own application-user row;
- users may read and update only their own preferences;
- ordinary users cannot read invitations;
- administrators may use invitation operations only after application authorization and trusted role context;
- users cannot change their own role, status, or owner ID;
- `WITH CHECK` prevents owner changes;
- migration and bootstrap operations use the separate privileged connection;
- direct repository tests confirm policies.

Keep application-level explicit owner filters even when RLS exists.

## Audit Events

Create a minimal privacy-safe audit table or domain model for:

- administrator bootstrap;
- invitation attempted;
- invitation sent;
- invitation failed;
- invitation accepted;
- login-linked activation;
- authorization denied where appropriate.

Do not record:

- passwords;
- tokens;
- secret keys;
- full provider responses;
- unnecessary user content.

Audit metadata must use an allow-list of safe fields.

## Migrations

Create a new migration after Milestone 2.

It must:

- create required enums or constrained columns;
- create users, preferences, invitations, and audit structures;
- add indexes and uniqueness constraints;
- create RLS policies;
- grant the runtime role only required privileges;
- preserve the existing vector extension;
- support upgrade from Milestone 2;
- support downgrade back to Milestone 2 on an empty/test dataset;
- pass upgrade, downgrade, and re-upgrade tests.

Do not edit the applied Milestone 2 migration.

## Backend Error Contract

Use a stable safe error structure, for example:

```json
{
  "error": {
    "code": "authentication_required",
    "message": "Authentication is required.",
    "request_id": "..."
  }
}
```

Provide stable codes for:

- authentication required;
- invalid authentication;
- user not provisioned;
- account disabled;
- administrator required;
- invitation duplicate;
- beta capacity reached;
- provider unavailable;
- validation failed.

Do not expose exception text.

## Frontend Routes

Implement at least:

```text
/
 /login
 /forgot-password
 /update-password
 /invite/accept
 /auth/confirm
 /auth/error

 /home
 /conversations
 /libraries
 /projects
 /memories
 /uploads
 /settings
 /admin/invitations
```

Behavior:

- `/` routes authenticated users to `/home` and others to `/login`;
- protected routes redirect unauthenticated users to login for UX;
- non-admin users cannot render admin content;
- backend remains authoritative and returns 403 independently;
- placeholder pages clearly identify future functionality.

## Frontend Settings

The settings page must implement real preference reads and updates for:

- greeting mode;
- motion mode;
- theme mode within current supported options;
- welcome completion.

Requirements:

- server-side initial data;
- accessible controls;
- pending and success state;
- safe error state;
- backend unavailable state;
- no optimistic success before confirmed persistence;
- no owner ID supplied by frontend.

## Administrator Invitation UI

Implement a small admin-only interface:

- current beta capacity;
- invited email input;
- list of invitation states;
- send action;
- pending, success, conflict, capacity, and provider-failure states;
- no raw provider details;
- no user-management features outside scope.

Do not expose the Supabase secret key through Next.js.

## Environment Configuration

Update root and frontend examples without real credentials.

Frontend-safe:

```text
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
NEXT_PUBLIC_SITE_URL
```

Server-only frontend:

```text
CONTEXTOS_API_URL
```

Backend secret/configuration:

```text
CONTEXTOS_SUPABASE_URL
CONTEXTOS_SUPABASE_JWT_ISSUER
CONTEXTOS_SUPABASE_JWT_AUDIENCE
CONTEXTOS_SUPABASE_JWKS_URL
CONTEXTOS_SUPABASE_SECRET_KEY
CONTEXTOS_FRONTEND_URL
CONTEXTOS_BETA_MAX_USERS
CONTEXTOS_MIGRATION_DATABASE_URL
```

Local database roles:

```text
POSTGRES_MIGRATION_USER
POSTGRES_MIGRATION_PASSWORD
POSTGRES_APP_USER
POSTGRES_APP_PASSWORD
```

Exact names may be adjusted to match existing naming, but public and secret boundaries must remain obvious.

No secret may use a `NEXT_PUBLIC_` prefix.

## Supabase Setup Documentation

Create a concise manual setup document that includes:

1. create a Supabase project;
2. enable email/password auth;
3. disable public signup;
4. create/use an asymmetric JWT signing key;
5. collect project URL and publishable key;
6. create a server secret key;
7. set exact local and future production redirect URLs;
8. configure invite and password-recovery email templates;
9. invite the initial administrator through the Dashboard;
10. bootstrap the application administrator by CLI;
11. never place the secret key in frontend configuration;
12. do not claim production SMTP readiness until custom SMTP is configured.

Do not provision cloud resources automatically.

## Tests — Backend

Required automated coverage:

### JWT

All cases listed in the JWT section.

### Authentication dependencies

- valid active user;
- valid invited user accepted/activated;
- valid token with no application user denied;
- disabled user denied;
- missing token;
- malformed bearer header;
- no secret leakage.

### Preferences

- owner read;
- owner update;
- invalid value;
- user A cannot read user B through repository;
- user A cannot update user B;
- owner cannot be changed;
- context leak test across pooled transactions.

### Administrator authorization

- admin can list invitations;
- admin can invite;
- user receives 403;
- JWT role or metadata cannot self-promote;
- unknown user denied.

### Invitations

- normalization;
- duplicate active invitation;
- existing user conflict;
- capacity reached;
- concurrent fourth-user attempts;
- provider success;
- provider timeout/failure;
- failed state audit;
- no invite token persistence.

### Bootstrap

- first bootstrap;
- idempotent same bootstrap;
- conflicting second administrator refused;
- safe output.

### RLS

Run against real PostgreSQL using the runtime role:

- no tenant context means no user rows;
- A sees only A;
- A cannot modify B;
- user cannot read invitations;
- admin can perform permitted invitation queries;
- role and status cannot be self-edited;
- context resets after transaction;
- direct runtime connection does not bypass RLS.

### Migrations

- upgrade from Milestone 2;
- expected tables and policies exist;
- downgrade;
- re-upgrade.

## Tests — Frontend

Use Vitest and Testing Library for:

- login form validation and safe errors;
- invitation acceptance states;
- password reset states;
- navigation behavior;
- mobile More menu;
- admin link visibility;
- greeting-mode rendering;
- motion preference;
- settings controls;
- invitation form states;
- assistant status text;
- reduced-motion class/behavior;
- keyboard focus behavior for drawers/dialogs where practical.

Use Playwright for public smoke tests:

- unauthenticated root redirects to login;
- login page works on desktop and mobile viewport;
- keyboard navigation;
- no horizontal overflow;
- obvious accessibility landmarks;
- auth error route;
- invalid redirect parameter cannot create an open redirect.

Do not add a production auth bypass for browser tests.

Manual authenticated browser verification will use the configured Supabase project.

## Security Regression Tests

At minimum prove:

1. A forged token is rejected.
2. A token for the wrong issuer is rejected.
3. A valid Supabase token without an application user is rejected.
4. A disabled application user is rejected.
5. User A cannot read or mutate User B's preferences.
6. User A cannot access invitation administration.
7. JWT metadata cannot make a user an administrator.
8. Missing RLS context returns no protected rows.
9. Tenant context does not leak through the pool.
10. A fourth invited/active beta user cannot be created under concurrent requests.
11. The browser bundle contains no Supabase secret key.
12. Logs and API errors contain no token, password, database URL, or provider response.

## CI

Extend CI to validate both backend and frontend.

Backend:

- lockfile sync;
- Ruff format/lint;
- mypy;
- migrations;
- full tests against PostgreSQL and Redis;
- Docker image build.

Frontend:

- frozen pnpm install;
- formatting/lint;
- type-check;
- unit/component tests;
- production build;
- Playwright public smoke tests if stable within CI;
- bundle/secret scan.

Compose:

- config validation;
- API and frontend image builds;
- smoke stack where practical.

Do not deploy.

## Docker Compose

Add the frontend service and database-role initialization required by this milestone.

Requirements:

- frontend on host port 3000;
- frontend server uses API service hostname internally when containerized;
- browser-visible URLs remain valid from the host browser;
- API CORS is allow-listed only if browser-direct API calls are actually required;
- prefer server-side frontend-to-API calls and avoid permissive CORS;
- database runtime and migration credentials are separate;
- existing PostgreSQL volume must not be deleted automatically;
- document any one-time local role migration step;
- no secrets baked into images;
- API and frontend run as non-root.

Do not run `docker compose down -v`.

## Required Documentation

Create or update:

```text
docs/security/authentication-and-authorization.md
docs/security/tenant-isolation-test-plan.md
docs/deployment/supabase-auth-setup.md
docs/decisions/0005-authentication-and-session-boundary.md
docs/decisions/0006-runtime-database-role-and-rls.md
docs/milestones/milestone-04.md
docs/milestones/roadmap.md
AGENTS.md command section
```

Do not expand `README.md`.

## Allowed Change Boundaries

Codex may change:

```text
frontend/**
backend/**
infra/postgres/**
.github/workflows/**
compose.yaml
.env.example
.gitignore
AGENTS.md
docs/security/**
docs/deployment/supabase-auth-setup.md
docs/decisions/0005-*.md
docs/decisions/0006-*.md
docs/milestones/milestone-04.md
docs/milestones/roadmap.md
```

Do not change unrelated product/design documents unless a direct contradiction is found. Report a contradiction before changing it.

## Validation Sequence

Use focused checks while developing.

### Backend static checks

From `backend/`:

```powershell
uv lock --check
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
```

### Backend tests

```powershell
uv run pytest tests/unit tests/api
```

Then with real PostgreSQL/Redis:

```powershell
uv run alembic upgrade head
uv run pytest tests/integration tests/security
uv run pytest --cov=contextos --cov-report=term-missing
```

### Frontend

From `frontend/`:

```powershell
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Run public Playwright smoke tests using the configured project scripts.

### Compose

From repository root:

```powershell
docker compose config
docker compose up --build -d
docker compose ps -a
```

Verify:

- migration exits 0;
- PostgreSQL healthy;
- Redis healthy;
- API healthy;
- frontend healthy;
- `/health` and `/ready` return 200;
- login route loads;
- unauthenticated protected route redirects;
- containers run as non-root.

Then:

```powershell
docker compose down
```

Do not remove volumes.

### Repository/security review

- `git diff --check`;
- all relative Markdown links valid;
- no `.env` tracked;
- no secrets in diff;
- no server secret in frontend bundle;
- no deprecated Supabase auth helpers;
- no public signup;
- no direct domain-table browser queries;
- no auth bypass;
- no document/chat/memory implementation;
- README unchanged.

## Manual Verification

After Codex completion and mentor review, the user will manually configure a Supabase project and verify:

1. public signup is disabled;
2. local and production-intended redirect URLs are configured;
3. the first admin receives an invite;
4. invite link reaches ContextOS;
5. password setup succeeds;
6. admin bootstrap CLI succeeds;
7. admin can log in;
8. admin sees invitation management;
9. admin invites a second user;
10. second user accepts and logs in;
11. ordinary user cannot open admin;
12. each user has separate preferences;
13. greeting setting persists;
14. reduced motion works;
15. logout works;
16. password reset works;
17. a fourth beta invitation is blocked;
18. mobile navigation places Projects under More.

Codex must not claim these user checks were completed.

## Milestone Status Update

After implementation, set:

```text
Implementation complete — awaiting security review and manual Supabase verification
```

List:

- files changed;
- migrations;
- test counts;
- validation;
- deviations;
- unresolved provider/manual setup items.

Do not mark approved.

## Completion Report

Return a concise report with:

- frontend and backend implementation summary;
- auth and authorization architecture;
- migrations;
- tests and real counts;
- RLS and isolation evidence;
- frontend build result;
- Compose status;
- CI updates;
- deviations;
- manual Supabase steps still required;
- suggested commit message.

Do not commit, push, deploy, or begin Milestone 5.

## Suggested Commit Message

```text
feat: add Quiet Orbit authentication and tenant isolation
```

## Acceptance Criteria

Ready for security review only when:

- Quiet Orbit shell is responsive and accessible;
- no fake user content is shown;
- invitation acceptance, login, logout, and reset flows exist;
- public signup is unavailable;
- SSR sessions use current Supabase cookie guidance;
- FastAPI independently verifies JWTs;
- invalid, forged, expired, wrong-issuer, and wrong-audience tokens fail;
- application role comes from PostgreSQL;
- unknown and disabled users fail;
- first-admin bootstrap is explicit and non-HTTP;
- admin invitations are application-authorized;
- beta cap is concurrency-safe;
- runtime database role is not owner/superuser;
- RLS defaults to deny without context;
- users are isolated in API and direct database tests;
- tenant context cannot leak through pooled connections;
- frontend contains no secret keys;
- tests, typing, lint, migrations, builds, and Compose validation pass;
- documentation and ADRs are updated;
- README is unchanged;
- no document, retrieval, conversation, or memory feature was added;
- Codex stops for security review.
