import { readFileSync } from "node:fs";
import { join } from "node:path";

import { fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import DemoPage from "@/app/demo/page";
import { DemoWorkspace } from "@/features/demo/demo-workspace";

vi.mock("@/components/theme/theme-control", () => ({
  ThemeControl: () => <div>Theme control</div>,
}));

describe("DemoWorkspace", () => {
  const fetchSpy = vi.fn();

  beforeEach(() => {
    fetchSpy.mockReset();
    vi.stubGlobal("fetch", fetchSpy);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the demo route as a public fictional interactive demo", () => {
    render(<DemoPage />);

    expect(screen.getByRole("heading", { name: /Explore ContextOS/i })).toBeInTheDocument();
    expect(screen.getByText("Demo Mode")).toBeInTheDocument();
    expect(screen.getByText("Interactive Demo")).toBeInTheDocument();
    expect(
      screen.getByText(
        "This guided demo uses fictional sample data and prepared responses. It does not access real user accounts, documents, or live AI services.",
      ),
    ).toBeInTheDocument();
    expect(screen.queryAllByRole("link")).toHaveLength(0);
    expect(screen.queryByRole("button", { name: /log in/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /create account/i })).not.toBeInTheDocument();
  });

  it("uses suggested questions as deterministic primary interactions with citations", () => {
    render(<DemoWorkspace />);

    fireEvent.click(
      screen.getByRole("button", {
        name: "What did the research notes identify as the top finding?",
      }),
    );

    expect(screen.getByText(/reliability as the strongest signal/i)).toBeInTheDocument();
    const conversation = screen.getByTestId("demo-conversation");
    expect(
      within(conversation).getByText("[1] Orchard Lab Research Notes.pdf, page 6"),
    ).toBeInTheDocument();
    expect(
      within(conversation).getByText(
        "Reliability ranked above speed when participants evaluated whether they trusted an answer.",
      ),
    ).toBeInTheDocument();
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("maps recognized composer questions and rejects unsupported questions honestly", () => {
    render(<DemoWorkspace />);

    fireEvent.change(screen.getByLabelText("Try a prepared sample question"), {
      target: { value: "Which project risks should I review first?" },
    });
    fireEvent.submit(screen.getByRole("button", { name: /show prepared answer/i }).closest("form")!);

    expect(screen.getByText(/review the launch-readiness checklist first/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Try a prepared sample question"), {
      target: { value: "Can you answer any arbitrary question?" },
    });
    fireEvent.submit(screen.getByRole("button", { name: /show prepared answer/i }).closest("form")!);

    expect(
      screen.getByText(/currently supports the provided sample questions/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/No network request or live AI call was made/i)).toBeInTheDocument();
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("resets local component state without touching browser storage", () => {
    window.sessionStorage.setItem("unrelated", "keep");
    window.localStorage.setItem("unrelated", "keep");
    render(<DemoWorkspace />);

    fireEvent.click(
      screen.getByRole("button", {
        name: "How does ContextOS show memory use?",
      }),
    );
    expect(screen.getByText(/memory as a separate source type/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /reset demo/i }));

    expect(screen.getByText(/Demo reset to the initial prepared example/i)).toBeInTheDocument();
    expect(screen.getByText(/renewal notice should be sent/i)).toBeInTheDocument();
    expect(window.sessionStorage.getItem("unrelated")).toBe("keep");
    expect(window.localStorage.getItem("unrelated")).toBe("keep");
  });

  it("renders demo-prefixed fictional records and keyboard-reachable controls", () => {
    const { container } = render(<DemoWorkspace />);

    expect(screen.getAllByText(/fictional/i).length).toBeGreaterThan(3);
    expect(screen.getByText("Quiet Harbor Lease Summary.pdf")).toBeInTheDocument();
    expect(screen.getByText("Orchard Lab Research Notes.pdf")).toBeInTheDocument();
    expect(screen.getByText("Northstar Project Plan.pdf")).toBeInTheDocument();
    expect(screen.getAllByRole("button").every((button) => button.tabIndex !== -1)).toBe(true);
    expect(screen.getAllByText(/approved/i).length).toBeGreaterThanOrEqual(3);
    expect(container.textContent).toContain("No live AI call");
  });

  it("keeps the demo layout mobile-safe at 390px", () => {
    Object.defineProperty(window, "innerWidth", { configurable: true, value: 390 });
    const { container } = render(<DemoWorkspace />);

    expect(container.querySelector('[data-app-shell="public"]')).toHaveClass("overflow-x-hidden");
    expect(container.querySelector(".xl\\:grid-cols-\\[18rem_minmax\\(0\\,1fr\\)_21rem\\]")).toBeTruthy();
    expect(container.querySelector("canvas")).not.toBeInTheDocument();
  });
});

describe("demo import boundary", () => {
  const demoFiles = [
    "app/demo/page.tsx",
    "features/demo/demo-workspace.tsx",
    "features/demo/demo-data.ts",
  ];
  const forbidden = [
    '"use server"',
    "@/lib/api",
    "@/lib/supabase",
    "@/features/conversations/actions",
    "@/features/documents/actions",
    "@/features/memories/actions",
    "CONTEXTOS_API_URL",
    "/api/v1",
    "createSupabase",
    "Supabase",
    "tenant_context",
    "fetch(",
  ];

  it("does not import authenticated data, server actions, Supabase, or backend URLs", () => {
    for (const file of demoFiles) {
      const source = readFileSync(join(process.cwd(), file), "utf8");
      for (const marker of forbidden) {
        expect(source, `${file} must not contain ${marker}`).not.toContain(marker);
      }
    }
    expect(readFileSync(join(process.cwd(), "features/demo/demo-data.ts"), "utf8")).toContain(
      "demo-",
    );
  });
});
