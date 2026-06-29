# Milestone Roadmap

## 1. Product and architecture foundation

- Status: approved.
- Absorbs original milestones: 1.
- Goal: establish the documentation baseline, product boundaries, security invariants, and approved technical direction.
- Security review gate: architecture and security invariants must be approved before any implementation milestone begins.

## 2. Backend and local platform foundation

- Status: implementation approved to start; not a later feature milestone.
- Absorbs original milestones: 2.
- Goal: create the typed backend foundation, local infrastructure, migrations, CI workflow, and reproducible developer platform.
- Security review gate: infrastructure, logging, readiness, and migration behavior must be reviewed before authentication or tenant-owned data models begin.

## 3. Frontend experience design

- Absorbs original milestones: 3.
- Goal: define the initial user experience and visual direction before frontend implementation.
- Security review gate: none beyond existing product and architecture constraints because this remains a design milestone.

## 4. Authentication, invitations, and tenant isolation

- Absorbs original milestones: 4.
- Goal: implement identity, invitation flow, and tenant isolation controls.
- Security review gate: adversarial authorization and cross-tenant access tests are required before proceeding.

## 5. Workspaces, private storage, quotas, and background PDF ingestion

- Absorbs original milestones: 5 and 6.
- Goal: establish user-owned records, private storage, quota enforcement, and bounded ingestion workers for PDFs.
- Security review gate: ownership, storage authorization, worker eligibility checks, and quota safety must pass before retrieval work begins.

## 6. Chunking, embeddings, hybrid retrieval, citation-backed chat, and persistent conversations

- Absorbs original milestones: 7, 8, and 9.
- Goal: build authorized retrieval, grounded chat, and conversation persistence without introducing long-term memory yet.
- Security review gate: retrieval authorization, citation grounding, and conversation access controls must be reviewed before memory is introduced.

## 7. Memory approval, conflict handling, retrieval, and combined context

- Absorbs original milestones: 10, 11, and 12.
- Goal: implement user-approved memory, conflict handling, memory retrieval, and combined context assembly with provenance.
- Security review gate: approved-memory-only behavior and deletion/supersession exclusion rules must be verified before export and deletion controls.

## 8. User data controls, administrator controls, export, and verified deletion

- Absorbs original milestones: 13 and 14.
- Goal: provide user export/deletion workflows and permission-checked administrative controls with auditability.
- Security review gate: verified deletion, administrative auditability, and cross-user isolation tests must pass before hardening.

## 9. Evaluation harness and security hardening

- Absorbs original milestones: 15 and 16.
- Goal: measure grounded behavior and reinforce security-sensitive controls across the implementation.
- Security review gate: evaluation and hardening outputs must be reviewed before deployment work.

## 10. Deployment and observability

- Absorbs original milestones: 17.
- Goal: make the system operational in approved environments with visible telemetry and deployment procedures.
- Security review gate: deployment configuration, secret handling, and operational monitoring must be reviewed before beta testing.

## 11. Private beta testing and remediation

- Absorbs original milestones: 18.
- Goal: run the invite-only beta, collect issues, and remediate approved findings.
- Security review gate: beta access boundaries and remediation tracking must remain in place throughout testing.

## 12. Documentation, case study, and release packaging

- Absorbs original milestones: 19.
- Goal: finalize documentation, project narrative, and release packaging after validated implementation experience.
- Security review gate: documentation must not expose secrets, private data, or unsupported claims.
