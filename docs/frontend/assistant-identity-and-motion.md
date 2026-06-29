# Assistant Identity and Motion

Related documents:
- [Experience Concepts](./experience-concepts.md)
- [Layouts and Wireframes](./layouts-and-wireframes.md)
- [Accessibility Strategy](./accessibility-strategy.md)
- [Performance Strategy](./performance-strategy.md)

## Assistant Identity Recommendation

Use a restrained ambient orb.

Why this identity:
- it feels personal without pretending to be human;
- it supports calmness and trust;
- it can express system state with minimal motion;
- it scales from welcome view to compact conversation header;
- it works in reduced-motion mode as a static symbol plus text label.

## Identity Rules

- No face, avatar, mascot, or character language.
- No constant pulsing.
- No particle storm, sparkles, or decorative flares.
- The orb is a small symbolic presence, not the dominant interface object.

## Assistant States

### Idle

- Visual: stable orb with faint edge light.
- Text label: `Ready`.
- Screen reader: no live announcement.
- Reduced-motion equivalent: static orb and label only.
- Stale-state behavior: after long inactivity, label remains `Ready`, no animation resumes automatically.

### Listening

- Visual: brief widening ring around the orb.
- Text label: `Listening`.
- Screen reader: polite live region when voice or dictation support is present later.
- Reduced-motion equivalent: label change only.
- Stale-state behavior: revert to idle if no input begins.

### Retrieving documents

- Visual: cool cyan segmented ring appears once.
- Text label: `Checking document sources`.
- Screen reader: polite live region announcement.
- Reduced-motion equivalent: static document icon next to label.
- Stale-state behavior: if retrieval takes too long, label becomes `Still checking document sources`.

### Retrieving memories

- Visual: warmer secondary ring layered beneath the cyan ring.
- Text label: `Checking approved memories`.
- Screen reader: polite live region announcement.
- Reduced-motion equivalent: memory badge plus text.
- Stale-state behavior: shifts to `Still checking approved memories` when delayed.

### Reading

- Visual: subtle downward sweep through the orb.
- Text label: `Reading sources`.
- Screen reader: polite live region announcement.
- Reduced-motion equivalent: label only.
- Stale-state behavior: escalate to `Reading sources, this is taking longer than usual`.

### Thinking

- Visual: brief low-amplitude glow shift.
- Text label: `Preparing a grounded answer`.
- Screen reader: polite live region announcement once.
- Reduced-motion equivalent: static status chip.
- Stale-state behavior: `Still preparing an answer`.

### Preparing answer

- Visual: orb sharpens and ring resolves.
- Text label: `Finalizing response`.
- Screen reader: no repeated announcements.
- Reduced-motion equivalent: label update only.
- Stale-state behavior: reverts to delayed copy if necessary.

### Waiting for memory approval

- Visual: small warm badge appears beside the orb.
- Text label: `Memory suggestion awaiting review`.
- Screen reader: polite announcement when suggestion appears.
- Reduced-motion equivalent: static badge and text.
- Stale-state behavior: badge persists until acted on or dismissed.

### Completed

- Visual: single soft settle transition.
- Text label: `Answer ready`.
- Screen reader: polite live region if the user is focused in the conversation stream.
- Reduced-motion equivalent: no transition, only label.
- Stale-state behavior: returns to idle after answer renders.

### Error

- Visual: border shifts to a restrained warning or error edge.
- Text label: `Something went wrong`.
- Screen reader: assertive alert with actionable text.
- Reduced-motion equivalent: static error indicator.
- Stale-state behavior: error remains until dismissed or retried.

### Dependency unavailable

- Visual: muted orb with broken-link status chip.
- Text label: `Service unavailable`.
- Screen reader: assertive alert with specific safe wording.
- Reduced-motion equivalent: label and status icon only.
- Stale-state behavior: remains visible until services recover or the user retries.

## Motion System

### Duration categories

- Immediate feedback: 80 to 120 ms.
- Small reveal/hide: 140 to 180 ms.
- Panel transitions: 180 to 220 ms.
- Route-level transitions: 180 to 240 ms.
- Error or status settle: under 160 ms.

### Easing categories

- Enter: soft ease-out.
- Exit: slightly faster ease-in.
- Emphasis: one restrained standard ease, not bounce.

### Route transitions

- Use opacity and small vertical shifts only.
- No full-screen wipes.
- No transition should delay interaction availability.

### Loading behavior

- Prefer skeleton text blocks and reserved layout space.
- One animated region at a time in the conversation area.
- Loading text remains visible even when motion is disabled.

### Context-panel expansion

- Desktop: slide-fade from right in 180 to 220 ms.
- Mobile: bottom sheet with upward reveal in 180 to 220 ms.
- Reduced motion: instant open/close with no movement.

### Assistant-state transitions

- State changes are subtle and localized to the assistant identity and its label.
- They should never cause layout shift.

### Maximum simultaneous animated regions

- Desktop: 3
- Tablet: 2
- Mobile: 2

These include route transitions, assistant state, loading skeleton shimmer, and panel reveal.

### Reduced-motion substitutions

- Replace motion with:
  - icon swaps;
  - label changes;
  - opacity-only state changes when needed;
  - instant panel open/close.

### Mobile simplification

- Remove decorative connection lines.
- Reduce or eliminate background animation.
- Keep only task-critical transitions.

### Motion prohibitions

- No constant floating.
- No constant pulsing.
- No cinematic intros.
- No blocking transitions before content.
- No heavy parallax.
- No 3D camera movement.
