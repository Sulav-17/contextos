# Version 1 Scope

## Included Capabilities

- Invite-only access for a small beta cohort.
- Private PDF upload and document storage.
- Citation-backed chat over uploaded documents.
- Persistent conversations and summaries.
- User-approved long-term memory.
- Administrator invitation and user controls.
- Data export and deletion workflows that preserve ownership rules.

## Provisional Quotas

The following limits are configurable provisional beta limits:

- 3 invited users;
- 10 PDFs per user;
- 15 MB maximum per PDF;
- 100 MB total file storage per user;
- 500 processed pages per user;
- 250 user chat messages per calendar month;
- 100 active approved memories per user;
- 1 concurrent ingestion job per user;
- 2 concurrent ingestion jobs globally;
- text-based PDFs only.

These are planning limits, not measured production capacity.

## Supported PDF Boundary

Version 1 supports text-based PDFs only. OCR and other file formats are deferred because they add complexity to ingestion, retrieval, and validation.

## Deferred Features

The following are explicitly out of scope for Version 1:

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

## Non-Goals

- General-purpose agent automation.
- Broad integration marketplace support.
- Public self-service onboarding.
- Multi-tenant collaboration beyond the approved invite-only beta.
- Unbounded ingestion, retrieval, or memory growth.

## Later Approval Required

The following require later user approval before introduction:

- any expansion beyond the approved three-user beta;
- any new file format support;
- any connector that can read external user data;
- any autonomous action that affects third-party systems;
- any change to memory approval rules;
- any change to deletion guarantees or ownership enforcement;
- any infrastructure or deployment expansion outside the approved beta direction.
