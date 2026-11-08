// Measure a section page as a browser draws it: the site title card, the side column, and the article cards. Prints JSON.
//
//     node tools/measure_section_page.cjs http://127.0.0.1:8000 /security/ 1920
//
// Needs the `playwright` package (set PLAYWRIGHT_MODULE to its path). Used by features/section-pages.feature, whose browser scenarios skip themselves without it.
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, route, width] = process.argv.slice(2);

function measure() {
  const box = (element) => {
    const found = element.getBoundingClientRect();
    return { left: found.left, top: found.top + scrollY, right: found.right, bottom: found.bottom + scrollY, width: found.width, height: found.height };
  };
  const sticker = document.querySelector(".mom-page-card .mom-sticker");
  const sideBoxes = [...document.querySelectorAll(".mom-sf-side *")].map(box).filter((found) => found.width > 0 && found.height > 0);
  const cards = [...document.querySelectorAll(".mom-sf-cards > a")].filter((card) => getComputedStyle(card).display !== "none");
  const cardBoxes = cards.map((card) => ({ lead: card.classList.contains("mom-story-card-lead"), image: box(card.querySelector(".mom-card-image")), card: box(card) }));
  const videos = [...document.querySelectorAll(".mom-sf-video-grid > li")].filter((item) => getComputedStyle(item).display !== "none").map(box);
  const rows = (boxes) => {
    const tops = [];
    for (const found of boxes) if (!tops.some((top) => Math.abs(top - found.top) < 40)) tops.push(found.top);
    return tops.sort((a, b) => a - b).map((top) => boxes.filter((found) => Math.abs(found.top - top) < 40).length);
  };
  const mainBox = box(document.querySelector(".mom-sf-main"));
  return {
    columns: Number(getComputedStyle(document.body).getPropertyValue("--mom-cols")) || 3,
    sticker: sticker ? box(sticker) : null,
    sideBoxes,
    cards: cardBoxes,
    articleRows: rows(cardBoxes.map((found) => found.card)),
    mainWidth: mainBox.width,
    mainRight: mainBox.right,
    videoRows: rows(videos),
    horizontalScroll: document.documentElement.scrollWidth > innerWidth + 1,
  };
}

(async () => {
  const browser = await playwright.chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: Number(width), height: 1000 } })).newPage();
  await page.goto(origin + route, { waitUntil: "load" });
  await page.waitForTimeout(200);
  console.log(JSON.stringify(await page.evaluate(measure)));
  await browser.close();
})();
