# Performance Strategy

Related documents:
- [Assistant Identity and Motion](./assistant-identity-and-motion.md)
- [Design System](./design-system.md)
- [Frontend Implementation Spec](./frontend-implementation-spec.md)

## Performance Position

These are design-stage acceptance targets, not measured results. The frontend should feel immediate on modern laptops and usable on mid-range mobile devices without relying on heavy runtimes or background media.

## Measurable Budgets

- Unauthenticated initial JavaScript: target under 170 KB gzip.
- Authenticated shell JavaScript: target under 260 KB gzip before route-specific features.
- Route-specific secondary panel JavaScript: target under 80 KB gzip per deferred panel.
- Largest Contentful Paint:
  - desktop target under 2.2 s on good broadband;
  - mobile target under 2.8 s on mid-range emulation.
- Interaction to Next Paint:
  - target under 200 ms for primary actions;
  - stretch target under 150 ms for route-local interactions.
- Cumulative Layout Shift: target under 0.05.
- Route transitions: visible shell response within 150 ms, full route content under 300 ms when data is ready.
- Animation frame rate: 55 to 60 FPS for approved transitions on supported hardware.
- Image or SVG weight: no decorative hero image required; any inline SVG accent should stay under 20 KB per route region.
- Font loading: system and local fallback first; no blocking remote font dependency for milestone implementation.
- Mobile memory pressure: keep initial rendered home and conversation shells within practical defaults by deferring inspector-heavy sections.
- Reduced-data behavior: no autoplay media, no large background assets, and optional decorative lines disabled when data-saving mode is later detected.

## Implementation Preferences

- Prefer React Server Components where suitable.
- Use route-level loading and streaming where it improves perceived performance.
- Dynamically load the context inspector, memory history panels, and admin-only interfaces.
- Prefer CSS and lightweight SVG over canvas or heavy runtime effects.
- Keep client state minimal and local to interaction-heavy features.
- Avoid large animation libraries unless CSS-only motion is clearly insufficient.
- Do not use WebGL or autoplay video.
- Do not use large background images.

## How Budgets Will Be Measured Later

- Bundle size: Next.js build analysis and route chunk inspection.
- LCP, INP, CLS: Lighthouse, Web Vitals reporting, and browser performance traces.
- Route transitions: browser performance markers and interaction timing checks.
- Frame rate: DevTools performance recording on representative devices.
- Reduced-motion and reduced-data behavior: manual settings checks and browser emulation.

## Risk Areas to Watch

- overuse of blur and layered transparency;
- too many client-only interactive panels at once;
- heavy citation preview rendering in large conversations;
- dense memory and upload lists without virtualization or pagination;
- motion libraries expanding the base bundle without clear value.
