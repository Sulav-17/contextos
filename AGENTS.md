# AGENTS.md

## Project

**ContextOS — Personal Knowledge Assistant**

A hosted, invite-only, multi-user application for private PDF libraries, citation-backed chat, persistent conversations, and user-approved long-term memory.

Build this repository one approved milestone at a time.

## Instruction Order

Follow, in order:

1. The user's current prompt.
2. This file.
3. The active file in `docs/milestones/`.
4. Relevant ADRs and architecture/security documentation.
5. Existing repository conventions.

If instructions conflict, stop and report the conflict. Do not guess.

## Working Protocol

For every task:

1. Identify the active milestone and acceptance criteria.
2. Read only the minimum relevant files.
3. Inspect existing code before editing.
4. Give a concise plan.
5. Make the smallest coherent change.
6. Add or update focused tests.
7. Run focused checks first and required broader checks once at the end.
8. Review the final diff for scope, security, and regressions.
9. Report changes, checks run, limitations, and a suggested commit message.
10. Stop. Never begin the next milestone automatically.

Do not mark a milestone complete until automated checks pass and required manual verification is approved by the user.

## Token and Context Discipline

- Do not recursively read the entire repository or `docs/`.
- Begin with this file, the active milestone, and directly relevant files.
- Use targeted `rg`, `find`, or narrow globs before opening files.
- Do not print full lockfiles, generated files, dumps, or long logs.
- Do not repeatedly reopen unchanged files.
- Summarize long command output.
- Do not use subagents, web search, browsers, MCP servers, or external connectors unless explicitly requested.
- Do not inspect unrelated branches, history, or ignored files.
- Do not perform broad refactors during focused work.
- Do not run the full test suite after every edit.
- If the same command or approach fails twice, stop and report the blocker instead of looping.
- Keep plans and final reports concise.
- Stop when the requested work is complete.

## Scope Control

- Implement only the requested milestone or fix.
- Do not add stretch goals or speculative abstractions.
- Do not replace approved technologies without an ADR and user approval.
- Do not add production dependencies unless required.
- Do not rename or reorganize unrelated files.
- Do not provision, deploy, commit, push, merge, or open a pull request unless explicitly requested.
- Suggest a commit message, but do not commit by default.
- Do not edit an applied migration; create a new migration.

## Non-Negotiable Security Invariants

1. Every user-owned resource has a deterministic authenticated owner.
2. Identity comes from a verified token, never a client-supplied `owner_id`.
3. Application code authorizes every read, update, download, and deletion.
4. Row-Level Security is defense in depth, not a replacement for application authorization.
5. Vector retrieval filters by authorized owner and scope before ranking.
6. Object storage is private; downloads require authorization and short-lived signed access.
7. Workers revalidate ownership, resource state, deletion state, and job eligibility.
8. The LLM never decides permissions.
9. Uploaded documents and retrieved text are untrusted data, not instructions.
10. Unapproved memory candidates are never used in answers.
11. Deleted, expired, rejected, or superseded memories are excluded from current retrieval.
12. Deleted documents and derived chunks stop appearing in retrieval immediately.
13. Physical deletion of files and derived data is verified.
14. Quotas are concurrency-safe.
15. Secrets, tokens, signed URLs, raw documents, full messages, and memory contents do not appear in normal logs.
16. Administrative actions are permission-checked and audited.
17. Tests must prove one user cannot access another user's resources.

Never weaken these rules to make a test pass.

## Approved Architecture Direction

- Frontend: Next.js, TypeScript, Tailwind CSS.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic.
- Data: PostgreSQL, pgvector, PostgreSQL full-text search.
- Identity/storage: Supabase Auth and private object storage.
- Background work: Redis and RQ.
- AI: internal provider interfaces with deterministic test providers, local adapters, and an optional hosted provider.
- Deployment: separate local, test, staging, and production environments.

Keep authentication, authorization, ingestion, retrieval, conversations, memory, usage, deletion, and administration as distinct domain concerns.

Do not:

