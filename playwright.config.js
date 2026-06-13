const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  outputDir: "./test-artifacts/playwright-output",
  reporter: [
    ["list"],
    ["html", { outputFolder: "test-artifacts/playwright-report", open: "never" }]
  ],
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  use: {
    browserName: "chromium",
    screenshot: "only-on-failure",
    trace: "retain-on-failure"
  }
});
