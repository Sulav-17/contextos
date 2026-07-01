import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ThemeControl } from "@/components/theme/theme-control";
import { ThemeProvider } from "@/components/theme/theme-provider";

function mockMatchMedia(matches = false) {
  window.matchMedia = vi.fn((query: string) => ({
    matches,
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
}

describe("ThemeControl", () => {
  beforeEach(() => {
    window.localStorage.clear();
    document.documentElement.removeAttribute("data-theme");
    document.documentElement.removeAttribute("data-appearance");
    mockMatchMedia(false);
  });

  it("persists selected appearance mode and applies the resolved theme", () => {
    render(
      <ThemeProvider>
        <ThemeControl />
      </ThemeProvider>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Light" }));

    expect(window.localStorage.getItem("contextos.appearance")).toBe("light");
    expect(document.documentElement.dataset.appearance).toBe("light");
    expect(document.documentElement.dataset.theme).toBe("light");
  });
});

