import { expect, test } from "@playwright/test";

test("login page exposes landmarks and no horizontal overflow", async ({ page }) => {
  await page.goto("/login?next=https://evil.example");

  await expect(page.getByRole("heading", { name: "Log in to ContextOS" })).toBeVisible();

  const existingAccount = page.getByRole("region", { name: "Existing account" });

  await expect(existingAccount.getByLabel("Email")).toBeVisible();
  await expect(existingAccount.getByLabel("Password")).toBeVisible();

  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  );

  expect(overflow).toBe(false);
});

test("auth error route is actionable", async ({ page }) => {
  await page.goto("/auth/error");

  await expect(
    page.getByRole("heading", {
      name: "This authentication link could not be used",
    }),
  ).toBeVisible();

  await expect(page.getByRole("link", { name: "Return to login" })).toHaveAttribute(
    "href",
    "/login",
  );
});