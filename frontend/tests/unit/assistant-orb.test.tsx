import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AssistantOrb } from "@/components/assistant/assistant-orb";

describe("AssistantOrb", () => {
  it("exposes status text", () => {
    render(<AssistantOrb state="saving preference" />);
    expect(screen.getByRole("status")).toHaveTextContent("Assistant status: saving preference");
  });
});
