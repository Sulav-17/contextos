# Information Architecture

Related documents:
- [User Journeys](./user-journeys.md)
- [Layouts and Wireframes](./layouts-and-wireframes.md)
- [Frontend Implementation Spec](./frontend-implementation-spec.md)

## Information Architecture Direction

ContextOS should organize around user work, not around system subsystems. The UI language should make documents, conversations, projects, and memories legible as separate but connected resources.

## Workspace Model Decision

Libraries and Projects should share an underlying workspace model conceptually, but the frontend should present them as different entry points:

- Libraries: document-centered spaces for uploads, processing, and retrieval readiness.
- Projects: goal-centered spaces that assemble conversations, relevant documents, and approved memories around an active area of work.

This keeps the data model extensible while maintaining a clear mental model for users.

## Route Evaluation

### `/`

- Purpose: lightweight landing and routing surface.
- Behavior:
  - unauthenticated users move to login or invite acceptance;
  - authenticated users route to `/home` or their preferred start page.

### `/login`

- Purpose: authentication entry.
- Notes: must remain compact and trust-oriented, not product-marketing heavy.

### `/invite/accept`

- Purpose: secure invitation acceptance and pre-auth context.
- Notes: should support expired invitation and already-used invitation states.

### `/home`

- Purpose: returning-user entry hub and first-time workspace arrival.
- Notes: compact personalized overview with recent work and pending review.

### `/conversations`

- Purpose: conversation index with recent, pinned, and archived threads.
- Notes: quick search and status filtering matter more than decorative cards.

### `/conversations/[conversationId]`

- Purpose: active conversation workspace.
- Notes: this is the primary operational view for Q&A, citations, source inspection, and memory suggestions.

### `/libraries`

- Purpose: library index across user workspaces.
- Notes: highlights upload state, storage, and retrieval readiness.

### `/libraries/[workspaceId]`

- Purpose: document-centered workspace.
- Notes: supports upload, processing, library browsing, and document-level actions.

### `/projects`

- Purpose: project index.
- Notes: surfaces active work clusters and recent project-level discussions.

### `/projects/[workspaceId]`

- Purpose: project-centered workspace.
- Notes: combines conversation, relevant documents, and pending decisions.

### `/memories`

- Purpose: memory center.
- Notes: supports pending review, approved memory management, conflict resolution, filtering, and history.

### `/uploads`

- Purpose: upload and processing overview.
- Notes: can be linked from home and libraries, but should not feel like an admin queue.

### `/settings`

- Purpose: user preferences and control.
- Notes: includes greeting behavior, memory behavior, motion, theme direction, and accessibility settings.

### `/admin`

- Purpose: administrator-only controls.
- Notes: hidden entirely from unauthorized users; no teasing inaccessible controls.

## Primary Navigation

Desktop primary navigation:
- Home
- Conversations
- Libraries
- Projects
- Memories
- Uploads
- Settings
- Admin, only when authorized

Primary nav should live in a persistent left rail on desktop and tablet-expanded mode.

## Contextual Actions

- Conversations: new conversation, inspect context, view citations, memory review.
- Libraries: upload PDF, filter by status, open document, retry failed processing.
- Projects: resume work, switch active conversation, inspect related sources.
- Memories: approve, edit, reject, filter, search, view history.
- Uploads: retry, inspect failure, open related library.

## Mobile Navigation

Mobile should use a bottom navigation with:
- Home
- Conversations
- Libraries
- Memories
- More

The "More" sheet contains Projects, Uploads, Settings, and Admin when authorized.

## Context Inspector Behavior

- On desktop: right-side inspector panel with pinned width.
- On tablet: slide-over drawer.
- On mobile: bottom sheet or full-screen drawer.

The inspector contains:
- source summary;
- document citations and previews;
- approved memory records used;
- conversation summary usage;
- processing state where relevant;
- reason codes for source inclusion;
- incorrect-context controls.

## Deep Links

Deep linking should support:
- opening a conversation directly;
- opening a project directly;
- opening a specific memory review state;
- opening a document from a citation or upload failure;
- opening settings subsections.

Deep links should preserve enough route state to reopen the relevant inspector or review panel when appropriate.

## Admin-Only Routes

- `/admin` is permission-gated and omitted from standard navigation for non-admin users.
- Any admin-only deep link should fail safely with a clear permission message and no data exposure.

## Main Workspace

### Navigation

- Home
- Conversations
- Libraries
- Projects
- Memories
- Uploads
- Settings
- Admin only for authorized users

### Main area

The main workspace should prioritize:

- the active assistant conversation;
- suggested next actions;
- recent activity relevant to the current workspace;
- document processing state when applicable;
- pending memory suggestions when applicable;
- useful empty states;
- one clear primary action at any given moment.

### Context inspector

The context inspector must allow inspection of:

- document sources;
- approved memories;
- conversation summary usage;
- citations and excerpts;
- processing state;
- factual reason codes for source selection;
- controls to report or remove incorrect context.

The inspector must not expose invented chain-of-thought.

## Home Screen Priorities

Desktop above the fold:

- compact personalized greeting;
- continue recent conversation;
- active project;
- recent documents;
- pending memory suggestions;
- storage and chat usage;
- one primary quick action.

Mobile above the fold:

- compact greeting;
- continue recent conversation;
- upload action;
- one recent document or pending memory card;
- usage summary below the first task row.

Empty state priority:

- explain that the workspace is ready;
- give one upload action;
- explain citations and approved memory behavior in one short line.

## Conversation Experience

Conversation routes must include:

- document citations;
- memory indicators;
- collapsible source previews;
- assistant status;
- context inspector access;
- follow-up suggestions;
- memory approval prompts;
- incorrect-context controls;
- refusal state;
- retry state;
- distinct source types.

Every answer should use a summary pattern equivalent to:

```text
Used 3 document sources
Used 2 approved memories
Used the current conversation summary
```

Users must be able to inspect the exact persisted source records that were surfaced to them.

## Memory Experience

Each memory record should show:

- category;
- content;
- source;
- created date;
- last verified date;
- privacy or sensitivity status;
- approval status;
- active, superseded, or expired state;
- edit;
- delete;
- history;
- workspace scope.

Supported categories:

- Background
- Preference
- Goal
- Project
- Decision
- Constraint
- Achievement

Memory UX states that must be supported:

- pending;
- edit before approval;
- rejection;
- duplicate warning;
- conflict warning;
- supersession;
- deletion;
- memory disabled;
- empty state;
- filtering and search.
