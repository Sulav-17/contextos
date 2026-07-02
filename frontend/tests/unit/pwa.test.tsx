import { readFileSync } from "node:fs";
import { join } from "node:path";

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import manifest from "@/app/manifest";
import { clearPrivateClientState } from "@/components/auth/client-state";
import { InstallControl } from "@/components/pwa/install-control";
import { OfflineStatus } from "@/components/pwa/offline-status";
import { ServiceWorkerRegistration } from "@/components/pwa/service-worker-registration";

function setOnline(value: boolean) {
  Object.defineProperty(navigator, "onLine", {
    configurable: true,
    value,
  });
}

describe("PWA foundation", () => {
  it("defines installable ContextOS manifest metadata", () => {
    const data = manifest();

    expect(data.name).toBe("ContextOS");
    expect(data.short_name).toBe("ContextOS");
    expect(data.start_url).toBe("/home");
    expect(data.display).toBe("standalone");
    expect(data.icons?.some((icon) => icon.purpose === "maskable")).toBe(true);
    expect(data.icons?.map((icon) => icon.sizes)).toEqual(
      expect.arrayContaining(["192x192", "512x512", "180x180"]),
    );
  });

  it("captures the browser install prompt and reports installed state", async () => {
    window.matchMedia = vi.fn().mockReturnValue({ matches: false });
    render(<InstallControl />);

    const prompt = vi.fn().mockResolvedValue(undefined);
    const event = new Event("beforeinstallprompt") as Event & {
      prompt: () => Promise<void>;
      userChoice: Promise<{ outcome: "accepted"; platform: string }>;
    };
    event.prompt = prompt;
    event.userChoice = Promise.resolve({ outcome: "accepted", platform: "web" });
    fireEvent(window, event);

    const button = await screen.findByRole("button", { name: "Install app" });
    expect(button).toBeEnabled();
    fireEvent.click(button);

    await waitFor(() => expect(prompt).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(screen.getByRole("button", { name: "Installed" })).toBeDisabled());
  });

  it("announces offline state accessibly", async () => {
    setOnline(false);
    render(<OfflineStatus />);
    window.dispatchEvent(new Event("offline"));

    expect(await screen.findByText(/Offline. Chat, uploads, memory actions/i)).toBeInTheDocument();
    expect(screen.getByTestId("offline-indicator")).toHaveAttribute("role", "status");
  });

  it("does not register a service worker outside production", () => {
    const register = vi.fn();
    Object.defineProperty(navigator, "serviceWorker", {
      configurable: true,
      value: { register },
    });

    render(<ServiceWorkerRegistration />);

    expect(register).not.toHaveBeenCalled();
  });
});

describe("service worker cache safety", () => {
  const source = readFileSync(join(process.cwd(), "public", "sw.js"), "utf8");

  it("uses versioned caches and clears stale ContextOS caches", () => {
    expect(source).toContain("contextos-static-${CACHE_VERSION}");
    expect(source).toContain("caches.delete");
    expect(source).toContain("CACHE_VERSION");
  });

  it("excludes private API, auth, document, conversation, memory, dashboard, and token routes", () => {
    expect(source).toContain("/^\\/api\\//");
    expect(source).toContain("/^\\/auth\\//");
    expect(source).toContain("Authorization");
    expect(source).toContain("access_token");
    expect(source).toContain("refresh_token");
    expect(source).toContain("upload");
    expect(source).toContain("download");
    expect(source).toContain("conversation");
    expect(source).toContain("memory");
    expect(source).toContain("dashboard");
    expect(source).toContain("usage");
  });

  it("uses no-store network handling for private requests and has no offline mutation queue", () => {
    expect(source).toContain('fetch(request, { cache: "no-store" })');
    expect(source).not.toContain('addEventListener("sync"');
    expect(source).not.toContain("mutation");
  });
});

describe("private client state cleanup", () => {
  it("clears drafts, ContextOS local state, and app caches on logout", async () => {
    const deleteCache = vi.fn().mockResolvedValue(true);
    Object.defineProperty(window, "caches", {
      configurable: true,
      value: {
        keys: vi.fn().mockResolvedValue(["contextos-static-v1", "other-cache"]),
        delete: deleteCache,
      },
    });
    window.sessionStorage.setItem("contextos.conversationDraft.1", "private draft");
    window.localStorage.setItem("contextos.theme", "dark");
    window.localStorage.setItem("unrelated", "keep");

    await clearPrivateClientState();

    expect(window.sessionStorage.getItem("contextos.conversationDraft.1")).toBeNull();
    expect(window.localStorage.getItem("contextos.theme")).toBeNull();
    expect(window.localStorage.getItem("unrelated")).toBe("keep");
    expect(deleteCache).toHaveBeenCalledWith("contextos-static-v1");
    expect(deleteCache).not.toHaveBeenCalledWith("other-cache");
  });
});
