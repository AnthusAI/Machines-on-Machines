// Measure the forum's layout as a browser draws it: where the site card (the sticker) is, how much of the page the forum uses, and whether the card or a side
// panel touches a row. Prints JSON. Works on /conversations/, a board page (/<section>/conversations/) and a thread page.
//
//     node tools/measure_forum_layout.cjs http://127.0.0.1:8000 /conversations/ 1440
//
// Needs the `playwright` package (set PLAYWRIGHT_MODULE to its path). Used by features/forum.feature (`@browser` scenarios); also run by hand on a build of
// the previous release to compare ("before") with a build of this branch ("after").
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, route, width] = process.argv.slice(2);

function measure() {
  const shown = (element) => getComputedStyle(element).display !== "none" && getComputedStyle(element).visibility !== "hidden" && element.getBoundingClientRect().width > 0 && element.getBoundingClientRect().height > 0;
  const box = (element) => { const found = element.getBoundingClientRect(); return { left: found.left, top: found.top + scrollY, right: found.right, bottom: found.bottom + scrollY, width: found.width, height: found.height }; };
  const hit = (one, two) => one.left < two.right - 1 && two.left < one.right - 1 && one.top < two.bottom - 1 && two.top < one.bottom - 1;
  const forum = document.querySelector(".mom-forum, .mom-topic");
  const page = document.querySelector(".mom-page, .mom-topic");
  const stickers = [...document.querySelectorAll("main .mom-sticker, .mom-page .mom-sticker, .mom-site-card-slot .mom-sticker")].filter(shown);
  const panels = [...document.querySelectorAll(".mom-forum-panel, .mom-topic-facts")].filter(shown);
  const rows = [...document.querySelectorAll(".mom-forum-row")].filter(shown);
  const boardBoxes = [...document.querySelectorAll(".mom-forum-board")].filter(shown);
  const posts = [...document.querySelectorAll(".mom-post")].filter(shown);
  const floating = [...stickers, ...panels].map(box);
  const blocks = [...rows, ...posts, ...document.querySelectorAll(".mom-forum-board-head, .mom-forum-strip")].filter(shown).map(box);
  const coveredBy = floating.filter((one) => blocks.some((two) => hit(one, two))).length;
  const panelOverlap = floating.filter((one, index) => floating.slice(index + 1).some((two) => hit(one, two))).length;
  const titles = [...document.querySelectorAll(".mom-forum-title")].filter(shown);
  const content = document.querySelector("main, .mom-page") ? document.querySelector("main") || document.querySelector(".mom-page") : document.body;
  const spine = document.querySelector("body.mom > .mom-spine");
  const spineWidth = spine && shown(spine) ? box(spine).width : 0;
  const rightmost = Math.max(0, ...[...(forum ? forum.querySelectorAll("*") : [])].filter(shown).filter((element) => !element.closest(".mom-forum-words")).map((element) => element.getBoundingClientRect().right));
  return {
    width: innerWidth,
    horizontalScroll: document.documentElement.scrollWidth > innerWidth + 1,
    stickerCount: stickers.length,
    sticker: stickers[0] ? box(stickers[0]) : null,
    stickerBelowFirstScreen: stickers[0] ? box(stickers[0]).top > innerHeight : null,
    panels: panels.map((panel) => ({ className: panel.className, ...box(panel) })),
    pageWidth: page ? box(page).width : null,
    contentWidth: innerWidth - spineWidth,
    forumWidth: forum ? box(forum).width : null,
    // How much of the window (less the spine) the forum's drawn content spans, from the page's left edge to its rightmost drawn edge
    usedFraction: forum && page ? (rightmost - box(page).left) / (innerWidth - spineWidth - box(page).left) : null,
    blankRight: Math.round(innerWidth - rightmost),
    boardBoxes: boardBoxes.map(box),
    boardColumns: new Set(boardBoxes.map((board) => Math.round(board.getBoundingClientRect().left))).size,
    boards: boardBoxes.length,
    rowColumns: new Set(rows.map((row) => Math.round(row.getBoundingClientRect().left))).size,
    rowsShown: rows.length,
    maxRowWidth: rows.length ? Math.max(...rows.map((row) => box(row).width)) : null,
    maxTitleWidth: titles.length ? Math.max(...titles.map((title) => box(title).width)) : null,
    rowsOverlapped: coveredBy, panelsOverlapped: panelOverlap,
    clippedText: [...document.querySelectorAll(".mom-forum-title, .mom-forum-about, .mom-forum-numbers, .mom-forum-board-title, .mom-post-text, .mom-post-author, .mom-post-head, .mom-forum-panel *")]
      .filter(shown).filter((element) => element.scrollWidth > element.clientWidth + 1).map((element) => element.className).slice(0, 5),
    stickerFirstThing: stickers[0] && forum ? box(stickers[0]).top < box(forum).top - 1 : null,
    pageHeight: document.documentElement.scrollHeight,
  };
}

(async () => {
  const browser = await playwright.chromium.launch();
  const context = await browser.newContext({ viewport: { width: Number(width), height: 1000 } });
  const page = await context.newPage();
  await page.goto(origin + route, { waitUntil: "load" });
  await page.waitForTimeout(200);
  const result = await page.evaluate(measure);
  console.log(JSON.stringify(result));
  await browser.close();
})();
