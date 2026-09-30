// Keyboard focus regression against the complete stylesheet cascade.
// Use a static server and CIRS_BROWSER_DIR pointing to a Playwright install.
const path = require("node:path");
const { chromium } = require(
  process.env.CIRS_BROWSER_DIR
    ? path.join(process.env.CIRS_BROWSER_DIR, "node_modules/playwright-core")
    : "playwright-core",
);
const assert = require("node:assert/strict");
const fs = require("node:fs");
const base = process.env.CIRS_PREVIEW_URL || "http://127.0.0.1:8879";
const output = process.env.CIRS_QA_DIR || "/tmp/laurels-focus-qa";
fs.mkdirSync(output, { recursive: true });

let browser;
(async () => {
  browser = await chromium.launch({
    executablePath: process.env.CIRS_CHROMIUM || "/usr/bin/chromium",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });
  const results = [];
  async function handoff(page) {
    await page.evaluate(() => {
      const trigger = ScrollTrigger.getAll().find((t) =>
        t.trigger?.matches("[data-lr-reel]"),
      );
      const top = trigger.end - 10;
      window.dispatchEvent(
        new CustomEvent("cirs-section-scroll", {
          detail: { top, duration: 0.01 },
        }),
      );
      window.scrollTo(0, top);
    });
    await page.waitForTimeout(700);
  }
  async function check(page, name, selector, role, background) {
    const target = page.locator(selector).first();
    if (name === "desktop-photographic-handoff") {
      // Keep the pinned composition at its final frame. Native focus scrolling
      // would rewind the reel and hide this moved story before it can be inspected.
      await page.keyboard.press("Tab");
      await page.keyboard.press("Escape");
      await handoff(page);
      await target.evaluate((element) =>
        element.focus({ preventScroll: true }),
      );
    } else {
      await target.scrollIntoViewIfNeeded();
      await target.focus();
      // Leave and return with real Tab navigation; no pseudo-class is forced.
      await page.keyboard.press("Shift+Tab");
      await page.keyboard.press("Tab");
    }
    await page.waitForTimeout(50);
    const state = await target.evaluate(
      (element, args) => {
        const css = getComputedStyle(element);
        const probe = document.createElement("span");
        probe.style.color = `var(${args.role})`;
        element.appendChild(probe);
        const expected = getComputedStyle(probe).color;
        probe.remove();
        const backing = args.background
          ? getComputedStyle(element.closest(args.background)).backgroundColor
          : null;
        function luminance(color) {
          const channels = color
            .match(/[\d.]+/g)
            .slice(0, 3)
            .map(Number)
            .map((n) => {
              n /= 255;
              return n <= 0.04045 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4;
            });
          return channels.reduce(
            (sum, n, i) => sum + n * [0.2126, 0.7152, 0.0722][i],
            0,
          );
        }
        const foreground = luminance(css.outlineColor),
          backdrop = backing ? luminance(backing) : null;
        return {
          focused: document.activeElement === element,
          focusVisible: element.matches(":focus-visible"),
          outline: css.outlineColor,
          expected,
          width: css.outlineWidth,
          style: css.outlineStyle,
          background: backing,
          contrast: backing
            ? (Math.max(foreground, backdrop) + 0.05) /
              (Math.min(foreground, backdrop) + 0.05)
            : null,
        };
      },
      { role, background },
    );
    results.push({ name, ...state });
    console.log(name, state.outline, state.expected, state.contrast);
    await page.screenshot({ path: path.join(output, `${name}.png`) });
    return state;
  }
  for (const [profile, viewport] of [
    ["desktop", { width: 1440, height: 900 }],
    ["mobile", { width: 390, height: 844 }],
  ]) {
    const page = await browser.newPage({ viewport, reducedMotion: "reduce" });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(`${base}/our-laurels.html`);
    await page.waitForTimeout(300);
    for (const [name, selector, background] of [
      ["chapters", ".rd-laurel summary", ".rd-laurels"],
      ["count", ".lr-count .lr-src", ".lr-count"],
      ["reel", ".lr-ms__open", ".lr-reel"],
      ["names", ".lr-name__btn", ".lr-names"],
      ["archive", ".lr-cat-btn", ".lr-archive"],
      ["ending", ".lr-end__note a", ".lr-end"],
    ])
      await check(
        page,
        `${profile}-${name}`,
        selector,
        "--lr-gold-ink",
        background,
      );
    await check(
      page,
      `${profile}-feature`,
      ".lr-features .lr-src",
      "--lr-gold",
      ".lr-features",
    );
    assert.deepEqual(errors, []);
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth > innerWidth,
      ),
      false,
    );
    await page.close();
  }
  const page = await browser.newPage({
    viewport: { width: 1440, height: 900 },
  });
  await page.goto(`${base}/our-laurels.html`);
  await page.waitForTimeout(300);
  await check(
    page,
    "desktop-photographic-handoff",
    ".lr-reel__final .lr-src",
    "--lr-gold",
    null,
  );
  await page.close();
  await browser.close();
  fs.writeFileSync(
    path.join(output, "results.json"),
    JSON.stringify(results, null, 2),
  );
  console.table(
    results.map(({ name, outline, expected, contrast }) => ({
      name,
      outline,
      expected,
      contrast,
    })),
  );
  for (const result of results) {
    assert.equal(result.focused, true, result.name);
    assert.equal(result.focusVisible, true, result.name);
    assert.equal(result.style, "solid", result.name);
    assert.equal(result.width, "2px", result.name);
    assert.equal(result.outline, result.expected, result.name);
    assert.ok(
      result.contrast === null || result.contrast >= 3,
      `${result.name}: ${result.contrast}`,
    );
  }
})()
  .catch((error) => {
    console.error(error);
    process.exitCode = 1;
  })
  .finally(() => browser?.close());
