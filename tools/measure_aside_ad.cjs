// Measure an article's in-text aside ad and the lines of words around it, as a browser draws them. Prints JSON.
//
//     node tools/measure_aside_ad.cjs http://127.0.0.1:8000 /articles/some-story/ 1440
//
// Needs the `playwright` package (set PLAYWRIGHT_MODULE to its path when it is not installed beside this repository).
// Used by features/advertising.feature, whose browser scenarios skip themselves when Playwright is missing.
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, route, width] = process.argv.slice(2);

function measure() {
  const aside = document.querySelector('[data-ad-placement="article-aside"]');
  const box = (element) => { const r = element.getBoundingClientRect(); return { left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width }; };
  const asideBox = box(aside);
  // Every line of the paragraphs next to the aside, from the text's own line boxes (a Range gives one rectangle per line).
  const lines = [];
  for (const paragraph of aside.parentElement.querySelectorAll(":scope > p")) {
    const range = document.createRange();
    range.selectNodeContents(paragraph);
    const rows = new Map();
    for (const rectangle of range.getClientRects()) {
      if (rectangle.width < 1) continue;
      const key = Math.round(rectangle.top);
      const row = rows.get(key) || { left: Infinity, right: -Infinity, top: rectangle.top, bottom: rectangle.bottom };
      row.left = Math.min(row.left, rectangle.left);
      row.right = Math.max(row.right, rectangle.right);
      rows.set(key, row);
    }
    for (const row of rows.values()) lines.push({ ...row, text: paragraph.textContent.slice(0, 40) });
  }
  return {
    width: innerWidth,
    floated: getComputedStyle(aside).cssFloat !== "none",
    aside: asideBox,
    column: box(aside.parentElement),
    lines,
    viewportOverflow: document.documentElement.scrollWidth - innerWidth,
  };
}

(async () => {
  const browser = await playwright.chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: Number(width), height: 1000 } })).newPage();
  await page.goto(origin + route, { waitUntil: "load" });
  await page.evaluate(() => document.querySelector("#papyrus-consent-banner")?.remove());
  await page.evaluate(() => document.fonts.ready);
  process.stdout.write(JSON.stringify(await page.evaluate(measure)));
  await browser.close();
})().catch((error) => { console.error(error.message); process.exit(1); });
