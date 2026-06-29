# Milestone 1 — Product and Architecture Foundation

**Status:** Implementation complete — awaiting mentor and user review
**Project:** ContextOS — Personal Knowledge Assistant

## Goal

Create a concise, internally consistent documentation foundation for ContextOS before any application code, dependencies, database migrations, cloud resources, or frontend components are introduced.

This milestone establishes:

- the product charter;
- the exact Version 1 scope and non-goals;
- the high-level system architecture;
- the initial threat model;
- the core tenancy and authorization rules;
- the approved technology direction;
- the milestone roadmap;
- the initial repository documentation structure.

## Why This Matters

ContextOS will contain authentication, multi-tenant data, private files, vector retrieval, long-term memory, background jobs, quotas, and deletion workflows.

If ownership, authorization, memory governance, and deletion rules are not documented before implementation, later code may become inconsistent or insecure.

This milestone is documentation-only.

## Current Repository State

The repository currently contains:

```text
AGENTS.md
```

Treat the repository as greenfield.

## In Scope

1. Create the initial documentation structure.
2. Create the root project README.
3. Record the Version 1 product boundaries.
4. Document the proposed architecture and major data flows.
5. Document the initial threat model and security invariants.
6. Record the first architecture decisions.
7. Record the complete high-level milestone roadmap.
8. Add basic repository hygiene files that do not require selecting runtime dependency versions.

## Out of Scope

Do not:

- initialize Next.js;
- initialize Python or FastAPI;
- add package manifests or lockfiles;
- add Docker or Docker Compose;
- configure Supabase;
- configure PostgreSQL, pgvector, Redis, or RQ;
- create database models or migrations;
- create API routes;
- create frontend components;
- implement authentication;
- implement document ingestion;
- implement retrieval, chat, or memory;
- provision or deploy cloud resources;
- install dependencies;
- run web research;
- commit, push, merge, or open a pull request.

## Approved Direction to Document

The current approved direction is:

- **Frontend:** Next.js, TypeScript, Tailwind CSS.
- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, Alembic.
- **Database:** PostgreSQL, pgvector, PostgreSQL full-text search.
- **Authentication and storage:** Supabase Auth and private object storage.
- **Background jobs:** Redis and RQ.
- **AI:** internal provider interfaces with deterministic mocks, local development adapters, and an optional hosted provider.
- **Deployment direction:** Vercel for the frontend, Render for the API and worker, and Supabase for managed data services.
- **Beta:** free, invite-only, publicly hosted, and limited to three users.

These are architecture decisions for the beta, not claims that services are already configured.

## Provisional Beta Limits

Document these as configurable provisional limits:

- 3 invited users;
- 10 PDFs per user;
- 15 MB maximum per PDF;
- 100 MB total file storage per user;
- 500 processed pages per user;
- 250 user chat messages per calendar month;
- 100 active approved memories per user;
- 1 concurrent ingestion job per user;
- 2 concurrent ingestion jobs globally;
- text-based PDFs only in Version 1.

Do not describe these targets as measured production capacity.

## Required Files

Create or update only the following files:

```text
README.md
CONTRIBUTING.md
.editorconfig
.gitignore
.env.example

docs/product/product-charter.md
docs/product/version-1-scope.md

docs/architecture/system-overview.md

docs/security/threat-model.md
docs/security/security-invariants.md

docs/decisions/0001-beta-technology-stack.md
docs/decisions/0002-tenant-isolation-strategy.md

docs/milestones/roadmap.md
docs/milestones/milestone-01.md
```

Do not create additional files unless one is strictly required to make a relative documentation link valid. Report any such deviation before creating it.

## File Requirements

### `README.md`

Include:

- project name and tagline;
- problem being solved;
- Version 1 capabilities;
- important non-goals;
- proposed technology stack;
- current project status;
- documentation map;
- warning that application implementation has not started;
- no setup or run commands yet.

### `CONTRIBUTING.md`

Include:

- milestone-first workflow;
- requirement to read `AGENTS.md`;
- branch and commit expectations at a high level;
- testing and documentation expectations;
- no secrets;
- no fake metrics;
- no deployment without approval.

Keep it concise.

