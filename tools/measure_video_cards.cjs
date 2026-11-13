// Measure and exercise the click-to-play video cards on a page as a browser draws them. Prints JSON.
//
//     node tools/measure_video_cards.cjs http://127.0.0.1:8000 /videos/ 1440
//
// Before any press it reports how many players the page has loaded and how the sideways rows are drawn; then it presses the first Play button, a second one
// by pointer and a third from the keyboard, reporting after each what the cards and the page look like. Requests to the video platforms are recorded and
// refused, so nothing leaves the machine. Needs the `playwright` package (set PLAYWRIGHT_MODULE to its path). Used by the @browser scenarios of
// features/video-cards.feature, which skip themselves without it.
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, route, width] = process.argv.slice(2);
const PLATFORM_HOSTS = /youtube-nocookie\.com|player\.vimeo\.com/;

function lookAtPage() {
  const shown = (element) => getComputedStyle(element).display !== "none" && element.getBoundingClientRect().width > 0;
  const rows = [...document.querySelectorAll(".mom-video-row")].map((row) => {
    const window_ = row.getBoundingClientRect();
    const cards = [...row.children].map((item) => item.getBoundingClientRect());
    const buttons = [...row.closest(".mom-video-section").querySelectorAll(".mom-video-scroll-button")];
    return {
      cards: cards.length,
      scrolls: row.scrollWidth > row.clientWidth + 1,
      snapType: getComputedStyle(row).scrollSnapType,
      overflowX: getComputedStyle(row).overflowX,
      nextCardPartlyShown: cards.some((card) => card.left < window_.right - 1 && card.right > window_.right + 1),
      wholeCardsShown: cards.filter((card) => card.left >= window_.left - 1 && card.right <= window_.right + 1).length,
      scrollButtonsDrawn: buttons.filter(shown).length,
      scrollButtonsDisabled: buttons.map((button) => button.disabled),
    };
  });
  const posters = [...document.querySelectorAll(".mom-video-poster")];
  const unnamed = posters.filter((poster) => !/^Play: .+/.test(poster.getAttribute("aria-label") || "")).length;
  return {
    width: innerWidth,
    overflowX: document.documentElement.scrollWidth > innerWidth + 1,
    frames: document.querySelectorAll("iframe").length,
    posters: posters.length,
    unnamedPosters: unnamed,
    rows,
  };
}

function lookAtCard(index) {
  const cards = [...document.querySelectorAll(".mom-reference-card-video")];
  const card = cards[index];
  const media = card.querySelector(".mom-media");
  const frame = card.querySelector("iframe");
  const box = card.getBoundingClientRect();
  const mediaBox = media.getBoundingClientRect();
  return {
    height: box.height, width: box.width, mediaHeight: mediaBox.height, mediaWidth: mediaBox.width,
    frame: Boolean(frame), frameSource: frame ? frame.src : null, frameTitle: frame ? frame.title : null,
    posterShown: Boolean(card.querySelector(".mom-video-poster")),
    focusedIsFrame: Boolean(frame) && document.activeElement === frame,
    frames: document.querySelectorAll("iframe").length,
    overflowX: document.documentElement.scrollWidth > innerWidth + 1,
  };
}

(async () => {
  const browser = await playwright.chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: Number(width), height: 1000 } })).newPage();
  const requested = [];
  await page.route(PLATFORM_HOSTS, (request) => { requested.push(request.request().url()); return request.abort(); });
  await page.goto(origin + route, { waitUntil: "load" });
  await page.waitForTimeout(300);
  const result = { atLoad: await page.evaluate(lookAtPage), requestedAtLoad: requested.length };
  const posterCount = result.atLoad.posters;
  if (posterCount >= 3) {
    const before = await page.evaluate(lookAtCard, 0);
    await page.locator(".mom-video-poster").first().scrollIntoViewIfNeeded();
    await page.locator(".mom-video-poster").first().click();
    await page.waitForTimeout(200);
    result.first = { before, after: await page.evaluate(lookAtCard, 0) };
    result.requestedAfterFirst = [...requested];
    await page.locator(".mom-video-poster").first().scrollIntoViewIfNeeded();
    await page.locator(".mom-video-poster").first().click();
    await page.waitForTimeout(200);
    result.second = { firstCard: await page.evaluate(lookAtCard, 0), secondCard: await page.evaluate(lookAtCard, 1) };
    await page.locator(".mom-video-poster").nth(1).focus();
    await page.keyboard.press("Enter");
    await page.waitForTimeout(200);
    result.keyboard = { secondCard: await page.evaluate(lookAtCard, 1), thirdCard: await page.evaluate(lookAtCard, 2) };
    result.requestedAfterKeyboard = [...requested];
  }
  console.log(JSON.stringify(result));
  await browser.close();
})();
