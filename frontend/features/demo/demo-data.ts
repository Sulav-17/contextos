export type DemoDocument = {
  id: string;
  name: string;
  pages: number;
  status: "Ready";
  summary: string;
};

export type DemoCitation = {
  id: string;
  documentId: string;
  documentName: string;
  pageNumber: number;
  excerpt: string;
};

export type DemoAnswer = {
  id: string;
  question: string;
  answer: string;
  citations: DemoCitation[];
  memoryIds: string[];
};

export type DemoConversationEntry = {
  id: string;
  title: string;
  preview: string;
  sourceLabel: string;
};

export type DemoMemory = {
  id: string;
  type: "preference" | "goal" | "project";
  content: string;
  source: string;
};

export const demoDocuments: DemoDocument[] = [
  {
    id: "demo-doc-renewal-brief",
    name: "Quiet Harbor Lease Summary.pdf",
    pages: 9,
    status: "Ready",
    summary: "A fictional lease summary with renewal, notice, and maintenance clauses.",
  },
  {
    id: "demo-doc-research-notes",
    name: "Orchard Lab Research Notes.pdf",
    pages: 14,
    status: "Ready",
    summary: "A fictional research memo about survey findings and decision criteria.",
  },
  {
    id: "demo-doc-project-plan",
    name: "Northstar Project Plan.pdf",
    pages: 11,
    status: "Ready",
    summary: "A fictional project plan with milestones, risks, and owner notes.",
  },
];

export const demoMemories: DemoMemory[] = [
  {
    id: "demo-memory-citations",
    type: "preference",
    content: "Prefers answers that separate document evidence from remembered context.",
    source: "Approved from fictional onboarding conversation",
  },
  {
    id: "demo-memory-northstar",
    type: "project",
    content: "Northstar review should focus on renewal timing, budget risk, and launch readiness.",
    source: "Approved from fictional planning note",
  },
  {
    id: "demo-memory-review",
    type: "goal",
    content: "Wants a short review checklist before making portfolio decisions.",
    source: "Approved manually in this fictional demo workspace",
  },
];

export const demoAnswers: DemoAnswer[] = [
  {
    id: "demo-answer-renewal-notice",
    question: "What renewal notice does the lease require?",
    answer:
      "The fictional lease summary says renewal notice should be sent at least 60 days before the current term ends. It also says the notice should identify the requested renewal term and be sent through the tenant portal or certified mail.",
    memoryIds: ["demo-memory-citations"],
    citations: [
      {
        id: "demo-citation-renewal-1",
        documentId: "demo-doc-renewal-brief",
        documentName: "Quiet Harbor Lease Summary.pdf",
        pageNumber: 4,
        excerpt:
          "Renewal requests must be delivered no fewer than 60 days before the end of the current term.",
      },
      {
        id: "demo-citation-renewal-2",
        documentId: "demo-doc-renewal-brief",
        documentName: "Quiet Harbor Lease Summary.pdf",
        pageNumber: 5,
        excerpt:
          "Accepted delivery channels are the tenant portal or certified mail with the renewal term stated clearly.",
      },
    ],
  },
  {
    id: "demo-answer-research-findings",
    question: "What did the research notes identify as the top finding?",
    answer:
      "The fictional research notes identify reliability as the strongest signal. Participants valued consistent retrieval and clear source labels more than speed alone.",
    memoryIds: ["demo-memory-citations"],
    citations: [
      {
        id: "demo-citation-research-1",
        documentId: "demo-doc-research-notes",
        documentName: "Orchard Lab Research Notes.pdf",
        pageNumber: 6,
        excerpt:
          "Reliability ranked above speed when participants evaluated whether they trusted an answer.",
      },
      {
        id: "demo-citation-research-2",
        documentId: "demo-doc-research-notes",
        documentName: "Orchard Lab Research Notes.pdf",
        pageNumber: 7,
        excerpt:
          "Source labels and inspectable excerpts were the most frequently requested trust cues.",
      },
    ],
  },
  {
    id: "demo-answer-project-risks",
    question: "Which project risks should I review first?",
    answer:
      "For the fictional Northstar plan, review the launch-readiness checklist first, then the budget dependency and the unresolved vendor timeline. The prepared memory nudges the answer toward renewal timing, budget risk, and launch readiness.",
    memoryIds: ["demo-memory-northstar", "demo-memory-review"],
    citations: [
      {
        id: "demo-citation-project-1",
        documentId: "demo-doc-project-plan",
        documentName: "Northstar Project Plan.pdf",
        pageNumber: 3,
        excerpt:
          "Launch readiness depends on checklist completion, budget confirmation, and vendor timeline closure.",
      },
      {
        id: "demo-citation-project-2",
        documentId: "demo-doc-project-plan",
        documentName: "Northstar Project Plan.pdf",
        pageNumber: 8,
        excerpt:
          "The budget dependency remains open until the finance review signs off on the revised estimate.",
      },
    ],
  },
  {
    id: "demo-answer-memory-use",
    question: "How does ContextOS show memory use?",
    answer:
      "This guided demo shows memory as a separate source type. Fictional approved memories appear next to document citations so remembered context is visible and not treated as document evidence.",
    memoryIds: ["demo-memory-citations", "demo-memory-review"],
    citations: [
      {
        id: "demo-citation-memory-1",
        documentId: "demo-doc-research-notes",
        documentName: "Orchard Lab Research Notes.pdf",
        pageNumber: 10,
        excerpt:
          "Participants asked for document evidence and remembered preferences to be labeled separately.",
      },
    ],
  },
];

export const demoConversationEntries: DemoConversationEntry[] = [
  {
    id: "demo-conversation-renewal",
    title: "Lease renewal review",
    preview: "Asked about renewal notice timing and delivery method.",
    sourceLabel: "2 document citations",
  },
  {
    id: "demo-conversation-research",
    title: "Research trust signals",
    preview: "Compared reliability, speed, and source-label findings.",
    sourceLabel: "2 document citations",
  },
  {
    id: "demo-conversation-northstar",
    title: "Northstar risk check",
    preview: "Reviewed launch readiness, budget dependency, and approved memory context.",
    sourceLabel: "2 memories + 2 citations",
  },
];

export function findPreparedAnswer(question: string): DemoAnswer | null {
  const normalized = normalizeQuestion(question);
  return (
    demoAnswers.find((answer) => normalizeQuestion(answer.question) === normalized) ?? null
  );
}

function normalizeQuestion(question: string): string {
  return question.trim().replace(/\s+/g, " ").toLowerCase();
}
