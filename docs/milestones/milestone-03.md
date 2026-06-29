# Milestone 3 — Frontend Experience Design

**Status:** Approved — ready for frontend implementation
**Project:** ContextOS — Personal Knowledge Assistant  
**Execution mode:** Design approval gate

## Completion Notes

- Changed files:
  - `docs/frontend/experience-concepts.md`
  - `docs/frontend/user-journeys.md`
  - `docs/frontend/information-architecture.md`
  - `docs/frontend/layouts-and-wireframes.md`
  - `docs/frontend/design-system.md`
  - `docs/frontend/assistant-identity-and-motion.md`
  - `docs/frontend/accessibility-strategy.md`
  - `docs/frontend/performance-strategy.md`
  - `docs/frontend/component-inventory.md`
  - `docs/frontend/frontend-implementation-spec.md`
  - `docs/decisions/0004-frontend-experience-direction.md`
  - `docs/milestones/milestone-03.md`
  - `docs/milestones/roadmap.md`
- Validation:
  - confirmed all required files exist;
  - confirmed the package remains documentation-only;
  - confirmed three concepts are materially distinct and one recommendation is explicit;
  - confirmed desktop, tablet, and mobile coverage;
  - confirmed 12 ASCII wireframes exist;
  - confirmed measurable accessibility and performance targets are documented;
  - confirmed implementation remains blocked pending concept approval;
  - `git diff --check`
- Deviations:
  - none.
- Unresolved design decisions:
  - none.

## Goal

Define the complete frontend experience before any frontend code is created.

Deliver:

- three materially distinct visual concepts;
- one recommended concept;
- first-time and returning-user journeys;
- desktop, tablet, and mobile layouts;
- assistant identity and state model;
- motion and reduced-motion behavior;
- accessibility strategy;
- measurable performance budgets;
- information architecture;
- component inventory;
- low-fidelity wireframes;
- source-transparency and memory-control interactions;
- a Codex-ready frontend implementation specification.

This milestone is documentation-only.

## Why This Stays Separate

The roadmap is being fast-tracked, but frontend design remains an approval gate because the product brief requires three concepts, wireframes, accessibility, performance planning, and user approval before implementation.

## Recommended Codex Settings

- **Model:** GPT-5.4
- **Reasoning:** Medium
- **Fast mode:** Off
- **Subagents:** Off
- **Web access:** Off

## Read Only

- `AGENTS.md`
- `docs/product/product-charter.md`
- `docs/product/version-1-scope.md`
- `docs/architecture/system-overview.md`
- `docs/security/security-invariants.md`
- `docs/milestones/roadmap.md`
- this milestone specification

Do not recursively inspect the repository.

## Experience Direction

ContextOS should feel like a private, calm, futuristic knowledge space where documents, conversations, projects, and approved memories form one understandable system.

It should feel:

- welcoming;
- intelligent;
- calm;
- personal;
- immersive;
- trustworthy;
- technically sophisticated.

It must not feel:

- clinical;
- crypto-themed;
- like a gaming HUD;
- like a sci-fi control panel;
- overanimated;
- cluttered with glow;
- confusing;
- decorative at the expense of usability;
- like a generic SaaS dashboard;
- like a direct ChatGPT clone.

## In Scope

1. Three visual concepts.
2. Recommended concept and rationale.
3. First-time and returning-user journeys.
4. Desktop, tablet, and mobile layouts.
5. Route and information architecture.
6. Assistant identity and states.
7. Motion system.
8. Accessibility strategy.
9. Performance strategy and budgets.
10. Design-token direction.
11. Component inventory.
12. Low-fidelity wireframes.
13. Source and provenance interactions.
14. Memory approval and management interactions.
15. Empty, loading, error, quota, and offline states.
16. Frontend package recommendations.
17. Exact frontend file plan.
18. Codex-ready implementation specification.
19. User approval checklist.

## Out of Scope

Do not:

- initialize Next.js;
- create `package.json` or lockfiles;
- install dependencies;
- create React, TypeScript, CSS, SVG, image, or test files;
- implement routes or components;
- connect to the backend;
- modify backend, Compose, CI, or README;
- use web search, image generation, or external design tools;
- commit, push, or begin frontend implementation.

## Allowed Files

Create or update only:

