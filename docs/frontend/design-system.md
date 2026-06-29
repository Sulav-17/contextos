# Design System Direction

Related documents:
- [Experience Concepts](./experience-concepts.md)
- [Layouts and Wireframes](./layouts-and-wireframes.md)
- [Accessibility Strategy](./accessibility-strategy.md)
- [Performance Strategy](./performance-strategy.md)

## Visual Direction

The recommended design system uses a near-black foundation with restrained blue-violet atmosphere, cyan intelligence accents, and warm-neutral signals for memory and governance states.

The goal is a private, immersive interface that still reads as practical software.

## Semantic Token Direction

```text
--surface-base
--surface-raised
--surface-overlay
--surface-inspector
--text-primary
--text-secondary
--text-muted
--accent-intelligence
--accent-memory
--accent-document
--accent-project
--status-success
--status-warning
--status-danger
--border-subtle
--border-strong
--focus-ring
--shadow-soft
--shadow-panel
--line-context
```

## Suggested Token Roles

- `--surface-base`: deep navy-black page field.
- `--surface-raised`: primary cards and conversation surfaces.
- `--surface-overlay`: drawers, dialogs, and elevated sheets.
- `--surface-inspector`: right-side context panel and bottom-sheet detail surfaces.
- `--text-primary`: off-white body and heading text.
- `--text-secondary`: slightly dimmed secondary labels.
- `--text-muted`: helper text and quiet metadata.
- `--accent-intelligence`: cyan accent for retrieval, assistant state, and analytical actions.
- `--accent-memory`: soft amber or warm neutral for memory review and approved memory indicators.
- `--accent-document`: cool blue for documents and citations.
- `--accent-project`: muted violet-blue for project grouping.
- `--status-success`: ready and verified states.
- `--status-warning`: pending review, quota thresholds, retryable conditions.
- `--status-danger`: failures, destructive actions, disabled states.
- `--border-subtle`: low-contrast structure lines.
- `--border-strong`: focused selection and active grouping.
- `--focus-ring`: high-contrast accessible ring for keyboard interaction.
- `--shadow-soft`: restrained depth for card separation.
- `--shadow-panel`: slightly stronger elevation for overlays.
- `--line-context`: sparse connected lines or dividers used as supplemental context cues.

## Typography Roles and Fallbacks

- Display: elegant serif or soft editorial headline style for welcome and section entry moments.
- Section heading: modern sans with strong weight and moderate tracking.
- Body: readable sans optimized for dense document and citation work.
- Metadata: smaller sans with clear numeric alignment.
- Monospace: used only for technical references or identifiers.

Fallback strategy:
- Headline: `"Iowan Old Style", "Palatino Linotype", Georgia, serif`
- UI sans: `"Aptos", "Segoe UI", "Helvetica Neue", Arial, sans-serif`
- Mono: `"Cascadia Code", "SFMono-Regular", Consolas, monospace`

No external font download is assumed in this milestone.

## Spacing

- Base spacing scale: 4, 8, 12, 16, 24, 32, 48, 64 px.
- Reading surfaces should favor 16 and 24 px interior spacing.
- Dense metadata areas may use 8 or 12 px spacing with clear separators.

## Radius

- Small controls: 10 px.
- Cards and panels: 18 to 24 px.
- Full-screen mobile sheets: 24 px top corners.
- The orb and circular status indicators are fully rounded.

## Borders

- Primary surfaces use subtle borders to preserve edge definition in dark themes.
- Active selection uses a stronger border or inset glow, never color alone.

## Shadows

- Shadows stay soft and shallow.
- Overlays may combine one soft shadow with one subtle border.
- Avoid heavy neon glows or deep stacked shadows.

## Focus Treatment

- All interactive elements need a clear visible focus ring.
- Focus uses both color and shape change.
- Context inspector items need a particularly strong focus outline because of dense content.

## Status Treatment

- Ready: icon + label + subtle success tint.
- Pending: icon + label + warning tint.
- Failed: icon + label + action hint.
- Superseded: neutral archived treatment plus history affordance.

## Source-Type Differentiation

- Documents: blue accent, file icon, citation blocks, page/excerpt metadata.
- Approved memories: warm accent, category pill, approval state, scope label.
- Conversation summary: neutral-violet summary card, clearly labeled as summary rather than raw message.
- Project context: cool violet grouping card with activity context.

No source type relies only on color. Each also uses iconography, labels, and structure.

## Icon Direction

- Thin to medium-stroke icons.
- Rounded edges preferred over sharp geometric aggression.
- Icons should feel precise, not playful or gamified.

## Future Light-Mode Strategy

Light mode should be possible later without changing information hierarchy:
- preserve semantic tokens rather than raw color names;
- keep contrast relationships strong;
- use soft grays and cool neutrals instead of stark white;
- ensure provenance, memory, and status remain structurally distinct.