### `.editorconfig`

Add conservative cross-platform defaults for:

- UTF-8;
- LF line endings;
- final newline;
- trimming trailing whitespace;
- 4-space indentation by default;
- 2-space indentation for JSON, YAML, JavaScript, TypeScript, CSS, and Markdown where appropriate.

Do not add language tooling.

### `.gitignore`

Include only safe initial exclusions such as:

- operating-system files;
- IDE metadata;
- environment files;
- Python caches and virtual environments;
- Node dependency and build directories;
- test and coverage artifacts;
- local Supabase state if applicable later;
- temporary uploads and local data;
- logs.

Do not ignore migration files, documentation, sample configuration, or source code.

### `.env.example`

Create a documentation-only placeholder file grouped by future service area.

Rules:

- use placeholder names only;
- do not use realistic secrets;
- do not include active URLs, keys, tokens, or passwords;
- state that variables will be finalized in later milestones.

### `docs/product/product-charter.md`

Include:

- target users;
- problem statement;
- product promise;
- beta model;
- five core product loops:
  - secure entry;
  - document knowledge;
  - grounded conversation;
  - controlled memory;
  - user and administrator control;
- success principles;
- portfolio purpose;
- explicit statement that trust and control matter more than maximum automation.

### `docs/product/version-1-scope.md`

Include:

- exact included capabilities;
- provisional quotas;
- supported PDF boundary;
- deferred features;
- non-goals;
- conditions that require later user approval.

Explicitly defer:

- OCR;
- file formats other than PDF;
- Gmail, Slack, Drive, Notion, and GitHub connectors;
- team workspaces;
- billing;
- public signup;
- autonomous external actions;
- graph databases;
- LangGraph;
- Kubernetes;
- mobile applications;
- WebGL or complex 3D interfaces.

### `docs/architecture/system-overview.md`

Include:

- a Mermaid system context diagram;
- a Mermaid high-level data-flow diagram;
- responsibilities of:
  - Next.js;
  - Supabase Auth;
  - FastAPI;
  - PostgreSQL/pgvector;
  - private object storage;
  - Redis;
  - RQ worker;
  - AI provider interfaces;
  - observability;
- the request authorization sequence;
- the PDF ingestion sequence;
- the future answer-generation context sources:
  - current conversation;
  - conversation summary;
  - approved memories;
  - document evidence;
- statement that these source types remain distinguishable.

Do not define SQL tables or API contracts yet.

### `docs/security/threat-model.md`

Include:

- assets;
- actors;
- trust boundaries;
- attack surfaces;
- threats;
- planned mitigations;
- residual risks.

At minimum cover:

- cross-user access;
- direct object ID guessing;
- unauthorized file downloads;
- permission errors in vector retrieval;
- malicious PDF content;
- prompt injection;
- leaked credentials;
- sensitive logging;
- quota bypass through concurrency;
- replayed or duplicated jobs;
- incomplete deletion;
- administrator misuse;
- third-party AI provider exposure.

Do not claim formal compliance certification.

### `docs/security/security-invariants.md`

Copy and organize the non-negotiable security invariants from `AGENTS.md`.

Add clear sections for:

- identity;
- application authorization;
- Row-Level Security;
- vector retrieval;
- object storage;
- workers;
- untrusted document content;
- memory lifecycle;
- quotas;
- logging;
- deletion;
- administration;
- required cross-user tests.

Do not weaken or reinterpret the root instructions.

### ADR Format

Both ADRs must use:

- Status;
- Context;
- Decision;
- Alternatives considered;
- Consequences;
- Security implications;
- Future migration path.

### `docs/decisions/0001-beta-technology-stack.md`

Record the approved beta technology direction.

Explain why the stack is practical for:

- a three-user beta;
- portfolio value;
- existing project experience;
- low operational complexity;
- future migration.

State clearly that dependency versions and final provider choices will be selected later.

### `docs/decisions/0002-tenant-isolation-strategy.md`

Record:

- FastAPI application authorization as the primary deterministic boundary;
- verified token identity;
- no trusted client-supplied owner identifiers;
- PostgreSQL RLS as defense in depth;
- permission filtering inside vector queries before ranking;
- private object storage;
- worker revalidation;
- administrative separation and auditing.

