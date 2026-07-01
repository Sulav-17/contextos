import type { Metadata } from "next";
import type { ReactNode } from "react";

import { SimulationBackdrop } from "@/components/ambient/simulation-backdrop";
import { ThemeProvider } from "@/components/theme/theme-provider";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "ContextOS",
    template: "%s | ContextOS",
  },
  description: "Private knowledge assistant for individual workspaces.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <script
          dangerouslySetInnerHTML={{
            __html: `
try {
  var mode = localStorage.getItem("contextos.appearance") || "system";
  var dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  var resolved = mode === "system" ? (dark ? "dark" : "light") : mode;
  document.documentElement.dataset.theme = resolved;
  document.documentElement.dataset.appearance = mode;
} catch (_) {}
            `,
          }}
        />
        <ThemeProvider>
          <SimulationBackdrop />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
