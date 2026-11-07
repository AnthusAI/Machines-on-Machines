// Drive the navigation as a browser draws it. Prints JSON.
//
//     node tools/check_nav.cjs http://127.0.0.1:8000 /videos/ 375 [nojs]
//
// Needs the `playwright` package (set PLAYWRIGHT_MODULE to its path when it is not installed beside this repository).
// Used by features/navigation.feature, whose browser scenarios skip themselves when Playwright is missing.
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, route, width, mode] = process.argv.slice(2);

(async () => {
  const browser = await playwright.chromium.launch();
  const context = await browser.newContext({ viewport: { width: Number(width), height: 900 }, javaScriptEnabled: mode !== "nojs" });
  const page = await context.newPage();
  await page.goto(origin + route, { waitUntil: "load" });
  await page.waitForTimeout(300);
  const visible = (selector) => page.$$eval(selector, (nodes) => nodes.filter((node) => node.offsetWidth > 0 && node.offsetHeight > 0).map((node) => ({ text: (node.getAttribute("aria-label") || node.textContent).trim(), href: node.getAttribute("href") })));
  const result = {
    barItems: await visible(".mom-nav-items a"),
    brandVisible: (await visible(".mom-brand-pill")).length > 0,
    buttonVisible: (await visible(".mom-menu-button")).length > 0,
    pageWidth: await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]),
  };
  if (mode !== "nojs" && result.buttonVisible) {
    const button = page.locator(".mom-menu-button");
    result.button = await button.evaluate((node) => ({ name: node.getAttribute("aria-label"), tag: node.tagName, controls: node.getAttribute("aria-controls"), expanded: node.getAttribute("aria-expanded"), icon: node.querySelector(".mom-icon-menu").getBoundingClientRect().width > 0 }));
    await button.click();
    await page.waitForTimeout(300);
    result.open = await page.evaluate(() => {
      const panel = document.querySelector(".mom-menu");
      const header = document.querySelector(".mom-masthead").getBoundingClientRect();
      const box = panel.getBoundingClientRect();
      const button = document.querySelector(".mom-menu-button");
      return {
        expanded: button.getAttribute("aria-expanded"),
        closeIcon: button.querySelector(".mom-icon-close").getBoundingClientRect().width > 0,
        panelTop: box.top, panelBottom: box.bottom, headerBottom: header.bottom, viewportHeight: innerHeight, panelPosition: getComputedStyle(panel).position,
        pageOverflow: getComputedStyle(document.documentElement).overflow,
        focusInPanel: panel.contains(document.activeElement),
        items: [...panel.querySelectorAll(".mom-menu-link")].map((link) => ({
          name: link.querySelector(".mom-menu-name").textContent, subtitle: (link.querySelector(".mom-menu-sub") || { textContent: "" }).textContent, href: link.getAttribute("href"),
          current: link.getAttribute("aria-current"), here: !!link.querySelector(".mom-menu-here"),
          height: link.getBoundingClientRect().height,
          nameSize: parseFloat(getComputedStyle(link.querySelector(".mom-menu-name")).fontSize),
          subtitleSize: parseFloat(getComputedStyle(link.querySelector(".mom-menu-sub") || link).fontSize),
        })),
      };
    });
    const stops = result.open.items.length + 1;
    const staysInside = async (key, count) => {
      for (let step = 0; step < count; step++) {
        await page.keyboard.press(key);
        const inside = await page.evaluate(() => { const active = document.activeElement; return active === document.querySelector(".mom-menu-button") || document.querySelector(".mom-menu").contains(active); });
        if (!inside) return false;
      }
      return true;
    };
    result.trap = { forward: await staysInside("Tab", stops * 2 + 1), backward: await staysInside("Shift+Tab", stops * 2 + 1) };
    await page.keyboard.press("Escape");
    await page.waitForTimeout(100);
    result.escape = await page.evaluate(() => ({ hidden: document.querySelector(".mom-menu").hidden, focusOnButton: document.activeElement === document.querySelector(".mom-menu-button"), expanded: document.querySelector(".mom-menu-button").getAttribute("aria-expanded"), locked: document.documentElement.classList.contains("mom-menu-open") }));
    await page.evaluate(() => document.addEventListener("click", (event) => event.preventDefault(), true));
    await button.click();
    await page.locator(".mom-menu-link").first().click();
    result.afterChoosing = await page.evaluate(() => ({ hidden: document.querySelector(".mom-menu").hidden, focusOnButton: document.activeElement === document.querySelector(".mom-menu-button") }));
  }
  console.log(JSON.stringify(result));
  await browser.close();
})();
