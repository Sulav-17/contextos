import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import { SimulationBackdrop } from "@/components/ambient/simulation-backdrop";
import { ServiceWorkerRegistration } from "@/components/pwa/service-worker-registration";
import { ThemeProvider } from "@/components/theme/theme-provider";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "ContextOS",
    template: "%s | ContextOS",
  },
  description: "Private knowledge assistant for individual workspaces.",
  applicationName: "ContextOS",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "ContextOS",
  },
  formatDetection: {
    telephone: false,
  },
  manifest: "/manifest.webmanifest",
  icons: {
    icon: "/icons/contextos-icon.svg",
    apple: "/icons/contextos-apple.svg",
  },
  other: {
    "mobile-web-app-capable": "yes",
  },
};

export const viewport: Viewport = {
  themeColor: "#50d9f6",
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
          <ServiceWorkerRegistration />
          <SimulationBackdrop />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
