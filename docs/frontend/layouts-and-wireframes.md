# Layouts and Wireframes

Related documents:
- [Information Architecture](./information-architecture.md)
- [Design System](./design-system.md)
- [Assistant Identity and Motion](./assistant-identity-and-motion.md)

## Layout Direction

The recommended Quiet Orbit concept uses a structured, low-clutter layout:

- Desktop: persistent left navigation, central work column, optional right context inspector.
- Tablet: collapsible navigation, central content, drawer-based inspector.
- Mobile: compact header, full-width primary content, bottom navigation, sheet-based inspector and review flows.

## Desktop Layout Rules

- Navigation width: 240 to 272 px.
- Main conversation width: 680 to 760 px for readable line length.
- Right inspector width: 320 to 380 px.
- Assistant identity: small and anchored near the conversation header, never centered as a hero once work begins.
- Atmosphere: static layered background and sparse connecting accents only around focus areas.

## Tablet Layout Rules

- Navigation collapses into a drawer or compact rail.
- Inspector becomes an overlay drawer.
- Decorative layers reduce to preserve space and performance.
- Touch-first controls gain larger hit targets and fewer simultaneous panels.

## Mobile Layout Rules

- Header stays compact and task-first.
- Chat and source information become stacked, not side-by-side.
- Source previews and context inspector become bottom sheets or full-screen detail views.
- Memory approval becomes a focused stepper card rather than a dense side panel.
- Safe-area padding is required for bottom navigation and sheets.

## Wireframe 1: First-Time Welcome

```text
+----------------------------------------------------------------------------------+
| ContextOS                                                Skip                     |
+----------------------------------------------------------------------------------+
|                                                                                  |
|   [ ambient orb ]                                                                |
|                                                                                  |
|   Welcome to your private knowledge space                                        |
|   Answers are grounded in your documents and visible context.                    |
|                                                                                  |
|   Sources ContextOS may use                                                     |
|   [ Documents ] [ Current conversation ] [ Approved memories only ]              |
|                                                                                  |
|   Memory control                                                                 |
|   Memory suggestions require approval before future use.                         |
|   [ Learn more ]                                                                 |
|                                                                                  |
|   Suggested first actions                                                        |
|   [ Upload your first PDF ]  [ Ask your first question ]                         |
|                                                                                  |
|   [ Continue to workspace ]                                                      |
|                                                                                  |
+----------------------------------------------------------------------------------+
```

## Wireframe 2: Returning-User Home

```text
+----------------------------------------------------------------------------------+
| Nav            Home                               Search            Profile       |
+----------------------------------------------------------------------------------+
| Home           Good evening, Sulav                                                  |
| Conversations  Pick up where you left off.                                          |
| Libraries      [ Continue conversation ] [ Upload PDF ] [ Review memories ]         |
| Projects                                                                         |
| Memories       Recent conversations         Active project        Pending memories   |
| Uploads        +----------------------+    +------------------+  +---------------+  |
| Settings       | Lease analysis Q&A   |    | Beta workspace   |  | 3 pending     |  |
|                | Used 4 docs, 1 mem   |    | 2 docs processing|  | 1 conflict    |  |
|                +----------------------+    +------------------+  +---------------+  |
|                                                                                  |
|                Recent documents              Usage                                |
|                +----------------------+    +----------------------------------+   |
|                | Contract.pdf Ready   |    | Storage 48 / 100 MB              |   |
|                | Notes.pdf Failed     |    | Chat 21 / 250 this month         |   |
|                +----------------------+    +----------------------------------+   |
+----------------------------------------------------------------------------------+
```

## Wireframe 3: Desktop Conversation with Context Inspector