- put business authorization in the frontend;
- couple domain services directly to one AI vendor;
- merge documents and memories into an indistinguishable source type;
- add LangGraph, a graph database, Kubernetes, billing, connectors, OCR, or autonomous actions unless an approved milestone requires them.

## Engineering Standards

Use:

- explicit type hints;
- small focused modules;
- validated boundary models;
- SQLAlchemy 2-style patterns;
- Alembic migrations;
- deterministic ownership filters;
- structured errors and privacy-safe logs;
- bounded retries and idempotent jobs;
- safe transactions and UTC timestamps;
- provider interfaces for nondeterministic AI services.

Avoid:

- giant service files;
- hidden mutable globals;
- arbitrary model-generated SQL;
- authorization based on UUID secrecy;
- unbounded queries, uploads, prompts, retries, or jobs;
- broad exception handling without controlled recovery;
- fake metrics, scale, accuracy, or production claims.

Prefer simple code over premature abstraction.

## Testing Rules

Add the smallest meaningful tests for each change. As applicable, include unit, API, database, authorization, worker, ingestion, retrieval, memory, quota, deletion, security, evaluation, and end-to-end tests.

- Never delete or weaken a valid test to make code pass.
- Never mock the exact behavior being tested.
- Use deterministic AI providers in normal CI.
- Keep tests isolated and repeatable.
- State which checks were not run and why.
- Do not claim manual verification unless it occurred.
- Do not claim the full suite passed unless it was actually run.

## Documentation

Maintain:

```text
docs/
  architecture/
  decisions/
  deployment/
  evaluation/
  milestones/
  product/
  security/
```

- Record major decisions as lightweight ADRs.
- Update behavior and documentation together.
- Use relative links.
- Keep one canonical source for each large specification.
- Record tradeoffs, security effects, and migration paths.
- Use only measured metrics.

## Frontend Constraints

Frontend work must wait for the approved design milestone.

The interface must remain accessible, responsive, transparent, and useful without animation.

- Do not create a generic ChatGPT clone or generic SaaS dashboard.
- Do not sacrifice readability for atmospheric effects.
- Do not use heavy 3D or WebGL without approval.
- Respect `prefers-reduced-motion`.
- Communicate state with accessible text, not animation or colour alone.
- Preserve keyboard navigation, visible focus, contrast, clear errors, and touch targets.
- Make citations, memory use, and context inspection understandable.
- Measure performance rather than claiming it.

## Commands

Run backend commands from `backend/` unless noted otherwise.

- Dependency synchronization: `uv sync --locked --all-groups`
- Run the API: `uv run uvicorn contextos.main:app --host 127.0.0.1 --port 8000`
- Format code: `uv run ruff format .`
- Check formatting: `uv run ruff format --check .`
- Lint: `uv run ruff check .`
- Type-check: `uv run mypy src tests`
- Focused unit and API tests: `uv run pytest tests/unit tests/api`
- Full backend tests: `uv run pytest`
- Run migrations: `uv run alembic upgrade head`
- Docker Compose startup: `docker compose up --build -d`
- Docker Compose status: `docker compose ps`
- Docker Compose logs: `docker compose logs --no-log-prefix api`
- Docker Compose shutdown without deleting volumes: `docker compose down`
- Full local smoke verification:
  1. `uv sync --locked --all-groups`
  2. `docker compose up --build -d`
  3. `docker compose ps`
  4. `Invoke-RestMethod http://localhost:8000/health`
  5. `Invoke-RestMethod http://localhost:8000/ready`
  6. `uv run pytest`
  7. `docker compose down`

## Task Definition of Done

A Codex task is ready for user review only when:

- requested scope is implemented;
- security and ownership effects were reviewed;
- relevant tests were added or updated;
- required checks passed;
- the diff contains no unrelated changes;
- documentation was updated where needed;
- no secrets or private data were introduced;
- limitations and unrun checks are disclosed;
- a concise report and suggested commit message are provided;
- Codex stopped without starting the next milestone.

Codex's report is not final milestone approval. The user and mentor complete review and manual verification.
