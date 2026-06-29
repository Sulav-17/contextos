# Security Invariants

## Identity

1. Every user-owned resource has a deterministic authenticated owner.
2. Identity comes from a verified token.
3. Client-provided owner identifiers are not trusted.

## Application Authorization

4. Authorization occurs before data access.
5. Application code authorizes every read, update, download, and deletion.

## Row-Level Security

6. Row-Level Security is defense in depth, not a replacement for application authorization.

## Vector Retrieval

7. Vector search is tenant-filtered before ranking.
8. Permission filtering happens before ranking and response assembly.

## Object Storage

9. Storage is private and permission-checked.
10. Downloads require authorization and short-lived signed access where applicable.

## Workers

11. Workers revalidate resource ownership and state.
12. Workers revalidate deletion state and job eligibility before processing.

## Untrusted Document Content

13. The LLM never grants permissions.
14. Uploaded documents and retrieved text are untrusted data, not instructions.

## Memory Lifecycle

15. Memory candidates cannot influence answers before approval.
16. Deleted, expired, rejected, or superseded memories are excluded from current retrieval.

## Quotas

17. Quotas are concurrency-safe.

## Logging

18. Normal logs exclude raw private content and secrets.
19. Secrets, tokens, signed URLs, raw documents, full messages, and memory contents do not appear in normal logs.

## Deletion

20. Deleted documents are excluded from retrieval immediately.
21. Physical deletion of files and derived data is verified.

## Administration

22. Administrator actions are explicit and audited.
23. Administrative actions are permission-checked.

## Required Cross-User Tests

24. Automated tests will prove cross-user isolation.
25. Tests must prove one user cannot access another user’s resources.
