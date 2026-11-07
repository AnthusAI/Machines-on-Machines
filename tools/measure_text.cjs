// List every visible piece of text on a page that is drawn below its minimum size, as a browser draws it. Prints JSON.
//
//     node tools/measure_text.cjs http://127.0.0.1:8000 / 375 '{"reading":18,"interface":14,"label":13}'
//
// The floors are rendered pixels and come from tools/scale_css.py (the caller passes them), so they live in one place. Needs the
// `playwright` package (set PLAYWRIGHT_MODULE to its path). Used by features/text-size.feature, which skips itself without Playwright.
//
// Which floor applies to a piece of text:
//   reading   a paragraph or list item of running prose inside an article, wiki or post body (not a figure, a callout, the See also
//             list, or the knowledge graph's lists)
//   label     uppercase text with letter spacing, the micro-labels
//   interface everything else
// Text is skipped when nobody can see it: display none, visibility hidden, zero opacity, a zero-size or clipped-away box, or a
// screen-reader-only box (1px or less in either direction).
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, route, width, floorsJson] = process.argv.slice(2);
const floors = JSON.parse(floorsJson);

function measure(floors) {
  const READING_BLOCK = "p, li";
  const READING_HOME = ".mom-article-body, .mom-home-purpose, .home-page-explainer-body";
  const NOT_READING = "figure, figcaption, aside, nav, .mom-see-also, .mom-hashtags, .papyrus-knowledge-neighbourhood, .papyrus-knowledge-related, .markus-callout, .mom-pull-quote, .mom-share-panel";
  const SKIPPED_TAGS = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE", "OPTION"]);

  function invisible(element) {
    for (let node = element; node && node.nodeType === 1; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (style.display === "none" || style.visibility === "hidden" || parseFloat(style.opacity) === 0) return true;
      if (node.hasAttribute("hidden")) return true;
      const box = node.getBoundingClientRect();
      if (node === element && (box.width === 0 || box.height === 0)) return true;
      if (style.position === "absolute" && (box.width <= 1 || box.height <= 1) && style.overflow !== "visible") return true;
      if (style.clip !== "auto" && /rect\(0(px)?,? 0(px)?,? 0(px)?,? 0(px)?\)/.test(style.clip)) return true;
      if (style.clipPath === "inset(50%)") return true;
    }
    return false;
  }

  function renderedSize(element) {
    const size = parseFloat(getComputedStyle(element).fontSize);
    const svg = element.closest("svg");
    if (svg && element.ownerSVGElement && element.getScreenCTM) {
      const matrix = element.getScreenCTM();
      return matrix ? size * Math.hypot(matrix.a, matrix.b) : size;
    }
    return size;
  }

  function roleOf(element, style) {
    const block = element.closest(READING_BLOCK);
    if (block && block.closest(READING_HOME) && !element.closest(NOT_READING) && !block.closest(NOT_READING)) return "reading";
    if (style.textTransform === "uppercase" && style.letterSpacing !== "normal") return "label";
    return "interface";
  }

  const offenders = [];
  let checked = 0;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    if (!node.nodeValue.trim()) continue;
    const element = node.parentElement;
    if (!element || SKIPPED_TAGS.has(element.tagName) || element.closest("script, style, noscript, template")) continue;
    if (invisible(element)) continue;
    const style = getComputedStyle(element);
    const role = roleOf(element, style);
    const size = renderedSize(element);
    checked += 1;
    if (size < floors[role] - 0.05) {
      offenders.push({ role, size: Math.round(size * 100) / 100, floor: floors[role], text: node.nodeValue.trim().slice(0, 50), path: element.tagName.toLowerCase() + (element.className && typeof element.className === "string" ? "." + element.className.trim().split(/\s+/).join(".") : "") });
    }
  }
  return { checked, offenders };
}

(async () => {
  const browser = await playwright.chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: Number(width), height: 1000 } })).newPage();
  await page.goto(origin + route, { waitUntil: "load" });
  await page.waitForTimeout(200);
  console.log(JSON.stringify(await page.evaluate(measure, floors)));
  await browser.close();
})();
