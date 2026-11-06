// Measure every content image on a page as a browser draws it. Prints JSON.
//
//     node tools/measure_images.cjs http://127.0.0.1:8000 / 375
//
// Needs the `playwright` package (set PLAYWRIGHT_MODULE to its path when it is not installed beside this repository).
// Used by features/image-ratio.feature, whose browser scenarios skip themselves when Playwright is missing.
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, route, width] = process.argv.slice(2);

function measure() {
  const rhythm = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--rhythm"));
  const ratioMedia = 16 / 9;
  const images = [];
  for (const image of document.querySelectorAll(".mom-card-image")) {
    if (image.closest(".mom-article-hero-band")) continue; // the one decorative strip, documented as an exception
    const box = image.getBoundingClientRect();
    if (box.width < 8) continue;
    const frame = image.closest(".mom-media");
    const frameBox = frame.getBoundingClientRect();
    const square = image.classList.contains("mom-card-image-square");
    const snapped = square ? box.width : Math.floor(box.width / ratioMedia / rhythm + 1e-6) * rhythm;
    images.push({
      square,
      width: box.width,
      height: box.height,
      ratio: box.width / box.height,
      multipleOfRhythm: Math.abs(box.height / rhythm - Math.round(box.height / rhythm)) < 0.02,
      // The height its own width asks for. A taller image has been stretched by whatever sits beside it.
      heightFromItsOwnWidth: snapped,
      stretched: box.height - snapped > 0.6,
      frameHeight: frameBox.height,
      fillsItsFrame: Math.abs(frameBox.height - box.height) < 0.6 && Math.abs(frameBox.width - box.width) < 0.6,
    });
  }
  return { rhythm, images };
}

(async () => {
  const browser = await playwright.chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: Number(width), height: 1000 } })).newPage();
  await page.goto(origin + route, { waitUntil: "load" });
  await page.waitForTimeout(200);
  console.log(JSON.stringify(await page.evaluate(measure)));
  await browser.close();
})();
