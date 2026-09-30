const { chromium } = require(
  process.env.CIRS_BROWSER_DIR
    ? require("path").join(
        process.env.CIRS_BROWSER_DIR,
        "node_modules/playwright-core",
      )
    : "playwright-core",
);
const fs = require("fs");
const assert = require("assert/strict");
(async () => {
  const b = await chromium.launch({
    executablePath: process.env.CIRS_CHROMIUM || "/usr/bin/chromium",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });
  const results = [];
  const output = process.env.CIRS_QA_DIR || "/tmp/laurels-qa";
  fs.mkdirSync(output, { recursive: true });
  for (const [name, viewport, reducedMotion] of [
    ["desktop", { width: 1440, height: 900 }, "no-preference"],
    ["mobile", { width: 390, height: 844 }, "no-preference"],
    ["reduced", { width: 1440, height: 900 }, "reduce"],
  ]) {
    const p = await b.newPage({ viewport, reducedMotion });
    const errors = [];
    p.on("pageerror", (e) => errors.push(e.message));
    await p.goto(
      (process.env.CIRS_PREVIEW_URL || "http://127.0.0.1:8878") +
        "/our-laurels.html",
    );
    await p.waitForTimeout(600);
    await p.screenshot({ path: `${output}/${name}-opening.png` });
    assert.equal(await p.locator(".lr-row").count(), 56);
    assert.equal(
      await p.evaluate(() => document.documentElement.scrollWidth > innerWidth),
      false,
    );
    async function at(sel, ratio = 0) {
      await p.evaluate(
        ([s, r]) => {
          window.dispatchEvent(
            new CustomEvent("cirs-section-scroll", {
              detail: {
                top:
                  document.querySelector(s).getBoundingClientRect().top +
                  scrollY +
                  r * document.querySelector(s).offsetHeight,
                duration: 0.01,
              },
            }),
          );
          window.scrollTo(
            0,
            document.querySelector(s).getBoundingClientRect().top +
              scrollY +
              r * document.querySelector(s).offsetHeight,
          );
        },
        [sel, ratio],
      );
      await p.waitForTimeout(800);
    }
    for (const sel of [".lr-count", ".lr-reel", ".lr-names", ".lr-season"]) {
      await at(
        sel,
        name === "desktop" && [".lr-count", ".lr-reel"].includes(sel)
          ? 0.12
          : 0,
      );
      await p.screenshot({ path: `${output}/${name}-${sel.slice(4)}.png` });
    }
    await at(".lr-end");
    await p.waitForTimeout(1700);
    await p.screenshot({ path: `${output}/${name}-ending.png` });
    if (reducedMotion === "no-preference") {
      assert.equal(await p.locator(".lr-end__dust").count(), 1);
      assert.equal(
        await p
          .locator(".lr-end__words > span")
          .last()
          .evaluate((e) => getComputedStyle(e).opacity),
        "1",
      );
      await p.evaluate(() => window.scrollBy(0, -30));
      await p.waitForTimeout(2400);
      assert.equal(
        await p
          .locator(".lr-end__previous")
          .evaluate((e) => getComputedStyle(e).opacity),
        "1",
      );
      await p.evaluate(() => window.scrollBy(0, 30));
      await p.waitForTimeout(350);
      const dissolve = await p.evaluate(() => {
        const canvas = document.querySelector(".lr-end__dust");
        return {
          previous: Number(
            getComputedStyle(document.querySelector(".lr-end__previous"))
              .opacity,
          ),
          words: [...document.querySelectorAll(".lr-end__words > span")].map(
            (e) => Number(getComputedStyle(e).opacity),
          ),
          pixels: canvas
            .getContext("2d")
            .getImageData(0, 0, canvas.width, canvas.height)
            .data.some((v, i) => i % 4 === 3 && v > 0),
        };
      });
      assert.ok(dissolve.previous < 1 && dissolve.previous > 0);
      assert.deepEqual(dissolve.words, [0, 0, 0]);
      assert.equal(dissolve.pixels, true);
      await p.screenshot({ path: `${output}/${name}-dissolve-out.png` });
      await p.waitForTimeout(500);
      const and = await p
        .locator(".lr-end__words > span")
        .evaluateAll((es) =>
          es.map((e) => Number(getComputedStyle(e).opacity)),
        );
      assert.ok(and[0] > 0);
      assert.equal(and[1], 0);
      assert.equal(and[2], 0);
      await p.waitForTimeout(550);
      const still = await p
        .locator(".lr-end__words > span")
        .evaluateAll((es) =>
          es.map((e) => Number(getComputedStyle(e).opacity)),
        );
      assert.ok(still[1] > 0);
      assert.equal(still[2], 0);
      await p.waitForTimeout(800);
      assert.equal(
        await p
          .locator(".lr-end__previous")
          .evaluate((e) => getComputedStyle(e).opacity),
        "0",
      );
      await at(".lr-season");
      assert.equal(
        await p.locator(".lr-end__dust").evaluate((e) => e.width),
        0,
      );
      assert.equal(
        await p
          .locator(".lr-end__previous")
          .evaluate((e) => getComputedStyle(e).opacity),
        "1",
      );
      await at(".lr-end");
      await p.waitForTimeout(1500);
      assert.equal(
        await p
          .locator(".lr-end__words > span")
          .last()
          .evaluate((e) => getComputedStyle(e).opacity),
        "1",
      );
    } else assert.equal(await p.locator(".lr-end__dust").count(), 0);
    await at(".lr-archive");
    await p.locator("#lr-q").fill("zzzz_no_match");
    await p.waitForTimeout(250);
    assert.equal(await p.locator(".lr-row:visible").count(), 0);
    await p.locator("[data-lr-reset]").click();
    await p.locator(".lr-row__btn").first().focus();
    await p.keyboard.press("Enter");
    assert.equal(
      await p.locator(".lr-row__btn").first().getAttribute("aria-expanded"),
      "true",
    );
    await p.keyboard.press("Enter");
    if (name === "desktop") {
      await p.setViewportSize({ width: 390, height: 844 });
      await p.waitForTimeout(400);
      assert.equal(await p.locator(".lr-end__dust").count(), 1);
      await p.setViewportSize(viewport);
      await p.waitForTimeout(400);
      await p.emulateMedia({ reducedMotion: "reduce" });
      await p.waitForTimeout(300);
      assert.equal(await p.locator(".lr-end__dust").count(), 0);
      await p.emulateMedia({ reducedMotion: "no-preference" });
      await p.waitForTimeout(300);
      assert.equal(await p.locator(".lr-end__dust").count(), 1);
    }
    assert.deepEqual(errors, []);
    results.push({
      name,
      errors,
      rows: await p.locator(".lr-row").count(),
      overflow: await p.evaluate(
        () => document.documentElement.scrollWidth > innerWidth,
      ),
    });
    await p.close();
  }
  fs.writeFileSync(`${output}/results.json`, JSON.stringify(results, null, 2));
  console.log(results);
  await b.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
