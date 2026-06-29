# Threat Model

## Assets

- user identities and tokens;
- private PDF files;
- extracted document text and chunks;
- embeddings and retrieval indexes;
- conversations and summaries;
- approved memories;
- quotas and usage state;
- administrator actions and audit records;
- secrets, API keys, and signed access material.

## Actors

- authenticated end users;
- invited beta users;
- administrators;
- background workers;
- third-party AI providers;
- unauthenticated external attackers;
- malicious or compromised insiders.

## Trust Boundaries

- browser to frontend;
- frontend to API;
- API to database;
- API to private object storage;
- API to background queue;
- worker to database and storage;
- application to third-party AI providers;
- administrator actions to audited control paths.

## Attack Surfaces

- authenticated API endpoints;
- document upload and download paths;
- retrieval and search requests;
- background job enqueue and execution paths;
- memory approval and deletion workflows;
- administrator controls;
- logs, metrics, and traces;
- third-party provider integrations.

## Threats and Planned Mitigations

### Cross-User Access

Threat: one user attempts to read another user’s resources.

Mitigations: deterministic ownership, verified token identity, application authorization before access, PostgreSQL RLS as defense in depth, and cross-user tests.

### Direct Object ID Guessing

Threat: an attacker guesses resource identifiers.

Mitigations: authorization before every read, update, download, and deletion; no trust in UUID secrecy; private object storage; worker revalidation.

### Unauthorized File Downloads

Threat: private documents or derived files are downloaded without permission.

Mitigations: permission checks on every download path, short-lived signed access where needed, and revalidation before serving stored content.

### Permission Errors in Vector Retrieval

Threat: global vector results expose another user’s content.

Mitigations: tenant filtering before ranking, scope-aware retrieval, and tests that enforce isolation.

### Malicious PDF Content

Threat: uploaded documents contain harmful or malformed content.

Mitigations: treat uploads as untrusted data, constrain supported formats to text-based PDFs, validate parsing behavior, and isolate ingestion from permissions decisions.

### Prompt Injection

Threat: document text attempts to override system instructions or influence access decisions.

Mitigations: treat retrieved content as untrusted data, keep permission checks outside the LLM, and never let the model grant access.

### Leaked Credentials

Threat: secrets or tokens are exposed through configuration, logs, or code.

Mitigations: placeholder configuration files, secret scanning, privacy-safe logging, and least-privilege access to runtime credentials.

### Sensitive Logging

Threat: raw document content, memories, tokens, or signed URLs appear in logs.

Mitigations: structured privacy-safe logging, redaction, and explicit logging guidelines.

### Quota Bypass Through Concurrency

Threat: simultaneous requests exceed per-user or global limits.

Mitigations: concurrency-safe quota enforcement and transactional state updates.

### Replayed or Duplicated Jobs

Threat: jobs run twice or are replayed after state changes.

Mitigations: idempotent workers, job eligibility checks, and revalidation of ownership and deletion state.

### Incomplete Deletion

Threat: deleted data continues to appear in retrieval or persists in derived form.

Mitigations: immediate exclusion from retrieval, verified physical deletion, and cleanup of derived chunks and related artifacts.

### Administrator Misuse

Threat: administrators use elevated controls without visibility.

Mitigations: explicit permission checks, audit logging, and separation between administrative and user operations.

### Third-Party AI Provider Exposure

Threat: private content is disclosed to an external provider unnecessarily.

Mitigations: provider interfaces, minimal data sharing, deterministic test providers for CI, and explicit governance around provider selection.

## Residual Risks

- Third-party providers still see any content sent to them for processing.
- Misconfiguration can weaken privacy or access control if later milestones drift from the approved design.
- Natural-language systems can still generate incorrect answers even when permissions are enforced.
- Operational mistakes remain possible without disciplined review and testing.

This milestone does not claim formal compliance certification.
