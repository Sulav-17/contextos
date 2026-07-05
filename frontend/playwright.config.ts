import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  webServer:
    process.env.PLAYWRIGHT_SKIP_WEB_SERVER === "1"
      ? undefined
      : {
          command: "pnpm dev",
          url: "http://127.0.0.1:3000/login",
          reuseExistingServer: true,
          timeout: 120000,
        },
  use: {
    baseURL: "http://127.0.0.1:3000",
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 5"] } },
  ],
});
