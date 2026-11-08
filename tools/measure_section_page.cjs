// Measure a section page as a browser draws it: the site title card, the side column (the conversations rail), the article, video and post cards. Prints JSON.
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
  const shown = (element) => getComputedStyle(element).display !== "none" && element.getBoundingClientRect().width > 0;
  const sticker = document.querySelector(".mom-home-card .mom-sticker");
  const sideBoxes = [...document.querySelectorAll(".mom-home-rail *, .mom-home-purpose")].filter(shown).map(box);
  const lead = document.querySelector(".mom-home-lead > a");
  const rows = (boxes) => {
    const tops = [];
    for (const found of boxes) if (!tops.some((top) => Math.abs(top - found.top) < 40)) tops.push(found.top);
    return tops.sort((a, b) => a - b).map((top) => boxes.filter((found) => Math.abs(found.top - top) < 40).length);
  };
  const cardsOf = (selector, imageSelector = ".mom-card-image") => [...document.querySelectorAll(selector)].filter(shown).map((card) => ({ card: box(card), image: box(card.querySelector(imageSelector)) }));
  const articles = cardsOf(".mom-sf-cards > a");
  const posts = cardsOf(".mom-sf-post-grid > a");
  const videos = [...document.querySelectorAll(".mom-sf-videos .home-page-grid > li")].filter(shown).map(box);
  return {
    columns: Number(getComputedStyle(document.body).getPropertyValue("--mom-cols")) || 3,
    sticker: sticker ? box(sticker) : null,
    sideBoxes,
    lead: lead ? { card: box(lead), image: box(lead.querySelector(".mom-card-image")) } : null,
    articles, posts,
    articleRows: rows(articles.map((found) => found.card)),
    postRows: rows(posts.map((found) => found.card)),
    videoRows: rows(videos),
    videoWidths: videos.map((found) => found.width),
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
