"use client";

import { WifiOff } from "lucide-react";

import { useNetworkState } from "@/lib/pwa/network";

export function OfflineStatus() {
  const networkState = useNetworkState();
  const offline = networkState === "offline";

  return (
    <div
      aria-live="polite"
      className={`offline-status ${offline ? "offline-status-visible" : ""}`}
      data-testid="offline-indicator"
      role="status"
    >
      {offline ? (
        <span className="inline-flex items-center gap-2">
          <WifiOff aria-hidden="true" size={16} />
          Offline. Chat, uploads, memory actions, and sync require connectivity.
        </span>
      ) : (
        <span className="sr-only">Online</span>
      )}
    </div>
  );
}
