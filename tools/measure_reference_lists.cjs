// Measure a Videos, Findings or section list page as a browser draws it: the lead, the section blocks, the stream and the site title card. Prints JSON.
//
//     node tools/measure_reference_lists.cjs http://127.0.0.1:8000 /videos/ 1440
//     node tools/measure_reference_lists.cjs http://127.0.0.1:8000 /videos/ 1440 --to-end     (also scrolls and presses Load more until the list is complete)
//
// Needs the `playwright` package (set PLAYWRIGHT_MODULE to its path). Used by the @browser scenarios of features/reference-lists.feature and
// features/section-lists.feature, which skip themselves without it.
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, route, width] = process.argv.slice(2);
const toEnd = process.argv.includes("--to-end");
const GIVE_UP_AFTER_MILLISECONDS = 90000;

function measure() {
  const SAME_ROW_TOLERANCE = 40;
  const shown = (element) => getComputedStyle(element).display !== "none" && element.getBoundingClientRect().width > 0;
  const box = (element) => {
    const found = element.getBoundingClientRect();
    return { left: found.left, top: found.top + scrollY, right: found.right, bottom: found.bottom + scrollY };
  };
  const visualRows = (row) => {
    const tops = [];
    for (const item of row.children) {
      const top = item.getBoundingClientRect().top;
      const existing = tops.find((entry) => Math.abs(entry.top - top) < SAME_ROW_TOLERANCE);
      if (existing) existing.count += 1; else tops.push({ top, count: 1 });
    }
    return tops.sort((a, b) => a.top - b.top).map((entry) => entry.count);
  };
  const rowsOf = (container) => [...container.querySelectorAll(".mom-refs-row")].filter(shown).map((row) => ({ of: row.children.length, visual: visualRows(row) }));
  const lead = document.querySelector(".mom-refs-lead");
  const stream = document.querySelector(".mom-refs-stream");
  const grid = stream && stream.querySelector("[data-reference-grid]");
  const sticker = document.querySelector(".mom-page-card .mom-sticker");
  const stickerBox = sticker ? box(sticker) : null;
  const TILT_BLEED = 8;   // the title card is tilted, so its box reaches a few pixels beyond the card it draws; only a deeper overlap is a card touching it
  const touches = (a, b) => a && b && a.left < b.right - TILT_BLEED && a.right > b.left + TILT_BLEED && a.top < b.bottom && a.bottom > b.top;
  const cards = [...document.querySelectorAll(".mom-refs-lead .mom-reference-card, .mom-refs-section .mom-reference-card, .mom-refs-stream .mom-reference-card")].filter(shown);
  const blockRows = {};
  for (const block of document.querySelectorAll(".mom-refs-section")) blockRows[block.getAttribute("aria-label")] = rowsOf(block);
  const empty = document.querySelector(".mom-refs-stream .home-page-empty");
  const more = document.querySelector("[data-reference-more]");
  const columns = grid ? getComputedStyle(grid).gridTemplateColumns.split(" ").filter(Boolean).length : 0;
  const count = grid ? grid.children.length : 0;
  return {
    width: innerWidth,
    columns: Number(getComputedStyle(document.body).getPropertyValue("--mom-cols")) || 3,
    overflowX: document.documentElement.scrollWidth > innerWidth + 1,
    leadRows: lead ? rowsOf(lead) : [],
    blockRows,
    blockTiers: [...document.querySelectorAll(".mom-refs-section")].map((block) => block.getAttribute("data-tier")),
    streamColumns: columns,
    streamFirstPageCount: count,
    streamFirstPageRows: columns ? count / columns : 0,
    headingsInLeadOrStream: document.querySelectorAll(".mom-refs-lead :is(h1,h2,h3,h4,h5,h6), .mom-refs-stream :is(h1,h2,h3,h4,h5,h6)").length,
    siteCardTouches: cards.filter((card) => touches(box(card), stickerBox)).length,
    loadMore: Boolean(more) && !more.hidden && shown(more),
    emptyVisible: Boolean(empty) && shown(empty),
    emptyCovered: Boolean(empty) && touches(box(empty), stickerBox),
  };
}

function tally() {
  const addresses = [...document.querySelectorAll(".mom-refs-lead .mom-reference-card, .mom-refs-stream .mom-reference-card")].map((card) => (card.matches("a") ? card : card.querySelector("a.mom-reference-card-title")).getAttribute("href"));
  const status = document.querySelector(".mom-refs-stream [data-reference-status]");
  return { uniqueAddresses: new Set(addresses).size, duplicates: addresses.length - new Set(addresses).size, status: status ? status.textContent.trim() : "" };
}

(async () => {
  const browser = await playwright.chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: Number(width), height: 1000 } })).newPage();
  await page.goto(origin + route, { waitUntil: "load" });
  await page.waitForTimeout(300);
  const result = await page.evaluate(measure);
  if (toEnd) {
    const started = Date.now();
    for (;;) {
      const done = await page.evaluate(() => { const more = document.querySelector("[data-reference-more]"); return !more || more.hidden; });
      if (done || Date.now() - started > GIVE_UP_AFTER_MILLISECONDS) break;
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      const button = await page.$("[data-reference-more] button");
      if (button && (await page.evaluate(() => document.querySelector("[data-reference-status]").textContent.includes("Press Load more")))) await button.click();
      await page.waitForTimeout(150);
    }
    Object.assign(result, await page.evaluate(tally));
  }
  console.log(JSON.stringify(result));
  await browser.close();
})();