```text
docs/frontend/experience-concepts.md
docs/frontend/user-journeys.md
docs/frontend/information-architecture.md
docs/frontend/layouts-and-wireframes.md
docs/frontend/design-system.md
docs/frontend/assistant-identity-and-motion.md
docs/frontend/accessibility-strategy.md
docs/frontend/performance-strategy.md
docs/frontend/component-inventory.md
docs/frontend/frontend-implementation-spec.md
docs/decisions/0004-frontend-experience-direction.md
docs/milestones/milestone-03.md
docs/milestones/roadmap.md
```

Do not modify `README.md`.

## Three Visual Concepts

Each concept must include:

- name and one-sentence idea;
- emotional tone;
- visual metaphor;
- entry experience;
- main workspace;
- assistant identity;
- document, memory, project, and conversation representation;
- navigation;
- source transparency;
- motion;
- mobile adaptation;
- accessibility implications;
- performance implications;
- strengths;
- weaknesses;
- implementation risk;
- fit for ContextOS.

The concepts must not be cosmetic variations of one dashboard.

All concepts must avoid:

- human avatars;
- robotic faces;
- cartoon mascots;
- generic sparkle icons;
- heavy 3D;
- WebGL;
- constant pulsing;
- inaccessible motion;
- hidden source provenance.

At least one concept must emphasize a calm ambient assistant.
At least one must emphasize layered cards and timelines.
At least one must emphasize connected nodes or constellations without becoming a graph-exploration product.

## Recommended Concept

Select one concept and explain why it is strongest for:

- trust;
- uniqueness;
- implementation feasibility;
- accessibility;
- responsiveness;
- performance;
- transparency;
- portfolio value;
- future extensibility.

Also document:

- ideas borrowed from the other concepts;
- explicitly rejected ideas;
- what would make the selected concept excessive.

## User Journeys

### First-time user

Cover:

1. invitation acceptance;
2. authentication handoff;
3. short welcome;
4. what ContextOS remembers and retrieves;
5. privacy and memory controls;
6. suggested first actions;
7. workspace entry;
8. first upload;
9. processing state;
10. first question;
11. citation inspection;
12. first memory suggestion;
13. approve, edit, or reject;
14. return to the workspace.

Requirements:

- no long mandatory introduction;
- greeting is skippable;
- reduced motion is respected;
- memory never feels secretly enabled;
- document, conversation, and memory sources remain distinct.

### Returning user

Cover:

- personalized greeting;
- continue recent conversation;
- open active project;
- inspect recently processed documents;
- review pending memories;
- see usage;
- skip greeting;
- open directly into workspace;
- resume after ingestion failure;
- understand superseded memory.

Returning users should reach useful work quickly.

## Information Architecture

Evaluate and document routes such as:

```text
/
 /login
 /invite/accept
 /home
 /conversations
 /conversations/[conversationId]
 /libraries
 /libraries/[workspaceId]
 /projects
 /projects/[workspaceId]
 /memories
 /uploads
 /settings
 /admin
```

Clarify:

- whether Libraries and Projects share an underlying workspace model;
- primary navigation;
- contextual actions;
- mobile navigation;
- context-inspector behavior;
- deep links;
- admin-only routes.

Do not define backend API contracts.

## Main Workspace

Design:

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

- assistant conversation;
- suggested actions;
- recent activity;
- processing state;
- memory suggestions;
- useful empty states;
- clear primary action.

### Context inspector

Allow inspection of:

- document sources;
- approved memories;
- conversation summary;
- citations and excerpts;
- processing state;
- factual reason codes for source selection;
- controls to report or remove incorrect context.

Do not expose invented chain-of-thought.

## Home Screen

Prioritize a restrained subset of:

- personalized greeting;
- recent conversations;
- active projects;
- recent documents;
- pending memory suggestions;
- unresolved decisions when genuinely represented;
- storage and chat usage;
- quick actions.

Define desktop and mobile priority, above-the-fold content, and empty states.

## Conversation Experience

Include:

- document citations;
- memory indicators;
- collapsible source previews;
- assistant status;
- context inspector;
- follow-up suggestions;
- memory approval prompts;
- incorrect-context controls;
- refusal state;
- retry state;
- distinct source types.

Example:

```text
Used 3 document sources
Used 2 approved memories
Used the current conversation summary
```

Users must be able to inspect the exact persisted source records.

## Memory Experience

Each memory object should show:

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

