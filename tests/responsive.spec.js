const { test, expect } = require("@playwright/test");
const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");

const demoRoot = process.env.DEMO_ROOT || "/work/demo";
const artifactsRoot = process.env.ARTIFACTS_ROOT || "/work/test-artifacts";
let server;
let baseUrl;

function contentType(filePath) {
  if (filePath.endsWith(".html")) return "text/html; charset=utf-8";
  if (filePath.endsWith(".css")) return "text/css; charset=utf-8";
  if (filePath.endsWith(".js")) return "text/javascript; charset=utf-8";
  return "application/octet-stream";
}

function listFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(dir, entry.name);
    return entry.isDirectory() ? listFiles(fullPath) : [fullPath];
  });
}

function sourceMatches(build, pattern) {
  return listFiles(path.join(demoRoot, build))
    .filter((filePath) => /\.(html|css|js)$/i.test(filePath))
    .flatMap((filePath) => {
      const text = fs.readFileSync(filePath, "utf8");
      return pattern.test(text) ? [path.relative(demoRoot, filePath)] : [];
    });
}

test.beforeAll(async () => {
  fs.mkdirSync(artifactsRoot, { recursive: true });
  server = http.createServer((request, response) => {
    const urlPath = new URL(request.url, "http://127.0.0.1").pathname;
    const normalizedPath = urlPath.endsWith("/") ? `${urlPath}index.html` : urlPath;
    const filePath = path.resolve(path.join(demoRoot, normalizedPath));

    if (!filePath.startsWith(path.resolve(demoRoot))) {
      response.writeHead(403);
      response.end("Forbidden");
      return;
    }

    fs.readFile(filePath, (error, body) => {
      if (error) {
        response.writeHead(404);
        response.end("Not found");
        return;
      }
      response.writeHead(200, { "Content-Type": contentType(filePath) });
      response.end(body);
    });
  });

  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

test.afterAll(async () => {
  await new Promise((resolve) => server.close(resolve));
});

async function openBuild(page, build, width, height = 900) {
  const consoleErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => consoleErrors.push(error.message));
  await page.setViewportSize({ width, height });
  await page.goto(`${baseUrl}/${build}/index.html`);
  await page.getByRole("button", { name: "Sign in" }).click();
  const heading = build === "jober" ? /daily control board/i : /manager dashboard/i;
  await expect(page.getByRole("heading", { name: heading })).toBeVisible();
  return consoleErrors;
}

async function expectNoHorizontalScroll(page) {
  await expect.poll(async () => page.evaluate(() => {
    return document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1;
  })).toBe(true);
}

async function captureVisual(page, build, viewportName) {
  await page.screenshot({
    path: path.join(artifactsRoot, `${build}-${viewportName}.png`),
    fullPage: true
  });
}

async function openMobileNav(page) {
  const menu = page.getByRole("button", { name: "Menu" });
  await expect(menu).toBeVisible();
  await menu.click();
  await expect(page.locator("#mobile-nav")).toHaveClass(/is-open/);
}

async function closeMobileNav(page) {
  await page.locator("#mobile-nav").getByRole("button", { name: "Close" }).click();
  await expect(page.locator("#mobile-nav")).not.toHaveClass(/is-open/);
}

async function setRole(page, build, role, width) {
  if (build === "corvinum" && width <= 1024) {
    await openMobileNav(page);
    await page.locator("#mobile-nav").getByRole("button", { name: role }).click();
    await closeMobileNav(page);
    return;
  }
  await page.getByRole("button", { name: role }).click();
}

async function setLanguage(page, language) {
  await page.getByRole("button", { name: language }).first().click();
}

async function navigateCorvinum(page, label, width) {
  if (width <= 1024) {
    await openMobileNav(page);
    await page.locator("#mobile-nav").getByRole("button", { name: label }).click();
    await expect(page.locator("#mobile-nav")).not.toHaveClass(/is-open/);
    return;
  }
  await page.locator(".sidebar").getByRole("button", { name: label }).click();
}

async function navigateJoberTab(page, label) {
  await page.locator(".folder-tabs").getByRole("button", { name: label }).click();
}

async function navigateJoberSection(page, label) {
  await page.locator(".sub-tabs").getByRole("button", { name: label }).click();
}

async function navigateTourStop(page, build, label, width) {
  if (build === "corvinum") {
    if (width <= 1024) {
      await page.locator(".manifest-toggle").click();
      await page.locator(".mobile-manifest .rail-step").filter({ hasText: label }).click();
      return;
    }
    await page.locator(".manifest-rail .rail-step").filter({ hasText: label }).click();
    return;
  }
  await page.locator(".step-bar .step-dot").filter({ hasText: label }).click();
}

async function expectTableCards(page) {
  const table = page.locator(".data-table").first();
  await expect(table).toBeVisible();
  await expect(table.locator("thead")).toHaveCSS("display", "none");
  await expect(table.locator("tbody tr").first()).toHaveCSS("display", "block");
  const labelledCells = await table.locator("tbody tr:first-child td[data-label]").count();
  expect(labelledCells).toBeGreaterThan(0);
}

async function expectVisibleButtonsMeetTapTarget(page) {
  const metrics = await page.locator("button:visible").evaluateAll((buttons) => buttons.map((button) => {
    const rect = button.getBoundingClientRect();
    return {
      label: button.textContent.trim().replace(/\s+/g, " "),
      height: rect.height
    };
  }).filter((metric) => metric.height > 0));

  for (const metric of metrics) {
    expect(metric.height, `${metric.label} button height`).toBeGreaterThanOrEqual(44);
  }
}

async function expectActionSpacing(page) {
  const actionGaps = await page.locator(".inline-actions:visible").evaluateAll((rows) => rows.map((row) => {
    const styles = getComputedStyle(row);
    return {
      columnGap: Number.parseFloat(styles.columnGap),
      rowGap: Number.parseFloat(styles.rowGap)
    };
  }));

  for (const gap of actionGaps) {
    expect(gap.columnGap, "action row column gap").toBeGreaterThanOrEqual(16);
    expect(gap.rowGap, "action row row gap").toBeGreaterThanOrEqual(16);
  }
}

const viewports = [
  { name: "phone", width: 375, height: 900 },
  { name: "tablet", width: 768, height: 900 },
  { name: "desktop", width: 1440, height: 1000 }
];

test("client builds have source-level name separation", async () => {
  expect(sourceMatches("corvinum", /jober/i)).toEqual([]);
  expect(sourceMatches("jober", /corvinum/i)).toEqual([]);
});

test("language switch works in all builds", async ({ page }) => {
  await openBuild(page, "internal", 1440, 1000);
  await setLanguage(page, "SK");
  await expect(page.getByRole("heading", { name: /manažérsky prehľad/i })).toBeVisible();
  await setLanguage(page, "HU");
  await expect(page.getByRole("heading", { name: /vezetői áttekintés/i })).toBeVisible();

  await openBuild(page, "corvinum", 1440, 1000);
  await setLanguage(page, "SK");
  await expect(page.getByRole("heading", { name: /manažérsky prehľad/i })).toBeVisible();
  await setLanguage(page, "HU");
  await expect(page.getByRole("heading", { name: /vezetői áttekintés/i })).toBeVisible();

  await openBuild(page, "jober", 1440, 1000);
  await setLanguage(page, "SK");
  await expect(page.getByRole("heading", { name: /denný riadiaci panel/i })).toBeVisible();
  await setLanguage(page, "HU");
  await expect(page.getByRole("heading", { name: /napi irányítópanel/i })).toBeVisible();
});

for (const viewport of viewports) {
  test(`CorvinumEU build works at ${viewport.name} width`, async ({ page }) => {
    const consoleErrors = await openBuild(page, "corvinum", viewport.width, viewport.height);
    await expectNoHorizontalScroll(page);

    await expect(page.getByText("CorvinumEU")).toBeVisible();
    await expect(page.getByRole("button", { name: "Jober" })).toHaveCount(0);

    if (viewport.width <= 1024) {
      await expect(page.locator(".mobile-manifest")).toBeVisible();
      await expect(page.locator(".manifest-rail")).toBeHidden();
      await openMobileNav(page);
      await closeMobileNav(page);
      await page.locator(".manifest-toggle").click();
      await expect(page.locator(".mobile-manifest .rail-step")).toHaveCount(11);
    } else {
      await expect(page.locator(".sidebar")).toBeVisible();
      await expect(page.locator(".manifest-rail")).toBeVisible();
      await expect(page.locator(".mobile-manifest")).toBeHidden();
    }

    await setRole(page, "corvinum", "Observer", viewport.width);
    await expect(page.getByText("Read-only view")).toBeVisible();
    await expectVisibleButtonsMeetTapTarget(page);
    await expectActionSpacing(page);
    await expectNoHorizontalScroll(page);
    if (viewport.name !== "tablet") await captureVisual(page, "corvinum", viewport.name);
    expect(consoleErrors).toEqual([]);
  });

  test(`Jober build works at ${viewport.name} width`, async ({ page }) => {
    const consoleErrors = await openBuild(page, "jober", viewport.width, viewport.height);
    await expectNoHorizontalScroll(page);

    await expect(page.getByText("Jober")).toBeVisible();
    await expect(page.locator(".folder-tab")).toHaveCount(6);
    await expect(page.locator(".step-dot")).toHaveCount(11);
    await expect(page.locator(".sidebar")).toBeHidden();
    await expect(page.locator(".manifest-rail")).toBeHidden();

    for (const label of ["Operations", "People", "Compliance", "Logistics", "Accounting", "Reports"]) {
      await expect(page.locator(".folder-tabs").getByRole("button", { name: label })).toBeVisible();
    }

    await navigateJoberTab(page, "Logistics");
    await expect(page.getByRole("heading", { name: /accommodation board/i })).toBeVisible();
    await navigateJoberSection(page, "Equipment");
    await expect(page.getByRole("heading", { name: /gear and sizes/i })).toBeVisible();
    await navigateJoberTab(page, "Accounting");
    await expect(page.getByRole("heading", { name: /pohoda snapshot/i })).toBeVisible();

    await setRole(page, "jober", "Observer", viewport.width);
    await expect(page.getByText("Read-only view")).toBeVisible();
    await expectVisibleButtonsMeetTapTarget(page);
    await expectActionSpacing(page);
    await expectNoHorizontalScroll(page);
    if (viewport.name !== "tablet") await captureVisual(page, "jober", viewport.name);
    expect(consoleErrors).toEqual([]);
  });
}

test("phone width restacks tables and decisions in both client builds", async ({ page }) => {
  let consoleErrors = await openBuild(page, "corvinum", 375, 920);
  await navigateCorvinum(page, "People", 375);
  await expectTableCards(page);
  await navigateCorvinum(page, "Documents", 375);
  await expectTableCards(page);
  await navigateTourStop(page, "corvinum", "Demand decision", 375);
  let firstDecisionBox = await page.locator(".decision-option").nth(0).boundingBox();
  let secondDecisionBox = await page.locator(".decision-option").nth(1).boundingBox();
  expect(secondDecisionBox.y).toBeGreaterThan(firstDecisionBox.y + firstDecisionBox.height - 1);
  expect(consoleErrors).toEqual([]);

  consoleErrors = await openBuild(page, "jober", 375, 920);
  await navigateJoberTab(page, "People");
  await expectTableCards(page);
  await navigateJoberTab(page, "Compliance");
  await expectTableCards(page);
  await navigateJoberTab(page, "Logistics");
  await expectTableCards(page);
  await navigateTourStop(page, "jober", "Demand decision", 375);
  firstDecisionBox = await page.locator(".decision-option").nth(0).boundingBox();
  secondDecisionBox = await page.locator(".decision-option").nth(1).boundingBox();
  expect(secondDecisionBox.y).toBeGreaterThan(firstDecisionBox.y + firstDecisionBox.height - 1);
  await navigateTourStop(page, "jober", "Manager field view", 375);
  await expect(page.getByRole("heading", { name: /field mode/i })).toBeVisible();
  await expectNoHorizontalScroll(page);
  expect(consoleErrors).toEqual([]);
});
