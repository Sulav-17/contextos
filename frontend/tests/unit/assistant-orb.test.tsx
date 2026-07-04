import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AssistantOrb } from "@/components/assistant/assistant-orb";

describe("AssistantOrb", () => {
  it("exposes status text", () => {
    render(<AssistantOrb state="saving preference" />);
    expect(screen.getByRole("status")).toHaveTextContent("Assistant status: saving preference");
  });

  it("maps assistant states to visual orb states", () => {
    const { rerender } = render(<AssistantOrb state="idle" />);
    expect(screen.getByRole("status").querySelector(".assistant-orb")).toHaveAttribute(
      "data-state",
      "idle",
    );

    rerender(<AssistantOrb state="checking session" />);
    expect(screen.getByRole("status").querySelector(".assistant-orb")).toHaveAttribute(
      "data-state",
      "thinking",
    );

    rerender(<AssistantOrb state="ready" />);
    expect(screen.getByRole("status").querySelector(".assistant-orb")).toHaveAttribute(
      "data-state",
      "ready",
    );

    rerender(<AssistantOrb state="backend unavailable" reducedMotion />);
    const orb = screen.getByRole("status").querySelector(".assistant-orb");
    expect(orb).toHaveAttribute("data-state", "error");
    expect(orb).toHaveAttribute("data-reduced-motion", "true");
  });

  it("renders the static visible orb rings and core", () => {
    render(<AssistantOrb state="retrieving document" />);

    const orb = screen.getByRole("status").querySelector(".assistant-orb");
    expect(orb?.querySelector(".orb-ring-inner")).toBeInTheDocument();
    expect(orb?.querySelector(".orb-ring-outer")).toBeInTheDocument();
    expect(orb?.querySelector(".orb-core")).toBeInTheDocument();
    expect(orb?.querySelector(".orb-particle")).not.toBeInTheDocument();
    expect(orb).toHaveAttribute("data-state", "thinking");
  });
});
