# ADR 0002: Tenant Isolation Strategy

## Status

Accepted

## Context

ContextOS will handle private documents, conversations, memory, and retrieval for more than one user. Tenant isolation must be deterministic, testable, and enforceable before data access.

## Decision

Use FastAPI application authorization as the primary deterministic boundary, with verified token identity and no trusted client-supplied owner identifiers.

The supporting controls are:

- PostgreSQL Row-Level Security as defense in depth;
- permission filtering inside vector queries before ranking;
- private object storage with authorization-gated downloads;
- worker revalidation of ownership, state, and job eligibility;
- explicit and audited administrative separation.

The LLM never decides access.

## Alternatives Considered

- Frontend-only authorization.
- Trusting UUID secrecy as an access boundary.
- Post-filtering global vector results after ranking.
- Allowing the LLM to infer access or ownership.
- Relying on Row-Level Security alone.

## Consequences

- Every access path needs explicit ownership and authorization checks.
- Retrieval code must remain scope-aware before ranking evidence.
- Workers must verify state again instead of trusting queued requests.
- Administrative controls remain visible and auditable.

## Security Implications

- This strategy directly supports cross-user isolation.
- It reduces the chance that leaked identifiers or model output could expose private data.
- It keeps permissions outside the LLM and inside deterministic application logic.

## Future Migration Path

If the implementation grows, additional policy layers or storage mechanisms can be introduced later, but they must preserve verified identity, application authorization, tenant-filtered retrieval, private storage, and worker revalidation.
