"use client";

import dynamic from "next/dynamic";

export const SimulationBackdropLoader = dynamic(
  () =>
    import("@/components/ambient/simulation-backdrop").then(
      (mod) => mod.SimulationBackdrop,
    ),
  { ssr: false },
);
