import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { SimulationBackdrop } from "@/components/ambient/simulation-backdrop";

function mockMatchMedia({ reduced = false, coarse = false } = {}) {
  window.matchMedia = vi.fn((query: string) => ({
    matches:
      (query.includes("prefers-reduced-motion") && reduced) ||
      (query.includes("pointer: coarse") && coarse),
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
}

function mockCanvasContext() {
  const context = {
    arc: vi.fn(),
    beginPath: vi.fn(),
    clearRect: vi.fn(),
    fill: vi.fn(),
    fillRect: vi.fn(),
    lineTo: vi.fn(),
    moveTo: vi.fn(),
    setTransform: vi.fn(),
    stroke: vi.fn(),
    set fillStyle(_value: string) {},
    set lineWidth(_value: number) {},
    set shadowBlur(_value: number) {},
    set shadowColor(_value: string) {},
    set strokeStyle(_value: string) {},
  } as unknown as CanvasRenderingContext2D;

  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(context);
}

describe("SimulationBackdrop", () => {
  beforeEach(() => {
    mockMatchMedia();
    mockCanvasContext();
    vi.spyOn(window, "requestAnimationFrame").mockReturnValue(1);
    vi.spyOn(window, "cancelAnimationFrame").mockImplementation(() => undefined);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders one aria-hidden noninteractive simulation canvas", () => {
    render(<SimulationBackdrop />);

    const canvas = screen.getByTestId("simulation-canvas");
    expect(screen.getByTestId("simulation-backdrop")).toHaveAttribute("aria-hidden", "true");
    expect(canvas).toHaveAttribute("aria-hidden", "true");
    expect(canvas).toHaveClass("simulation-canvas");
    expect(canvas).toHaveStyle({ pointerEvents: "none" });
    expect(document.querySelectorAll("canvas")).toHaveLength(1);
  });

  it("runs the animation loop for normal motion users", () => {
    render(<SimulationBackdrop />);

    expect(window.requestAnimationFrame).toHaveBeenCalled();
  });

  it("does not run continuous animation for reduced-motion users", () => {
    mockMatchMedia({ reduced: true });
    render(<SimulationBackdrop />);

    expect(window.requestAnimationFrame).not.toHaveBeenCalled();
  });

  it("does not subscribe to pointer interaction for coarse pointers", () => {
    const addEventListener = vi.spyOn(window, "addEventListener");
    mockMatchMedia({ coarse: true });

    render(<SimulationBackdrop />);

    expect(addEventListener).not.toHaveBeenCalledWith(
      "pointermove",
      expect.any(Function),
      expect.anything(),
    );
  });
});
