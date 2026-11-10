const [origin, width, theme] = process.argv.slice(2);
let chromium;
try {
  ({ chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright"));
} catch {
  console.error("Playwright is not installed");
  process.exit(2);
}

(async () => {
  let browser;
  try {
    browser = await chromium.launch(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {});
  } catch {
    console.error("Playwright Chromium is not available");
    process.exit(2);
  }
  try {
    const page = await browser.newPage({ viewport: { width: Number(width), height: 900 }, colorScheme: theme });
    await page.goto(new URL("/field-notes/the-agents-are-writing-the-benchmarks-now/", origin).href);
    const measured = await page.locator(".markus-two-up").evaluate((pair) => {
      const [first, second] = Array.from(pair.children, (column) => column.getBoundingClientRect());
      const fontSize = (element) => parseFloat(getComputedStyle(element).fontSize);
      return {
        arrangement: Math.abs(first.top - second.top) < 1 && second.left >= first.right ? "side by side" : "stacked",
        nestedFigures: pair.querySelectorAll("figure figure").length,
        overflow: pair.scrollWidth > pair.clientWidth || document.documentElement.scrollWidth > innerWidth,
        quotes: Array.from(pair.querySelectorAll(".markus-pull-quote"), (quote) => ({
          size: fontSize(quote.querySelector("blockquote")),
          sourceSize: fontSize(quote.querySelector("figcaption")),
        })),
        singleSize: fontSize(document.querySelector(".mom-pull-quote-text")),
      };
    });
    console.log(JSON.stringify(measured));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
