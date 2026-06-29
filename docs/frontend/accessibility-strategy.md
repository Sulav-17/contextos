# Accessibility Strategy

Related documents:
- [Layouts and Wireframes](./layouts-and-wireframes.md)
- [Assistant Identity and Motion](./assistant-identity-and-motion.md)
- [Performance Strategy](./performance-strategy.md)

## Accessibility Standard

Frontend implementation should target WCAG 2.2 AA from the first coded milestone.

## Core Commitments

- No information relies only on color.
- Animation has text equivalents.
- Visual connections are supplemental.
- All workflows work without animation.
- The context inspector is keyboard accessible.
- Memory approval cannot be triggered accidentally.

## Semantic Structure

- Use clear landmarks: header, nav, main, aside, footer where appropriate.
- Use one clear page heading per route.
- Maintain heading hierarchy inside dense panels and cards.

## Keyboard Navigation

- All major flows must be fully operable by keyboard.
- The left navigation, conversation stream, source previews, context inspector, drawers, dialogs, and memory approval controls must have logical tab order.
- Citation expansion and source preview controls must be keyboard reachable and visibly focused.

## Focus Management

- Route changes move focus to the main heading or primary task anchor.
- Drawers and dialogs trap focus while open.
- Closing a drawer or dialog returns focus to the invoking control.
- Inline context inspector openings should not unexpectedly move focus unless user intent requires it.

## Dialogs and Drawers

- All drawers and dialogs need explicit titles.
- Escape closes non-destructive overlays.
- Destructive actions require confirmation with clear focus order.

## Screen-Reader Labels

- Assistant states announce with human-readable labels.
- Source summary bars must describe document count, approved memory count, and conversation summary usage.
- Memory approval actions must describe consequences:
  - approve for future use;
  - edit before approval;
  - reject and exclude from future use.

## Live Regions

- Use polite live regions for:
  - loading and retrieval state;
  - answer ready;
  - processing complete;
  - new pending memory suggestion.
- Use assertive live regions only for:
  - failures;
  - permission issues;
  - destructive confirmations;
  - dependency unavailable states.

## Accessible Loading States

- Loading states keep labels visible.
- Skeletons supplement, not replace, meaningful text.
- Long-running processing includes clear progress labels where known.

## Reduced Motion

- Respect `prefers-reduced-motion`.
- Provide an explicit in-product reduced-motion setting as well.
- Reduced-motion mode removes non-essential motion and decorative connection reveals.

## Contrast

- Text contrast must meet AA requirements for body, labels, metadata, and controls.
- Low-contrast atmospheric styling cannot be used for essential content.
- Focus outlines must remain visible against dark layered surfaces.

## Non-Color Source Labels

- Documents, memories, conversation summaries, and project context must each use:
  - text labels;
  - icons or shapes;
  - structured grouping.

## Error Handling

- Errors must be specific, privacy-safe, and actionable.
- Avoid raw backend detail, stack traces, or storage internals.
- Errors should answer:
  - what happened;
  - what the user can do next;
  - whether work was preserved.

## Touch Targets

- Minimum touch target: 44 x 44 px.
- Dense metadata rows on mobile must still preserve target size through padding or row-level actions.

## Skip Links

- Provide at least:
  - Skip to main content
  - Skip to conversation
  - Skip to context inspector, when present

## Timeout Behavior

- Avoid silent timeout expiration for important workflows.
- Long-running upload or review states should show persistence and recovery information.

## Mobile Accessibility

- Bottom navigation must be labeled and screen-reader friendly.
- Sheets must announce entry and exit cleanly.
- Gesture-only interactions are not allowed; every action needs a visible control.

## Future Testing Plan

Automated checks later:
- axe-based page checks;
- keyboard tab sequence smoke tests;
- reduced-motion regression checks;
- contrast checks in design review and implementation.

Manual checks later:
- screen-reader pass on key flows;
- keyboard-only pass on conversation and memory review;
- mobile accessibility pass with touch and zoom;
- low-vision review for provenance and source differentiation.
