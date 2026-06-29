# Component Inventory

Related documents:
- [Information Architecture](./information-architecture.md)
- [Layouts and Wireframes](./layouts-and-wireframes.md)
- [Frontend Implementation Spec](./frontend-implementation-spec.md)

## Application Shell

### AppShell

- Purpose: shared page frame with navigation, header, main content, and contextual surface slots.
- Major states: authenticated, unauthenticated redirect, admin-visible, reduced-motion.
- Accessibility considerations: landmarks, skip links, focus restoration on route change.
- Server/client preference: server-first with client islands for interactive chrome.
- Reuse: all authenticated routes.
- Implementation priority: highest.

### PageHeader

- Purpose: route title, compact assistant status, actions, and search trigger.
- Major states: normal, compact mobile, loading, error.
- Accessibility considerations: heading ownership and action labeling.
- Server/client preference: mixed.
- Reuse: most routes.
- Implementation priority: highest.

## Navigation

### PrimaryNav

- Purpose: main section navigation.
- Major states: desktop rail, tablet compact rail, mobile bottom nav, admin-enabled.
- Accessibility considerations: current page semantics, keyboard order, touch target size.
- Server/client preference: client for responsive behavior with server-rendered structure.
- Reuse: all authenticated routes.
- Implementation priority: highest.

### ContextSwitcher

- Purpose: switch current library or project workspace context.
- Major states: idle, expanded, searching, empty.
- Accessibility considerations: combobox or listbox semantics.
- Server/client preference: client.
- Reuse: conversations, libraries, projects.
- Implementation priority: medium.

## Assistant Identity

### AssistantOrb

- Purpose: ambient assistant identity and state feedback.
- Major states: idle, reading, retrieving, thinking, error, unavailable.
- Accessibility considerations: paired text label and reduced-motion equivalent.
- Server/client preference: client-light or CSS-driven.
- Reuse: welcome, home, conversation.
- Implementation priority: high.

### AssistantStatusLabel

- Purpose: explicit readable state text.
- Major states: all assistant states.
- Accessibility considerations: live region behavior.
- Server/client preference: client.
- Reuse: header, conversation.
- Implementation priority: high.

## Conversation

### ConversationThread

- Purpose: render conversation messages and related answer states.
- Major states: empty, loading, populated, refusal, retryable error.
- Accessibility considerations: heading structure, live updates, citation reachability.
- Server/client preference: mixed.
- Reuse: conversation routes, project workspace.
- Implementation priority: highest.

### MessageComposer

- Purpose: collect user questions and follow-ups.
- Major states: idle, typing, sending, disabled, quota-blocked.
- Accessibility considerations: labeled input, send-state announcement, keyboard shortcuts.
- Server/client preference: client.
- Reuse: conversation routes.
- Implementation priority: highest.

### FollowUpSuggestionBar

- Purpose: present suggested next questions.
- Major states: hidden, visible, loading.
- Accessibility considerations: button labels and sensible tab order.
- Server/client preference: mixed.
- Reuse: conversation routes.
- Implementation priority: medium.

## Citations and Source Previews

### SourceSummaryBar

- Purpose: summarize what source classes were used in an answer.
- Major states: no sources, docs only, docs plus memories, summary included.
- Accessibility considerations: explicit text, not icon-only.
- Server/client preference: server-first.
- Reuse: conversation answers.
- Implementation priority: highest.

### CitationList

- Purpose: list cited source records.
- Major states: collapsed, expanded, loading previews.
- Accessibility considerations: button semantics, excerpt labels, page references.
- Server/client preference: mixed.
- Reuse: conversation and inspector.
- Implementation priority: highest.

### SourcePreviewCard

- Purpose: preview document excerpt, memory record, or summary item.
- Major states: document, memory, summary, unavailable.
- Accessibility considerations: clear labeling by source type.
- Server/client preference: mixed.
- Reuse: inspector, answer details, memory history.
- Implementation priority: high.

## Context Inspector

### ContextInspector

- Purpose: show detailed answer context without exposing chain-of-thought.
- Major states: closed, open, loading, unavailable.
- Accessibility considerations: keyboard drawer behavior, focus trap when overlaid.
- Server/client preference: client shell plus server-loaded content.
- Reuse: conversation and project workspaces.
- Implementation priority: highest.

### ReasonCodeList

- Purpose: show factual reasons for source selection.
- Major states: empty, populated, unavailable.
- Accessibility considerations: plain-language explanation and list semantics.
- Server/client preference: server-first.
- Reuse: context inspector.
- Implementation priority: high.

### IncorrectContextControl

- Purpose: let users flag or remove incorrect context influence.
- Major states: idle, dialog open, submitted, failed.
- Accessibility considerations: confirmation safeguards and descriptive copy.
- Server/client preference: client.
- Reuse: context inspector.
- Implementation priority: high.

