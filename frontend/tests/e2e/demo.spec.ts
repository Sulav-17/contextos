import { expect, test } from "@playwright/test";

test("public demo loads with disclosure and deterministic citations", async ({ page }) => {
  await page.goto("/demo");

  await expect(page.getByRole("heading", { name: /Explore ContextOS/i })).toBeVisible();
  await expect(page.getByText("Demo Mode")).toBeVisible();
  await expect(
    page.getByText(
      "This guided demo uses fictional sample data and prepared responses. It does not access real user accounts, documents, or live AI services.",
    ),
  ).toBeVisible();

  await page
    .getByRole("button", { name: "Which project risks should I review first?" })
    .click();
  await expect(page.getByText(/review the launch-readiness checklist first/i)).toBeVisible();
  await expect(page.getByText("[1] Northstar Project Plan.pdf, page 3")).toBeVisible();
  await expect(page.getByRole("link")).toHaveCount(0);
  await expect(page.getByRole("button", { name: /log in/i })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /create account/i })).toHaveCount(0);
});

test("public demo composer is honest for unsupported questions", async ({ page }) => {
  await page.goto("/demo");

  await page.getByLabel("Try a prepared sample question").fill("Can you answer anything?");
  await page.getByRole("button", { name: /Show prepared answer/i }).click();

  await expect(
    page.getByText(/currently supports the provided sample questions/i),
  ).toBeVisible();
  await expect(page.getByText(/No network request or live AI call was made/i)).toBeVisible();
});

test("public demo has no horizontal overflow at 390px width", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/demo");

  await expect(page.getByRole("heading", { name: /Explore ContextOS/i })).toBeVisible();
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth,
  );
  expect(overflow).toBe(false);
});
