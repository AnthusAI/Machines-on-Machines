// Measure every advertisement on a page as a browser draws it: where its label, its picture and the column it sits in start and how wide they are,
// and the gap between the label and the picture. Prints JSON, one entry per ad.
//
//     node tools/measure_ad_slots.cjs http://127.0.0.1:8000 /field-notes/some-story/ 375
//
// Needs the `playwright` package (set PLAYWRIGHT_MODULE to its path when it is not installed beside this repository).
// Used by features/advertising.feature, whose browser scenarios skip themselves when Playwright is missing.
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, route, width, theme] = process.argv.slice(2);

function measure() {
  return [...document.querySelectorAll("[data-ad]")].filter((ad) => ad.getBoundingClientRect().height > 0).map((ad) => {
    const label = ad.querySelector(".mom-ad-label").getBoundingClientRect();
    const picture = [...ad.querySelectorAll("img")].find((image) => image.getBoundingClientRect().height > 0).getBoundingClientRect();
    const slot = ad.getBoundingClientRect();
    const parent = ad.parentElement;
    const parentStyle = getComputedStyle(parent);
    const parentBox = parent.getBoundingClientRect();
    const columnLeft = parentBox.left + parseFloat(parentStyle.paddingLeft);
    const columnWidth = parentBox.width - parseFloat(parentStyle.paddingLeft) - parseFloat(parentStyle.paddingRight);
    // The cards in the ad's own grid row: the story and reference cards that start within half a card of the ad's picture. Their pictures are the first thing in the card.
    const neighbourPictureTops = [...parent.children].filter((sibling) => sibling !== ad && sibling.matches(".mom-story-card, .mom-reference-card"))
      .filter((sibling) => Math.abs(sibling.getBoundingClientRect().top - picture.top) < 40)
      .map((sibling) => sibling.querySelector("img, .mom-art, iframe").getBoundingClientRect().top);
    return {
      neighbourPictureTops,
      unit: ad.dataset.adUnit, placement: ad.dataset.adPlacement, floated: getComputedStyle(ad).cssFloat !== "none",
      columnLeft, columnWidth, slotLeft: slot.left, slotWidth: slot.width,
      labelLeft: label.left, pictureLeft: picture.left, pictureWidth: picture.width, gap: picture.top - label.bottom, pictureTop: picture.top, labelTop: label.top,
    };
  });
}

(async () => {
  const browser = await playwright.chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: Number(width), height: 1000 }, colorScheme: theme || "light" })).newPage();
  await page.goto(origin + route, { waitUntil: "load" });
  await page.evaluate((chosen) => { document.documentElement.dataset.theme = chosen; document.querySelector("#papyrus-consent-banner")?.remove(); }, theme || "light");
  await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { scrollTo(0, y); await new Promise((resolve) => setTimeout(resolve, 40)); } scrollTo(0, 0); await document.fonts.ready; });
  await page.waitForTimeout(300);
  process.stdout.write(JSON.stringify(await page.evaluate(measure)));
  await browser.close();
})().catch((error) => { console.error(error.message); process.exit(1); });