## Documents and Uploads

### UploadDropzone

- Purpose: entry point for PDF upload.
- Major states: idle, drag, uploading, disabled, quota-blocked.
- Accessibility considerations: keyboard-operable alternative to drag and drop.
- Server/client preference: client.
- Reuse: home, libraries, uploads.
- Implementation priority: high.

### DocumentCard

- Purpose: represent a document and its current status.
- Major states: ready, processing, failed, deleted reference.
- Accessibility considerations: status text, non-color differentiation.
- Server/client preference: mixed.
- Reuse: libraries, home, uploads.
- Implementation priority: high.

### ProcessingTimeline

- Purpose: explain upload progress.
- Major states: queued, processing, ready, failed.
- Accessibility considerations: readable progress labels.
- Server/client preference: mixed.
- Reuse: uploads and libraries.
- Implementation priority: medium.

## Memory

### MemoryCard

- Purpose: display a memory record with category, source, scope, and status.
- Major states: pending, approved, rejected, superseded, expired.
- Accessibility considerations: approval safety, history access, label clarity.
- Server/client preference: mixed.
- Reuse: memory center, home.
- Implementation priority: high.

### MemoryApprovalPanel

- Purpose: approve, edit, or reject a memory suggestion.
- Major states: pending, conflict warning, duplicate warning, edited, confirmed.
- Accessibility considerations: confirmation flow and accidental activation prevention.
- Server/client preference: client.
- Reuse: conversation, memory center.
- Implementation priority: highest.

### MemoryHistoryView

- Purpose: show edits, supersession, and verification history.
- Major states: available, empty, loading.
- Accessibility considerations: timeline readability and descriptive changes.
- Server/client preference: mixed.
- Reuse: memory center.
- Implementation priority: medium.

## Home

### HomeHero

- Purpose: compact greeting and next best actions.
- Major states: first-time, returning, minimized.
- Accessibility considerations: skip or minimize options.
- Server/client preference: mixed.
- Reuse: home only.
- Implementation priority: high.

### ActivityCard

- Purpose: summarize recent documents, conversations, or project activity.
- Major states: normal, loading, empty.
- Accessibility considerations: heading and action clarity.
- Server/client preference: server-first.
- Reuse: home and projects.
- Implementation priority: high.

### UsageSummary

- Purpose: show storage and chat usage.
- Major states: normal, warning, limit reached.
- Accessibility considerations: explicit numeric labels and action hints.
- Server/client preference: server-first.
- Reuse: home and settings.
- Implementation priority: medium.

## Settings

### PreferencesForm

- Purpose: greeting, memory, motion, and theme preferences.
- Major states: pristine, dirty, saving, saved, failed.
- Accessibility considerations: grouped controls, error messaging, switch labels.
- Server/client preference: client.
- Reuse: settings.
- Implementation priority: medium.

## Admin

### AdminOverviewCard

- Purpose: summarize invite-only beta administration areas.
- Major states: normal, empty, loading.
- Accessibility considerations: clear separation of admin-only actions.
- Server/client preference: mixed.
- Reuse: admin.
- Implementation priority: low for Milestone 4 implementation planning, but documented now.

## Status and Feedback

### EmptyStatePanel

- Purpose: guide users when no relevant content exists.
- Major states: no docs, no memories, no conversations, no projects.
- Accessibility considerations: clear heading and primary action.
- Server/client preference: server-first.
- Reuse: many routes.
- Implementation priority: highest.

### ErrorStatePanel

- Purpose: show actionable, privacy-safe failures.
- Major states: retryable, quota, unavailable, forbidden.
- Accessibility considerations: alert semantics and recovery actions.
- Server/client preference: mixed.
- Reuse: many routes.
- Implementation priority: highest.

### OfflineBanner

- Purpose: indicate slow or unavailable network conditions.
- Major states: offline, reconnecting, recovered.
- Accessibility considerations: live region and dismissal behavior.
- Server/client preference: client.
- Reuse: app shell.
- Implementation priority: medium.

## Primitives

### Button

- Purpose: shared action control.
- Major states: primary, secondary, quiet, destructive, loading, disabled.
- Accessibility considerations: focus ring, loading label.
- Server/client preference: shared primitive.
- Reuse: universal.
- Implementation priority: highest.

### Card

- Purpose: shared container for raised surfaces.
- Major states: base, interactive, selected, warning.
- Accessibility considerations: heading ownership and border contrast.
- Server/client preference: shared primitive.
- Reuse: universal.
- Implementation priority: highest.

### Drawer

- Purpose: mobile and tablet contextual overlays.
- Major states: closed, open, loading.
- Accessibility considerations: dialog semantics and focus trap.
- Server/client preference: client.
- Reuse: inspector, settings, memory details.
- Implementation priority: high.
