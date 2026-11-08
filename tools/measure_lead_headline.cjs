// Measure how much of its card the lead headline fills on a page, as a browser draws it. Prints JSON.
//
//     node tools/measure_lead_headline.cjs http://127.0.0.1:8000 / 375
//
// Needs the `playwright` package (set PLAYWRIGHT_MODULE to its path). Used by features/home-page.feature, whose browser scenario skips itself without it.
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, route, width] = process.argv.slice(2);

function measure() {
  const headline = document.querySelector(".mom-story-card-lead .mom-story-card-headline");
  if (!headline) return null;
  const box = headline.getBoundingClientRect();
  const range = document.createRange();
  range.selectNodeContents(headline);
  const tops = {};
  for (const rectangle of range.getClientRects()) {
    const key = Math.round(rectangle.top);
    tops[key] = Math.max(tops[key] || 0, rectangle.right - box.left);
  }
  const widths = Object.keys(tops).sort((a, b) => a - b).map((key) => tops[key]);
  return { box: box.width, widths, fontSize: parseFloat(getComputedStyle(headline).fontSize), horizontalScroll: document.documentElement.scrollWidth > innerWidth };
}

(async () => {
  const browser = await playwright.chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: Number(width), height: 900 } })).newPage();
  await page.goto(origin + route, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  console.log(JSON.stringify(await page.evaluate(measure)));
  await browser.close();
})().catch((error) => { console.error(error); process.exit(1); });
