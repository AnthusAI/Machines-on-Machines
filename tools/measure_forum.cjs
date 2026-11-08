// Measure the forum as a browser draws it: /conversations/ (boards of rows) or a thread page (posts). Prints JSON.
//
//     node tools/measure_forum.cjs http://127.0.0.1:8000 /conversations/ 375
//
// With a Load more button, presses each one until it is gone and reports how many rows are then shown. Needs the `playwright` package
// (set PLAYWRIGHT_MODULE to its path). Used by features/forum.feature, whose browser scenarios skip themselves without it.
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, route, width] = process.argv.slice(2);

function measure() {
  const shown = (element) => getComputedStyle(element).display !== "none" && element.getBoundingClientRect().width > 0;
  const box = (element) => { const found = element.getBoundingClientRect(); return { left: found.left, top: found.top + scrollY, right: found.right, bottom: found.bottom + scrollY, width: found.width, height: found.height }; };
  const root = document.querySelector(".mom-forum, .mom-topic");
  const rows = [...document.querySelectorAll(".mom-forum-row")].filter(shown);
  const posts = [...document.querySelectorAll(".mom-post")].filter(shown);
  const blocks = [...rows, ...posts].map(box);
  const overlapping = blocks.filter((one, index) => blocks.slice(index + 1).some((two) => one.left < two.right - 1 && two.left < one.right - 1 && one.top < two.bottom - 1 && two.top < one.bottom - 1)).length;
  const clippedText = [...document.querySelectorAll(".mom-forum-title, .mom-forum-about, .mom-forum-numbers, .mom-forum-board-title, .mom-post-text, .mom-post-author, .mom-post-head")]
    .filter(shown).filter((element) => element.scrollWidth > element.clientWidth + 1).map((element) => element.className);
  const outside = [...(root ? root.querySelectorAll("*") : [])].filter(shown).filter((element) => !element.closest(".mom-forum-words") && element.getBoundingClientRect().right > innerWidth + 1).length;
  const bordered = [...(root ? root.querySelectorAll("*") : [])].filter((element) => {
    const style = getComputedStyle(element);
    return ["Top", "Right", "Bottom", "Left"].some((side) => parseFloat(style[`border${side}Width`]) > 0 && style[`border${side}Style`] !== "none") || style.boxShadow !== "none";
  }).length;
  return {
    horizontalScroll: document.documentElement.scrollWidth > innerWidth + 1,
    rootWidth: root ? box(root).width : null,
    boards: document.querySelectorAll(".mom-forum-board").length,
    rowsShown: rows.length, rowsTotal: document.querySelectorAll(".mom-forum-row").length,
    rowHeight: rows[0] ? box(rows[0]).height : null, postsShown: posts.length,
    overlapping, clippedText, outside, bordered,
    loadMoreButtons: document.querySelectorAll(".mom-forum-load-more").length,
  };
}

(async () => {
  const browser = await playwright.chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: Number(width), height: 1000 } })).newPage();
  await page.goto(origin + route, { waitUntil: "load" });
  await page.waitForTimeout(200);
  const before = await page.evaluate(measure);
  let presses = 0;
  while (await page.$(".mom-forum-load-more")) {
    await page.click(".mom-forum-load-more");
    presses += 1;
    if (presses > 200) break;
  }
  const after = await page.evaluate(measure);
  console.log(JSON.stringify({ before, after, presses }));
  await browser.close();
})();