Categories:

- Background
- Preference
- Goal
- Project
- Decision
- Constraint
- Achievement

Design states for:

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

## Assistant Identity

Define one restrained identity from:

- ambient orb;
- softly glowing node;
- abstract symbol;
- responsive waveform;
- small constellation.

Avoid faces, avatars, mascots, sparkle icons, constant pulsing, and particle storms.

Define visual and accessible behavior for:

- idle;
- listening;
- retrieving documents;
- retrieving memories;
- reading;
- thinking;
- preparing answer;
- waiting for memory approval;
- completed;
- error;
- dependency unavailable.

Every state needs:

- visual treatment;
- text label;
- screen-reader behavior;
- reduced-motion equivalent;
- stale-state behavior when applicable.

## Motion System

Document:

- durations;
- easing categories;
- route transitions;
- loading behavior;
- context-panel expansion;
- assistant-state transitions;
- maximum simultaneous animated regions;
- reduced-motion substitutions;
- mobile simplification.

Avoid:

- constant floating;
- continuous pulsing;
- cinematic introductions;
- blocking transitions;
- animation on every element;
- heavy parallax;
- 3D camera motion.

Motion must never delay task completion.

## Design System

Document semantic roles for:

- deep navy or near-black foundation;
- soft blue and violet atmosphere;
- cyan intelligence/retrieval accent;
- warm neutral or subtle amber accent;
- off-white text;
- translucent layered surfaces;
- restrained blur;
- gentle borders;
- sparse connected lines.

Propose semantic tokens such as:

```text
--surface-base
--surface-raised
--surface-overlay
--text-primary
--text-muted
--accent-intelligence
--accent-memory
--accent-document
--status-warning
--focus-ring
```

Also define:

- typography roles and fallbacks;
- spacing;
- radius;
- borders;
- shadows;
- focus treatment;
- status treatment;
- source-type differentiation;
- icon direction;
- a future light-mode strategy.

Do not download or commit fonts.

## Responsive Design

### Desktop

Define navigation, conversation width, assistant placement, context inspector, and atmosphere.

### Tablet

Define collapsible navigation, inspector drawer, reduced decorative layers, and touch behavior.

### Mobile

Define compact greeting, bottom navigation or drawer, full-width chat, collapsible sources, upload flow, memory approval, safe areas, and touch targets.

Do not merely stack the desktop layout.

## Accessibility

Document a WCAG 2.2 AA direction including:

- semantic landmarks;
- headings;
- keyboard navigation;
- focus management;
- dialogs and drawers;
- screen-reader labels;
- live regions;
- accessible loading states;
- reduced motion;
- contrast;
- non-color source labels;
- error handling;
- touch targets;
- skip links;
- timeout behavior;
- mobile accessibility;
- future automated and manual testing.

Explicitly state:

- no information relies only on color;
- animation has text equivalents;
- visual connections are supplemental;
- all workflows work without animation;
- the context inspector is keyboard accessible;
- memory approval cannot be triggered accidentally.

## Performance Budgets

Set measurable acceptance targets for:

- unauthenticated initial JavaScript;
- authenticated shell JavaScript;
- Largest Contentful Paint;
- Interaction to Next Paint;
- Cumulative Layout Shift;
- route transitions;
- animation frame rate;
- image/SVG weight;
- font loading;
- mobile performance;
- reduced-data behavior.

Treat these as targets, not measured results.

Prefer:

- React Server Components where suitable;
- route-level loading;
- dynamic loading of secondary panels;
- CSS and lightweight SVG;
- minimal client state;
- no WebGL;
- no autoplay video;
- no large background images;
- no heavy animation runtime without proven value.

Explain how the budgets will later be measured.

## Component Inventory

Group components under:

- application shell;
- navigation;
- assistant identity;
- conversation;
- citations and source previews;
- context inspector;
- documents and uploads;
- memory;
- home;
- settings;
- admin;
- status and feedback;
- primitives.

For each component list:

- purpose;
- major states;
- accessibility considerations;
- server/client preference;
- reuse;
- implementation priority.

Do not create code.

## Required Wireframes

Use Markdown and ASCII for:

1. first-time welcome;
2. returning-user home;
3. desktop conversation with context inspector;
4. mobile conversation;
5. library/workspace;
6. upload and processing;
7. memory centre;
8. memory approval;
9. settings for greeting, memory, motion, and theme;
10. admin overview;
11. empty state;
12. insufficient-evidence refusal.

