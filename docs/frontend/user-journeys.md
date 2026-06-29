# User Journeys

Related documents:
- [Experience Concepts](./experience-concepts.md)
- [Information Architecture](./information-architecture.md)
- [Layouts and Wireframes](./layouts-and-wireframes.md)

## Journey Principles

- Users should reach useful work quickly.
- Privacy, retrieval, and memory rules must be understandable early.
- Greeting and guidance are helpful but skippable.
- Sources remain visibly distinct: documents, approved memories, and conversation summary never collapse into one ambiguous bucket.

## First-Time User Journey

### 1. Invitation acceptance

- The user opens `/invite/accept`.
- The page confirms invite validity, who invited them, and what ContextOS is for in one short paragraph.
- The primary action is "Continue securely".
- If the invitation is expired, the user gets a specific action path instead of a dead end.

### 2. Authentication handoff

- The user is handed to the approved authentication flow.
- Context is preserved so they return to the invite flow instead of landing in a generic login page.
- The UI shows a compact "Secure sign-in" explanation, not marketing copy.

### 3. Short welcome

- After authentication, the user sees a skippable welcome panel.
- It explains three truths:
  - answers come from your documents and current context;
  - memory suggestions require approval before future use;
  - you can inspect and correct what ContextOS used.

### 4. What ContextOS remembers and retrieves

- The welcome panel includes a simple source model:
  - Documents: uploaded evidence.
  - Conversation summary: continuity inside the current thread.
  - Approved memories: only after review.

### 5. Privacy and memory controls

- The user can open a short "How memory works" drawer.
- They see approve, edit, reject, and disable options before any suggestion is shown later.
- Memory never feels silently enabled.

### 6. Suggested first actions

- The interface presents three clear next steps:
  - Upload your first PDF
  - Ask a question after upload
  - Explore memory controls

### 7. Workspace entry

- The user enters `/home`.
- The page focuses on one primary upload action, one explanation of the empty state, and one recent activity region.
- The greeting is visible but not dominant.

### 8. First upload

- The user selects a PDF from the upload panel or the library empty state.
- Constraints are visible: text PDF only, max size, and quota context.
- The upload view explains that processing happens before the file becomes searchable.

### 9. Processing state

- The uploaded document appears immediately in a visible processing list.
- Status labels are explicit: Uploaded, Queued, Processing, Ready, Failed.
- The user can leave the page without losing awareness of the job.

### 10. First question

- Once a document is ready, the user can open a suggested prompt or type their own question.
- The conversation view shows a small explanation of how sources will appear.

### 11. Citation inspection

- The first answer includes a visible source summary and expandable citations.
- The user can inspect excerpts and source records in the context inspector.

### 12. First memory suggestion

- After a relevant conversation, a small non-blocking prompt surfaces a memory candidate.
- The candidate is clearly marked as pending and not in use.

### 13. Approve, edit, or reject

- The user can:
  - approve as suggested;
  - edit content, category, or scope before approval;
  - reject with optional reason.

### 14. Return to the workspace

- After decision, the user returns to the same conversation or home context.
- A brief confirmation explains what changed:
  - Approved memory will be eligible for future retrieval.
  - Rejected memory will not be used.

## Returning User Journey

### Entry pattern

- Returning users land on `/home` by default.
- If they used a deep link, the greeting collapses and the target view opens directly.
- The greeting is minimized by default, with a settings control to restore the full greeting or open directly into the workspace.

### Fast useful work

- The top of `/home` shows:
  - a compact personalized greeting;
  - continue recent conversation;
  - active project snapshot;
  - pending memory suggestions;
  - recent documents and processing state;
  - usage summary.

### Continue recent conversation

- The user can resume the most recent active conversation from the home hero or recent list.
- The conversation opens with the source summary and context inspector available immediately.

### Open active project

- A project card shows active documents, recent thread, and pending items.
- One tap opens the project-specific workspace.

### Inspect recently processed documents

- Recent uploads show whether they are ready, failed, or still processing.
- The user can jump directly to the related library or retry view.

### Review pending memories

- Pending memory suggestions appear as an actionable queue, not a passive badge.
- The user can triage them from home or open the full memory center.

### See usage

- Storage and chat usage appear in a compact status strip with thresholds and next-action guidance.

### Skip greeting

- Greeting can be permanently minimized in settings.
- The minimized state still preserves a lightweight personal touch without consuming vertical space.

### Open directly into workspace

- The user can pin a preferred landing page in settings:
  - Home
  - Conversations
  - Projects
  - Libraries

### Resume after ingestion failure

- If a document failed processing, home shows a specific failure card with retry or inspect action.
- The user does not need to dig through logs or status pages.

### Understand superseded memory

- If a memory was replaced, the returning user sees the active memory and a clear superseded marker with history access.
- The language explains that superseded memories are excluded from current retrieval.

## System States

### No documents

- The user sees a calm empty state with one upload action and one explanation of how documents become searchable.

### No conversations

- The user sees suggested first prompts and an explanation that conversations persist once started.

### No memories

- The memory center explains that approved memories will appear only after review.

### Processing

- Upload and document views show status labels and preserve the ability to keep working elsewhere.

### Failed ingestion

- The UI states what failed in privacy-safe terms and gives a retry or replacement action.

### Retryable failure

- The user gets a single recommended next step and reassurance that existing content is unaffected.

### Backend unavailable

- The user sees a service unavailable state with retry guidance and no leaked infrastructure details.

### Storage quota reached

- Upload actions disable with an explicit quota explanation and next-step guidance.

### Chat quota reached

- The composer disables with quota text, current usage, and reset timing where available.

### Memory limit reached

- Memory approval explains the limit and offers review or cleanup actions before approval continues.

### Expired invitation

- The invite route explains expiration and directs the user to request a fresh invite.

### Disabled account

- The login or app-entry route explains that access is disabled and points to support or the inviter path.

### Insufficient evidence

- The assistant refuses clearly, states what source classes were checked, and offers next actions.

### Old conversation referencing deleted source

- The conversation shows that a previously cited source is no longer available and that current retrieval excludes deleted data.

### Reduced-motion mode

- Decorative motion is removed, assistant-state changes become label-based, and all workflows remain intact.

### Offline or slow network

- An inline banner explains degraded connectivity, whether work is preserved, and when retry is available.