Include rejected alternatives such as:

- frontend-only authorization;
- UUID secrecy;
- post-filtering global vector results;
- allowing the LLM to infer access.

### `docs/milestones/roadmap.md`

Document the following milestone sequence:

1. Product and architecture foundation.
2. Backend foundation and local development environment.
3. Frontend experience design.
4. Authentication, invitations, and user isolation.
5. Workspaces, document metadata, private storage, and quotas.
6. Background PDF ingestion.
7. Chunking, embeddings, and hybrid retrieval.
8. Citation-backed document chat.
9. Persistent conversations and summaries.
10. Memory model and approval workflow.
11. Memory extraction, conflict handling, and retrieval.
12. Combined context and provenance.
13. User data controls, export, and deletion.
14. Administrator and invitation controls.
15. Evaluation harness.
16. Security hardening.
17. Deployment and observability.
18. Private beta testing.
19. Documentation, case study, and release packaging.

For each milestone include:

- one-sentence goal;
- primary completion gate;
- major dependency.

Do not add implementation detail belonging to future milestone specifications.

### `docs/milestones/milestone-01.md`

Preserve this specification as the canonical Milestone 1 document.

After implementation:

- update **Status** to `Implementation complete — awaiting mentor and user review`;
- add a completion notes section;
- list validation actually performed;
- list deviations and unresolved issues;
- do not mark the milestone fully approved or complete.

## Security Requirements

The documentation must make these rules unambiguous:

1. Every user-owned resource has a deterministic owner.
2. Identity comes from a verified token.
3. Client-provided owner identifiers are not trusted.
4. Authorization occurs before data access.
5. Vector search is tenant-filtered before ranking.
6. Storage is private and permission-checked.
7. Workers revalidate resource ownership and state.
8. The LLM never grants permissions.
9. Uploaded documents are untrusted data.
10. Memory candidates cannot influence answers before approval.
11. Superseded and deleted memories are excluded from current retrieval.
12. Deleted documents are excluded from retrieval immediately.
13. Physical deletion is verified.
14. Quotas are concurrency-safe.
15. normal logs exclude raw private content and secrets.
16. administrator actions are explicit and audited.
17. automated tests will prove cross-user isolation.

## Validation

Perform only lightweight documentation and repository checks.

Required:

1. Confirm every required file exists.
2. Confirm no unapproved files were created.
3. Confirm all relative Markdown links resolve.
4. Confirm Mermaid blocks are fenced correctly.
5. Run `git diff --check`.
6. Search for likely secret patterns and confirm no secrets were added.
7. Confirm no application code, package manifests, lockfiles, migrations, containers, or cloud configuration were introduced.
8. Review for contradictions involving:
   - product scope;
   - technology direction;
   - ownership;
   - vector filtering;
   - memory approval;
   - quotas;
   - deletion;
   - deployment status.

Do not install tools only to validate Markdown.

## Completion Report

Return a concise report containing:

- files created or updated;
- major decisions documented;
- validation commands and results;
- deviations;
- unresolved questions;
- suggested commit message.

Do not commit.

## Suggested Commit Message

```text
docs: establish ContextOS product and architecture foundation
```

## Completion Notes

### Validation Performed

- Confirmed the required documentation files exist.
- Reviewed relative Markdown links for internal consistency.
- Verified Mermaid blocks are fenced in the architecture document.
- Ran `git diff --check`.
- Searched the repository for likely secret patterns and found no newly added secrets.
- Confirmed no application code, package manifests, lockfiles, migrations, containers, or cloud configuration were introduced.

### Deviations

- No deviations from the approved file list.
- No runtime initialization or dependency installation was performed.

### Unresolved Issues

- None identified in this documentation-only milestone.

## Acceptance Criteria

Milestone 1 is ready for mentor and user review when:

- all required files exist;
- documentation is internally consistent;
- Version 1 scope and deferred features are explicit;
- architecture diagrams reflect the approved direction;
- security invariants are complete and unambiguous;
- the roadmap contains all 19 milestones;
- no functional application code or dependencies were added;
- validation passes;
- Codex stops without beginning Milestone 2.