```text
+------------------------------------------------------------------------------------------------+
| Nav                  Conversation: Lease Renewal                               Context Inspector |
+------------------------------------------------------------------------------------------------+
| Home                 [ orb ] Ready                                                              |
| Conversations        Used 3 document sources | Used 1 approved memory | Used conversation sum  |
| Libraries                                                                                      |
| Projects             User: Summarize the renewal risks.                                        |
| Memories                                                                                       |
| Uploads              Assistant:                                                                |
| Settings             The main risks are notice timing, rent escalation, and early termination. |
|                      [ Citation 1 ] [ Citation 2 ] [ Citation 3 ]                              |
|                      [ Memory used: tenant prefers concise executive summaries ]               |
|                                                                                 +------------+ |
|                      Follow-up suggestions                                      | Sources    | |
|                      [ Compare clauses ] [ Draft questions ]                    |------------| |
|                                                                                 | Documents  | |
|                      Composer                                                   | - Lease... | |
|                      [ Ask a follow-up...                           ][ Send ]   | - Addendum | |
|                                                                                 | Memories   | |
|                                                                                 | - Pref...  | |
|                                                                                 | Summary    | |
|                                                                                 | - Current  | |
|                                                                                 | Reason     | |
|                                                                                 | - matched  | |
|                                                                                 | Report bad | |
|                                                                                 +------------+ |
+------------------------------------------------------------------------------------------------+
```

## Wireframe 4: Mobile Conversation

```text
+--------------------------------------------------+
| <- Lease Renewal                  [ Sources ]    |
+--------------------------------------------------+
| [ orb ] Ready                                     |
| Used 3 docs | 1 approved memory                  |
|                                                   |
| User                                               |
| Summarize the renewal risks.                       |
|                                                   |
| Assistant                                          |
| The main risks are notice timing...                |
| [ View citations ] [ View context ]                |
|                                                   |
| Follow-ups                                         |
| [ Compare clauses ] [ Draft questions ]            |
|                                                   |
| [ Ask a follow-up...                    ][ Send ]  |
+--------------------------------------------------+
| Home | Conv | Libraries | Memories | More         |
+--------------------------------------------------+
```

## Wireframe 5: Library / Workspace

```text
+----------------------------------------------------------------------------------+
| Nav                  Library: Beta Workspace                   [ Upload PDF ]     |
+----------------------------------------------------------------------------------+
|                Filters: [ All ] [ Ready ] [ Processing ] [ Failed ]              |
|                                                                                  |
|                +----------------------+  +----------------------+                 |
|                | Lease.pdf            |  | Notes.pdf            |                 |
|                | Ready                |  | Failed processing    |                 |
|                | 42 pages             |  | Retry available      |                 |
|                | Open | Ask about it  |  | Inspect | Retry      |                 |
|                +----------------------+  +----------------------+                 |
|                                                                                  |
|                Recent processing                                                    |
|                [ Uploaded ] -> [ Queued ] -> [ Processing ] -> [ Ready ]         |
+----------------------------------------------------------------------------------+
```

## Wireframe 6: Upload and Processing

```text
+----------------------------------------------------------------------------------+
| Uploads                                                           [ New upload ] |
+----------------------------------------------------------------------------------+
| Queue                                                                            |
| +-------------------------------------------------------------------------------+ |
| | Contract.pdf      Processing text extraction         4 / 6 steps             | |
| | Keep working while we prepare this document for retrieval.                    | |
| +-------------------------------------------------------------------------------+ |
|                                                                                  |
| Recent failures                                                                   |
| +-------------------------------------------------------------------------------+ |
| | Scan.pdf         Failed: unsupported PDF content                              | |
| | Action: upload a text-based PDF or retry after replacing the file            | |
| +-------------------------------------------------------------------------------+ |
+----------------------------------------------------------------------------------+
```

## Wireframe 7: Memory Centre

```text
+----------------------------------------------------------------------------------+
| Memories                                      Search [.............]             |
+----------------------------------------------------------------------------------+
| Tabs: [ Pending ] [ Approved ] [ Superseded ] [ Rejected ]                      |
| Filters: Category | Workspace | Status | Sensitivity                            |
|                                                                                  |
| +-------------------------------------------------------------------------------+ |
| | Preference                                                                    | |
| | User prefers concise executive summaries                                      | |
| | Source: Conversation 2026-06-20  | Scope: Beta workspace                     | |
| | Status: Approved | Last verified: 2026-06-22                                  | |
| | Edit | History | Delete                                                      | |
| +-------------------------------------------------------------------------------+ |
+----------------------------------------------------------------------------------+
```

