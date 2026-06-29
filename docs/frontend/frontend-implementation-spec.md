# Frontend Implementation Specification

Status: Quiet Orbit approved, implementation blocked until frontend implementation begins

Related documents:
- [Experience Concepts](./experience-concepts.md)
- [Information Architecture](./information-architecture.md)
- [Layouts and Wireframes](./layouts-and-wireframes.md)
- [Design System](./design-system.md)
- [Assistant Identity and Motion](./assistant-identity-and-motion.md)
- [Accessibility Strategy](./accessibility-strategy.md)
- [Performance Strategy](./performance-strategy.md)
- [Component Inventory](./component-inventory.md)

## Implementation Block

Frontend implementation remains blocked until the user approves one concept from Milestone 3.

## Approved-Concept Placeholder

Quiet Orbit is the approved concept. Implementation remains blocked until frontend implementation begins.

## Routes

- `/`
- `/login`
- `/invite/accept`
- `/home`
- `/conversations`
- `/conversations/[conversationId]`
- `/libraries`
- `/libraries/[workspaceId]`
- `/projects`
- `/projects/[workspaceId]`
- `/memories`
- `/uploads`
- `/settings`
- `/admin`

## Package Recommendations

Recommended package direction for the implementation milestone:

- Next.js
- TypeScript
- Tailwind CSS
- Radix UI primitives
- TanStack Query
- Zod
- React Hook Form only for forms that need structured validation and error handling
- one restrained icon package, such as Lucide
- Vitest
- Testing Library
- Playwright

Motion recommendation:
- prefer CSS-first motion;
- only introduce a lightweight motion package if implementation proves CSS alone is insufficient for state transitions.

Non-recommendations:
- no heavy component suites;
- no WebGL;
- no large animation runtimes by default.

## Exact File Boundaries

Quiet Orbit is the approved concept. For implementation, the structural boundary should be:

```text
frontend/
  app/
    (marketing)/
    (auth)/
    (app)/
      home/
      conversations/
      libraries/
      projects/
      memories/
      uploads/
      settings/
      admin/
  components/
    primitives/
    shell/
    navigation/
    feedback/
  features/
    assistant/
    conversations/
    citations/
    context-inspector/
    documents/
    uploads/
    memories/
    home/
    settings/
    admin/
  lib/
    api/
    config/
    accessibility/
    utils/
  styles/
    tokens.css
    globals.css
  tests/
    unit/
    integration/
    e2e/
  public/
    reserved/
```

## Route Groups

- `(marketing)`: reserved only if a future public-facing shell becomes necessary; not required for Milestone 4.
- `(auth)`: login and invite acceptance.
- `(app)`: authenticated shell and all application routes.

## Server / Client Boundaries

- Server-first:
  - route shells;
  - data-presenting pages where possible;
  - static settings and navigation structure;
  - source summaries and many card lists.
- Client-required:
  - message composer;
  - drawers and dialogs;
  - memory approval flows;
  - context inspector open/close logic;
  - upload interaction;
  - route-local optimistic UI where justified.

## Feature Folder Direction

- `assistant/`: orb, status labels, motion hooks.
- `conversations/`: thread, composer, follow-up suggestions.
- `citations/`: source summary, citation lists, source preview cards.
- `context-inspector/`: inspector, reason codes, incorrect-context controls.
- `documents/` and `uploads/`: document cards, upload flow, processing views.
- `memories/`: memory cards, approval, conflict review, history.
- `home/`: greeting, activity cards, usage summary.
- `settings/`: preference controls.
- `admin/`: invite-only admin surfaces.

## API Client

- Centralize backend access in `frontend/lib/api/`.
- Keep fetch wrappers thin and typed.
- Do not spread raw fetch calls across feature components.
- Keep authorization handling behind a future auth-aware boundary rather than inside visual components.

## Future Auth Boundary

- Reserve an auth boundary in the app shell that separates:
  - unauthenticated routes;
  - authenticated application routes;
  - administrator-only routes.
- UI components should consume resolved session state rather than owning token logic directly.

## Test Organization

- `tests/unit/`: component and utility behavior.
- `tests/integration/`: route-local flows, accessibility flows, state combinations.
- `tests/e2e/`: invitation, login handoff, upload, conversation, memory review, quota and error recovery.

## Asset Strategy

- Prefer CSS, inline icons, and lightweight SVG only when justified later.
- Do not require hero images, custom font files, or generated mockups.
- Decorative visual identity should come from tokens, gradients, borders, and layout rather than asset weight.

## Tokens

Quiet Orbit is the approved concept. Implementation must include semantic tokens equivalent to those in [Design System](./design-system.md), and the architecture must remain theme-ready for a later light-mode pass.

## Component Priorities

### Priority 1

- app shell
- primary nav
- page header
- assistant orb and label
- conversation thread
- message composer
- source summary bar
- citation list
- context inspector
- upload dropzone
- document card
- memory approval panel
- empty and error states

### Priority 2

- activity cards
- usage summary
- processing timeline
- memory center lists
- settings preferences
- offline banner

### Priority 3

- admin overview
- memory history detail
- advanced project-level context linking

## Responsive Rules

- Desktop: three-zone layout where helpful, with fixed left nav and optional right inspector.
- Tablet: collapsible nav, drawer inspector, fewer decorative layers.
- Mobile: full-width primary content, bottom nav, sheets for detail panels, larger touch targets.

## Accessibility Requirements

- WCAG 2.2 AA target.
- Keyboard-complete operation.
- Focus management for drawers and dialogs.
- Non-color differentiation for source types and statuses.
- Reduced-motion behavior.
- Text equivalents for assistant states and visual source links.
- Memory approval safeguards.

## Motion Requirements

Quiet Orbit is the approved concept. Implementation must obey the constraints and durations in [Assistant Identity and Motion](./assistant-identity-and-motion.md).

## Performance Budgets

Implementation must target the budgets in [Performance Strategy](./performance-strategy.md), including:
- unauthenticated JS under 170 KB gzip;
- authenticated shell JS under 260 KB gzip;
- LCP under 2.2 s desktop and 2.8 s mobile target;
- INP under 200 ms;
- CLS under 0.05.

## Tests

Implementation milestone should include:
- route rendering tests;
- component accessibility tests;
- keyboard navigation tests for inspector, drawers, and memory approval;
- reduced-motion behavior tests;
- source summary and citation rendering tests;
- end-to-end flows for login handoff, upload, conversation, citation inspection, memory approval, and error states.

## Non-Goals

- No public marketing site expansion.
- No theme-polishing beyond approved design direction.
- No custom illustration system.
- No heavy animation runtime.
- No experimental graph exploration interface.

## Acceptance Criteria

- Concept implementation matches the approved Milestone 3 concept.
- Routes follow the approved IA.
- Source transparency is visible in conversation flows.
- Memory approval and editing are clear and safe.
- Desktop, tablet, and mobile behaviors are implemented.
- Reduced motion works.
- Performance budgets are checked.
- No backend contracts are invented in the frontend docs milestone.

## Manual Verification

Quiet Orbit is the approved concept. Manual verification remains pending until implementation begins.

Later manual verification should include:
- first-time user journey;
- returning-user journey;
- citation inspection;
- memory approval and rejection;
- mobile conversation;
- reduced-motion mode;
- keyboard-only navigation;
- quota and unavailable states.

## User Approval Checklist

The user should explicitly approve:

1. the selected visual concept;
2. the home screen density and greeting behavior;
3. the mobile navigation model;
4. the assistant identity direction;
5. the memory approval interaction model;
6. the decision to keep implementation blocked until concept approval.
