# Tenant Isolation Test Plan

Status: Milestone 4 implementation pending security review.

## Automated Coverage

Current focused coverage includes JWT validation for valid tokens, wrong issuer, wrong audience, wrong role,
invalid subject, expired tokens, JWKS cache hits, and key refresh.

Required security-review coverage to run against PostgreSQL:

- missing tenant context returns no protected rows;
- user A reads only user A;
- user A cannot update user B preferences;
- ordinary users cannot read invitations;
- admins can list and create invitations after application authorization;
- role and status are not user-editable through direct runtime access;
- context resets after commit and rollback;
- pooled runtime connections do not leak prior tenant context;
- concurrent invitation attempts cannot create a fourth beta user.

## Manual Review Focus

- Confirm runtime database role is not table owner or superuser.
- Confirm application queries keep explicit owner filters even with RLS.
- Confirm custom PostgreSQL settings are set transaction-locally only.
- Confirm logs and API errors do not expose tokens, passwords, database URLs, signed links, or provider responses.
