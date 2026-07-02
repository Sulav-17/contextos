"use client";

import { useCallback, useEffect, useState } from "react";

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed"; platform: string }>;
};

export type InstallState =
  | "checking"
  | "available"
  | "installed"
  | "ios-guidance"
  | "unavailable";

function isStandalone(): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    ("standalone" in navigator && Boolean((navigator as Navigator & { standalone?: boolean }).standalone))
  );
}

function isIosSafariLike(): boolean {
  const userAgent = navigator.userAgent.toLowerCase();
  return /iphone|ipad|ipod/.test(userAgent) && !/crios|fxios|edgios/.test(userAgent);
}

export function useInstallPrompt() {
  const [promptEvent, setPromptEvent] = useState<BeforeInstallPromptEvent | null>(null);
  const [state, setState] = useState<InstallState>(() =>
    isStandalone() ? "installed" : "checking",
  );

  useEffect(() => {
    if (isStandalone()) {
      return;
    }
    let capturedPrompt = false;

    const onBeforeInstallPrompt = (event: Event) => {
      event.preventDefault();
      capturedPrompt = true;
      setPromptEvent(event as BeforeInstallPromptEvent);
      setState("available");
    };
    const onInstalled = () => {
      setPromptEvent(null);
      setState("installed");
    };

    window.addEventListener("beforeinstallprompt", onBeforeInstallPrompt);
    window.addEventListener("appinstalled", onInstalled);
    window.setTimeout(() => {
      if (!capturedPrompt) {
        setState(isIosSafariLike() ? "ios-guidance" : "unavailable");
      }
    }, 250);

    return () => {
      window.removeEventListener("beforeinstallprompt", onBeforeInstallPrompt);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  const promptInstall = useCallback(async () => {
    if (!promptEvent) {
      return;
    }
    await promptEvent.prompt();
    const choice = await promptEvent.userChoice;
    if (choice.outcome === "accepted") {
      setState("installed");
    } else {
      setState(isIosSafariLike() ? "ios-guidance" : "unavailable");
    }
    setPromptEvent(null);
  }, [promptEvent]);

  return { promptInstall, state };
}
