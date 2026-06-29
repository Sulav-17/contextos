# ADR 0004: Frontend Experience Direction

- Status: Accepted

## Context

ContextOS requires a complete frontend experience design package before any frontend code is implemented. The product must feel private, calm, technologically sophisticated, and trustworthy while preserving source transparency, memory controls, and accessibility.

The product brief and milestone rules require three materially distinct concepts, a recommendation, wireframes, responsive behavior, accessibility guidance, and performance planning before implementation may begin.

## Decision

Three concepts were developed:

- Quiet Orbit: a calm ambient workspace centered on a restrained assistant orb and layered conversational surfaces.
- Ledger Flow: a layered card and timeline experience emphasizing governed records, activity, and review states.
- Signal Constellation: a sparse connected-context interface using restrained node and line metaphors without becoming a graph product.

Recommended concept:

- Quiet Orbit

Borrowed ideas:

- from Ledger Flow: timeline-style event cards for processing and review-heavy moments;
- from Signal Constellation: sparse contextual linking cues inside inspector and project views only where they clarify provenance.

Rejected ideas:

- dense generic SaaS dashboards;
- full graph exploration as a primary mode;
- human avatars, mascots, or robotic assistant faces;
- constant pulsing and heavy ambient animation;
- WebGL-driven atmosphere.

Implementation remains blocked until frontend implementation begins.

## Alternatives Considered

- Choosing Ledger Flow as the primary direction:
  - stronger operational transparency;
  - weaker emotional warmth and higher risk of feeling administrative.
- Choosing Signal Constellation as the primary direction:
  - stronger distinctiveness and portfolio novelty;
  - higher clarity, accessibility, and implementation risk if overextended.
- Deferring concept choice and moving straight to implementation:
  - rejected because it would violate the milestone approval gate and weaken design coherence.

## Consequences

- The frontend has a clear design center before code is created.
- Quiet Orbit provides the strongest balance of trust, uniqueness, accessibility, and implementation feasibility.
- The documentation package gives the next milestone explicit route, layout, component, accessibility, and performance direction.
- Frontend implementation must remain paused until concept approval.

## Accessibility Implications

- The selected direction supports a strongly readable linear layout with optional contextual panels.
- All source relationships remain legible without relying on animation or visual lines.
- Assistant state changes always need text labels and reduced-motion equivalents.
- Memory approval remains deliberate and cannot be triggered accidentally.

## Performance Implications

- Quiet Orbit avoids high-risk rendering patterns such as dense animated graphs or WebGL.
- The design still requires discipline around blur, overlays, and deferred secondary panels.
- The documentation package defines measurable bundle and Core Web Vitals targets for later implementation.

## Future Migration Path

- User has approved Quiet Orbit from Milestone 3.
- Milestone 4 begins implementation using the blocked implementation spec as the canonical frontend plan.
- Borrowed timeline and contextual-linking ideas may be introduced selectively after the core shell is stable.
- A future light-mode variant can be added by extending semantic tokens rather than redesigning structure.
