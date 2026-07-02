import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "ContextOS",
    short_name: "ContextOS",
    description: "Private knowledge assistant for PDFs, conversations, citations, and memory.",
    start_url: "/home",
    scope: "/",
    display: "standalone",
    background_color: "#050912",
    theme_color: "#50d9f6",
    icons: [
      {
        src: "/icons/contextos-icon.svg",
        sizes: "192x192",
        type: "image/svg+xml",
        purpose: "any",
      },
      {
        src: "/icons/contextos-maskable.svg",
        sizes: "512x512",
        type: "image/svg+xml",
        purpose: "maskable",
      },
      {
        src: "/icons/contextos-apple.svg",
        sizes: "180x180",
        type: "image/svg+xml",
        purpose: "any",
      },
    ],
  };
}
