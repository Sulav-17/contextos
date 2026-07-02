"use client";

import { useEffect, useState } from "react";

export type NetworkState = "online" | "offline";

export function useNetworkState(): NetworkState {
  const [state, setState] = useState<NetworkState>("online");

  useEffect(() => {
    const update = () => setState(navigator.onLine ? "online" : "offline");
    update();
    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    return () => {
      window.removeEventListener("online", update);
      window.removeEventListener("offline", update);
    };
  }, []);

  return state;
}

export function networkUnavailableMessage(action: string): string {
  return `${action} requires connectivity. Your current text is preserved; reconnect and retry.`;
}
