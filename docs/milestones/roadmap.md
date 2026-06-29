# Milestone Roadmap

## 1. Product and architecture foundation

- Goal: establish the documentation baseline, product boundaries, security invariants, and approved technical direction.
- Completion gate: canonical product, architecture, security, ADR, and roadmap documents are in place and internally consistent.
- Major dependency: none.

## 2. Backend foundation and local development environment

- Goal: create the backend project skeleton and local development setup.
- Completion gate: the backend runs locally with its initial structure and developer workflow.
- Major dependency: approved technology direction from Milestone 1.

## 3. Frontend experience design

- Goal: define the initial user experience and visual direction.
- Completion gate: the frontend design system and primary user flows are documented and ready for implementation.
- Major dependency: product scope from Milestone 1.

## 4. Authentication, invitations, and user isolation

- Goal: implement identity, invitation flow, and tenant isolation controls.
- Completion gate: invited users can authenticate and access only their own data.
- Major dependency: backend foundation and tenant isolation strategy.

## 5. Workspaces, document metadata, private storage, and quotas

- Goal: establish user-owned document records, private storage, and quota enforcement.
- Completion gate: document metadata, private storage, and quota rules work together safely.
- Major dependency: authentication and backend foundations.

## 6. Background PDF ingestion

- Goal: process uploaded PDFs asynchronously and safely.
- Completion gate: PDF ingestion runs through a bounded background workflow with ownership checks.
- Major dependency: private storage, quotas, and worker infrastructure.

## 7. Chunking, embeddings, and hybrid retrieval

- Goal: prepare document text for retrieval and support hybrid search.
- Completion gate: document chunks and retrieval indexes are available for authorized queries.
- Major dependency: ingestion pipeline and data foundation.

## 8. Citation-backed document chat

- Goal: answer questions with evidence from user documents.
- Completion gate: chat responses include grounded citations from authorized document evidence.
- Major dependency: chunking, embeddings, and retrieval.

## 9. Persistent conversations and summaries

- Goal: store conversation history and derived summaries for continuity.
- Completion gate: conversations persist across sessions and can be summarized safely.
- Major dependency: authenticated chat and backend state.

## 10. Memory model and approval workflow

- Goal: define user-controlled long-term memory with explicit approval.
- Completion gate: memory candidates can be reviewed and approved before use.
- Major dependency: persistent conversations and product memory rules.

## 11. Memory extraction, conflict handling, and retrieval

- Goal: extract memory candidates and manage conflicts and supersession.
- Completion gate: memory extraction is governed, reviewable, and retrieval-safe.
- Major dependency: memory model and approval workflow.

## 12. Combined context and provenance

- Goal: assemble conversation, memory, and document evidence into traceable answer context.
- Completion gate: answer context remains provenance-aware and source types stay distinguishable.
- Major dependency: retrieval, chat, and memory milestones.

## 13. User data controls, export, and deletion

- Goal: provide user-facing export and deletion controls.
- Completion gate: export and deletion workflows are complete and verified.
- Major dependency: ownership, storage, chat, and memory foundations.

## 14. Administrator and invitation controls

- Goal: add explicit administrative controls for invitations and user management.
- Completion gate: administrative actions are permission-checked and audited.
- Major dependency: authentication and tenant isolation.

## 15. Evaluation harness

- Goal: measure behavior, grounding, and security-sensitive outcomes.
- Completion gate: repeatable evaluation exists for the approved product behaviors.
- Major dependency: retrieval, chat, and memory features.

## 16. Security hardening

- Goal: reinforce the system with additional defensive controls and checks.
- Completion gate: major security invariants are verified across the implementation.
- Major dependency: core product and infrastructure features.

## 17. Deployment and observability

- Goal: make the system operational in the approved environments with visible telemetry.
- Completion gate: deployment paths and observability are documented and functioning.
- Major dependency: backend, frontend, and infrastructure foundations.

## 18. Private beta testing

- Goal: run the invite-only beta with real users and controlled feedback.
- Completion gate: beta usage is monitored and reviewed against the approved limits.
- Major dependency: deployment, security, and product readiness.

## 19. Documentation, case study, and release packaging

- Goal: package the project narrative, documentation, and public-facing summary.
- Completion gate: documentation is complete enough to explain the product, architecture, and learnings.
- Major dependency: the preceding milestones and validated implementation experience.