## Wireframe 8: Memory Approval

```text
+----------------------------------------------------------------------------------+
| Review memory suggestion                                                         |
+----------------------------------------------------------------------------------+
| Category suggestion: Preference                                                  |
| Candidate text: User prefers concise executive summaries.                        |
| Source: Conversation "Lease Renewal"                                             |
| Scope: Beta workspace                                                            |
|                                                                                  |
| Notes                                                                            |
| This memory is pending and is not used in future answers until approved.         |
|                                                                                  |
| [ Edit before approval ]                                                         |
| [ Approve ]   [ Reject ]   [ Dismiss for now ]                                   |
|                                                                                  |
| Possible conflict                                                                |
| Existing memory: User prefers detailed clause analysis.                          |
| [ Compare ]                                                                      |
+----------------------------------------------------------------------------------+
```

## Wireframe 9: Settings for Greeting, Memory, Motion, and Theme

```text
+----------------------------------------------------------------------------------+
| Settings                                                                         |
+----------------------------------------------------------------------------------+
| Preferences                                                                       |
| Greeting                                                                          |
| [x] Show compact personalized greeting                                            |
| [ ] Open directly to last conversation                                            |
|                                                                                  |
| Memory                                                                            |
| [x] Show memory suggestions                                                       |
| [ ] Pause all new memory suggestions                                              |
|                                                                                  |
| Motion                                                                            |
| [x] Standard motion                                                               |
| [ ] Reduced motion                                                                |
|                                                                                  |
| Theme                                                                             |
| [x] Dark atmospheric                                                              |
| [ ] Follow system                                                                 |
| Light mode strategy planned for later milestone                                   |
+----------------------------------------------------------------------------------+
```

## Wireframe 10: Admin Overview

```text
+----------------------------------------------------------------------------------+
| Admin                                                                            |
+----------------------------------------------------------------------------------+
| Beta access                                                                       |
| +----------------------+  +----------------------+  +--------------------------+  |
| | Invited users        |  | Pending invites      |  | Audit trail              |  |
| | 3 active             |  | 1 pending            |  | Latest admin actions     |  |
| +----------------------+  +----------------------+  +--------------------------+  |
|                                                                                  |
| Invitations                                                                       |
| [ Create invite ]   [ Disable account ]   [ View audit details ]                 |
+----------------------------------------------------------------------------------+
```

## Wireframe 11: Empty State

```text
+----------------------------------------------------------------------------------+
| Home                                                                             |
+----------------------------------------------------------------------------------+
|                                                                                  |
|   [ orb ]                                                                        |
|   Your knowledge space is ready.                                                 |
|   Upload a text-based PDF to start grounded conversations.                       |
|                                                                                  |
|   [ Upload your first PDF ]                                                      |
|   [ Learn how citations work ]                                                   |
|                                                                                  |
|   No documents yet | No conversations yet | No approved memories yet             |
|                                                                                  |
+----------------------------------------------------------------------------------+
```

## Wireframe 12: Insufficient-Evidence Refusal

```text
+----------------------------------------------------------------------------------+
| Conversation                                                                     |
+----------------------------------------------------------------------------------+
| Assistant                                                                        |
| I do not have enough supported evidence in your current authorized context       |
| to answer that confidently.                                                      |
|                                                                                  |
| What I checked                                                                    |
| - 2 document sources                                                             |
| - 0 approved memories                                                            |
| - current conversation summary                                                   |
|                                                                                  |
| Next actions                                                                      |
| [ Open cited sources ] [ Upload another document ] [ Rephrase question ]         |
+----------------------------------------------------------------------------------+
```
