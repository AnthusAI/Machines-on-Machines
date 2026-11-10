// Measures highlights and runs of citation numbers in a browser. Prints one JSON object.
//   node tools/measure_highlight.cjs ORIGIN WIDTH THEME [SCREENSHOT_DIRECTORY]
// With a screenshot directory it also saves pictures of the article excerpt, with the citation gap before and after the fix.
const [origin, width, theme, screenshotDirectory] = process.argv.slice(2);
let chromium;
try {
  ({ chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright"));
} catch {
  console.error("Playwright is not installed");
  process.exit(2);
}

const CITATION_RUN = '<p id="run">Flight records. <span class="citation"><a href="#citation-3">3</a></span> <span class="citation"><a href="#citation-4">4</a></span> <span class="citation"><a href="#citation-5">5</a></span> <span class="citation"><a href="#citation-1">1</a></span></p>'
  + '<p id="single">One claim with a single note after it. <span class="citation"><a href="#citation-1">1</a></span> Then the text goes on.</p>';

function luminance([red, green, blue]) {
  const linear = (channel) => { const value = channel / 255; return value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4; };
  return 0.2126 * linear(red) + 0.7152 * linear(green) + 0.0722 * linear(blue);
}
function contrast(first, second) {
  const [lighter, darker] = [luminance(first), luminance(second)].sort((a, b) => b - a);
  return (lighter + 0.05) / (darker + 0.05);
}
const channels = (color) => color.match(/[\d.]+/g).slice(0, 3).map(Number);

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
    await page.goto(new URL("/field-notes/a-highlight-helps-a-reader-skim/", origin).href);
    await page.evaluate((html) => { document.querySelector(".mom-article-body p").insertAdjacentHTML("afterend", html); }, CITATION_RUN);

    const measured = await page.evaluate(() => {
      const style = (element, property) => getComputedStyle(element)[property];
      const marks = Array.from(document.querySelectorAll(".mom-article-body mark"), (mark) => ({
        background: style(mark, "backgroundColor"),
        color: style(mark, "color"),
        weight: Number(style(mark, "fontWeight")),
        radius: parseFloat(style(mark, "borderTopLeftRadius")),
        borderWidth: parseFloat(style(mark, "borderTopWidth")),
        outlineStyle: style(mark, "outlineStyle"),
        borderStyle: style(mark, "borderTopStyle"),
        paddingInline: parseFloat(style(mark, "paddingLeft")),
        decorationBreak: style(mark, "boxDecorationBreak"),
        lines: new Set(Array.from(mark.getClientRects(), (rectangle) => Math.round(rectangle.top))).size,
        linkColor: mark.querySelector("a") ? style(mark.querySelector("a"), "color") : null,
      }));
      const bodyWeight = Number(style(document.querySelector(".mom-article-body p"), "fontWeight"));
      const gapsAfterPreviousNumber = (selector) => {
        const numbers = Array.from(document.querySelectorAll(selector + " .citation"));
        return numbers.slice(1).map((number, index) => number.getBoundingClientRect().left - numbers[index].getBoundingClientRect().right);
      };
      const single = document.querySelector("#single .citation");
      return {
        marks, bodyWeight,
        runGaps: gapsAfterPreviousNumber("#run"),
        runFontSize: parseFloat(style(document.querySelector("#run .citation"), "fontSize")),
        singleMarginLeft: parseFloat(style(single, "marginLeft")),
        firstOfRunMarginLeft: parseFloat(style(document.querySelector("#run .citation"), "marginLeft")),
        overflow: document.documentElement.scrollWidth > innerWidth,
      };
    });
    measured.contrasts = measured.marks.map((mark) => ({
      text: contrast(channels(mark.color), channels(mark.background)),
      link: mark.linkColor ? contrast(channels(mark.linkColor), channels(mark.background)) : null,
    }));

    if (screenshotDirectory) {
      const fs = require("fs");
      fs.mkdirSync(screenshotDirectory, { recursive: true });
      const label = `${width}-${theme}`;
      const excerpt = page.locator(".mom-article-body");
      const shoot = async (name) => { await excerpt.screenshot({ path: `${screenshotDirectory}/${name}-${label}.png` }); };
      await page.addStyleTag({ content: ".mom-article-body figure, .mom-ad, aside, #papyrus-consent-banner { display: none !important; }" });
      await shoot("after");
      await page.addStyleTag({ content: ".mom-article-body .citation + .citation { margin-left: -0.3em !important; }" });
      await shoot("before-citation-gap");
    }
    console.log(JSON.stringify(measured));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