Emphasize hierarchy and interaction, not decoration.

## System States

Define UX for:

- no documents;
- no conversations;
- no memories;
- processing;
- failed ingestion;
- retryable failure;
- backend unavailable;
- storage quota reached;
- chat quota reached;
- memory limit reached;
- expired invitation;
- disabled account;
- insufficient evidence;
- old conversation referencing deleted source;
- reduced-motion mode;
- offline or slow network.

Errors must be specific, actionable, and privacy-safe.

## Package Recommendations

Evaluate only likely implementation needs:

- Next.js;
- TypeScript;
- Tailwind CSS;
- Radix UI primitives;
- TanStack Query;
- Zod;
- React Hook Form if justified;
- a restrained icon package;
- Vitest;
- Testing Library;
- Playwright;
- CSS-only motion versus a lightweight motion package.

Prefer the smallest package set.

Do not recommend heavy component suites, WebGL, or large animation systems.

Do not create manifests.

## Exact Frontend File Plan

Propose the next milestone structure, including:

```text
frontend/
  app/
  components/
  features/
  lib/
  styles/
  tests/
  public/
```

Define:

- route groups;
- server/client boundaries;
- feature folders;
- primitives;
- API client;
- future auth boundary;
- test organization;
- asset strategy.

Do not create these files.

## Frontend Implementation Specification

Create:

```text
docs/frontend/frontend-implementation-spec.md
```

It must include:

- approved-concept placeholder;
- routes;
- packages;
- exact file boundaries;
- tokens;
- component priorities;
- responsive rules;
- accessibility requirements;
- motion requirements;
- performance budgets;
- tests;
- non-goals;
- acceptance criteria;
- manual verification.

Mark concept-dependent sections:

```text
Quiet Orbit is the approved concept
```

Implementation must remain blocked until concept approval.

## ADR

Create:

```text
docs/decisions/0004-frontend-experience-direction.md
```

Use:

- Status;
- Context;
- Decision;
- Alternatives considered;
- Consequences;
- Accessibility implications;
- Performance implications;
- Future migration path.

Status:

```text
Proposed — awaiting user approval
```

Record the three concepts, recommendation, borrowed ideas, rejected ideas, and implementation block.

## Roadmap Update

Update the roadmap only to:

- show Milestone 2 as approved;
- show Milestone 3 as the active design gate;
- state that implementation follows concept approval;
- preserve the fast-tracked 12-milestone sequence.

## Milestone Status Update

Store this file as:

```text
docs/milestones/milestone-03.md
```

After producing the design package:

- set status to `Design package complete — awaiting mentor and user concept approval`;
- list changed files;
- list validation;
- list deviations;
- list unresolved design decisions;
- do not mark approved;
- do not begin frontend implementation.

## Validation

Required:

1. All required files exist.
2. No frontend code or manifests exist.
3. No files outside approved paths changed.
4. Relative Markdown links resolve.
5. Fences are balanced.
6. All 12 wireframes exist.
7. Three concepts are materially distinct.
8. One recommendation is explicit.
9. Desktop, tablet, and mobile are covered.
10. Accessibility and performance targets are measurable.
11. No images, font files, or generated assets were added.
12. Implementation is blocked pending approval.
13. `git diff --check` passes.

Do not install documentation tools.

## Completion Report

Return:

- files changed;
- three concept names;
- recommended concept;
- major journey and layout decisions;
- accessibility direction;
- performance budgets;
- package summary;
- validation;
- deviations;
- unresolved decisions needing approval;
- suggested commit message.

Do not commit, push, implement frontend code, or begin the next milestone.

## Suggested Commit Message

```text
docs: define ContextOS frontend experience
```

## Acceptance Criteria

Ready for review only when:

- three distinct concepts exist;
- one is recommended;
- both user journeys are complete;
- desktop, tablet, and mobile are defined;
- assistant states are defined;
- motion and reduced motion are defined;
- source transparency is clear;
- memory controls are clear;
- accessibility is complete;
- measurable performance budgets exist;
- component inventory is complete;
- all wireframes exist;
- implementation file plan is explicit;
- implementation specification exists;
- implementation remains blocked;
- no frontend code or dependencies were added;
- README was not changed;
- Codex stops.
