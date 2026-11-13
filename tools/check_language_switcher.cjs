// Exercise the language switcher and the welcoming banner in a browser. Prints JSON.
//
//     node tools/check_language_switcher.cjs http://127.0.0.1:8000 <scenario> <width>
//
// Scenarios (routes are the pages of tests/language_cases.py):
//   switcher    the control in the bar and the list in the menu on the three-language page, and whether the page scrolls sideways
//   offer       a Chinese-preferring browser on the English page: the banner, its countdown, and where the countdown ends
//   nothing     a Chinese-preferring browser on a page with no Chinese page, and on a page with no translation: no banner
//   primary     an English-preferring browser on the Spanish page: a "Read in English" link, and a clock that never moves the page
//   remember    Stay here is remembered across a reload and other pages; a switcher choice switches later pages with a note and Undo
//   noshift     the bar does not move when the banner appears
// Google Fonts requests are refused so layout is the same on every machine, and the countdown runs on Playwright's fake clock. Needs the `playwright`
// package (set PLAYWRIGHT_MODULE to its path). Used by the @browser scenarios of features/language-switcher.feature, which skip without it.
const playwright = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const [origin, scenario, width] = process.argv.slice(2);
const STEER = "/field-notes/steer-a-story/";
const STEER_ES = "/field-notes/steer-a-story-es/";
const STEER_ZH = "/field-notes/steer-a-story-zh/";
const MONITOR = "/field-notes/run-a-monitor/";
const UNTRANSLATED = "/field-notes/read-the-wire/";
const OTHER_ENGLISH_PAGE = MONITOR;

async function open(browser, { locale, clock = false, javaScript = true } = {}) {
  const context = await browser.newContext({ viewport: { width: Number(width), height: 900 }, locale: locale || "en-US", javaScriptEnabled: javaScript });
  const page = await context.newPage();
  await page.route(/fonts\.(googleapis|gstatic)\.com|googletagmanager\.com/, (route) => route.abort());
  if (clock) await page.clock.install();
  return { context, page };
}

const bannerFacts = () => {
  const banner = document.querySelector("[data-mom-language-banner]");
  if (!banner) return { present: false };
  const shown = (element) => element && !element.hidden && getComputedStyle(element).display !== "none" && element.getBoundingClientRect().width > 0;
  const actions = [...banner.querySelectorAll("[data-action]")].filter(shown).map((button) => ({ action: button.getAttribute("data-action"), text: button.textContent.trim() }));
  return {
    present: true, shown: shown(banner), mode: banner.getAttribute("data-mode"), lang: banner.getAttribute("lang"),
    message: banner.querySelector(".mom-language-banner-message").textContent, count: banner.querySelector(".mom-language-banner-count").textContent,
    live: banner.querySelector(".mom-language-banner-live").textContent, liveRole: banner.querySelector(".mom-language-banner-live").getAttribute("role"),
    liveAria: banner.querySelector(".mom-language-banner-live").getAttribute("aria-live"), actions,
    readHref: banner.querySelector('[data-action="read"]').getAttribute("href"),
    beforeMasthead: Boolean(banner.compareDocumentPosition(document.querySelector(".mom-masthead")) & Node.DOCUMENT_POSITION_FOLLOWING),
    height: banner.getBoundingClientRect().height, focusInside: banner.contains(document.activeElement),
  };
};

const pageFacts = () => ({
  path: location.pathname, lang: document.documentElement.lang, overflowX: document.documentElement.scrollWidth > innerWidth + 1,
  stored: (() => { try { return localStorage.getItem("papyrus.readingLanguage"); } catch (error) { return "blocked"; } })(),
});

const switcherFacts = () => {
  const visible = (element) => element && getComputedStyle(element).display !== "none" && element.getBoundingClientRect().width > 0;
  const trigger = document.querySelector(".mom-language-trigger");
  const options = (selector) => [...document.querySelectorAll(selector)].map((link) => ({
    text: link.querySelector(".mom-language-name").textContent, lang: link.getAttribute("lang"), hreflang: link.getAttribute("hreflang"),
    href: link.getAttribute("href"), current: link.getAttribute("aria-current"), mark: Boolean(link.querySelector('[data-icon="check"]')),
    box: link.getBoundingClientRect().toJSON(), fontSize: parseFloat(getComputedStyle(link).fontSize),
  }));
  const triggerBox = trigger.getBoundingClientRect();
  return {
    triggerShown: visible(trigger), triggerName: trigger.getAttribute("aria-label"), triggerText: trigger.textContent.trim(), currentNameShown: visible(trigger.querySelector(".mom-language-current")),
    triggerBox: triggerBox.toJSON(), triggerHasIcon: Boolean(trigger.querySelector('[data-icon="languages"]')),
    barOptions: options(".mom-language-list .mom-language-option"), menuOptions: options(".mom-menu-language-list .mom-language-option"),
    menuButtonShown: visible(document.querySelector(".mom-menu-button")), viewport: innerWidth, overflowX: document.documentElement.scrollWidth > innerWidth + 1,
    barRight: document.querySelector(".mom-nav").getBoundingClientRect().right,
  };
};

async function runSwitcher(browser) {
  const { context, page } = await open(browser);
  await page.goto(origin + STEER, { waitUntil: "load" });
  const result = { initial: await page.evaluate(switcherFacts) };
  await page.locator(".mom-language-trigger").focus();
  result.focusOutline = await page.evaluate(() => { const style = getComputedStyle(document.querySelector(".mom-language-trigger")); return { style: style.outlineStyle, width: parseFloat(style.outlineWidth) }; });
  await page.keyboard.press("Enter");
  result.afterOpen = { open: await page.evaluate(() => document.querySelector(".mom-language-details").open), facts: await page.evaluate(switcherFacts) };
  result.listInside = await page.evaluate(() => { const box = document.querySelector(".mom-language-list").getBoundingClientRect(); return box.left >= 0 && box.right <= innerWidth; });
  await page.keyboard.press("Escape");
  result.afterEscape = { open: await page.evaluate(() => document.querySelector(".mom-language-details").open), focusOnTrigger: await page.evaluate(() => document.activeElement.classList.contains("mom-language-trigger")) };
  if (result.initial.menuButtonShown) {
    await page.locator(".mom-menu-button").click();
    result.menuOpen = await page.evaluate(() => { const section = document.querySelector(".mom-menu-languages"); return { shown: Boolean(section) && section.getBoundingClientRect().height > 0, title: section.querySelector("h2").textContent.trim() }; });
    await page.evaluate(() => document.querySelector(".mom-menu").scrollTo(0, 99999));
    result.menuOptions = await page.evaluate(switcherFacts).then((facts) => facts.menuOptions);
  }
  const noScript = await open(browser, { javaScript: false });
  await noScript.page.goto(origin + STEER, { waitUntil: "load" });
  result.withoutJavaScript = await noScript.page.evaluate(switcherFacts);
  await noScript.context.close();
  await context.close();
  return result;
}

async function runOffer(browser) {
  const { context, page } = await open(browser, { locale: "zh-CN", clock: true });
  await page.goto(origin + STEER, { waitUntil: "load" });
  const result = { atLoad: await page.evaluate(bannerFacts), page: await page.evaluate(pageFacts) };
  await page.clock.runFor(4000);
  result.afterFourSeconds = await page.evaluate(bannerFacts);
  await page.getByRole("button", { name: result.atLoad.actions.find((action) => action.action === "pause").text }).click();
  await page.clock.runFor(30000);
  result.stillOnPageWhilePaused = (await page.evaluate(pageFacts)).path;
  result.pausedBanner = await page.evaluate(bannerFacts);
  await page.getByRole("button", { name: result.pausedBanner.actions.find((action) => action.action === "pause").text }).click();
  await page.clock.runFor(16000);
  await page.waitForURL(origin + STEER_ZH);
  result.arrived = await page.evaluate(pageFacts);
  result.historyLength = await page.evaluate(() => history.length);
  await context.close();
  return result;
}

async function runNothing(browser) {
  const result = {};
  const chinese = await open(browser, { locale: "zh-CN" });
  await chinese.page.goto(origin + MONITOR, { waitUntil: "load" });
  await chinese.page.waitForTimeout(300);
  result.noChinesePage = { banner: await chinese.page.evaluate(bannerFacts), page: await chinese.page.evaluate(pageFacts), options: (await chinese.page.evaluate(switcherFacts)).barOptions.map((option) => option.text) };
  await chinese.page.goto(origin + UNTRANSLATED, { waitUntil: "load" });
  result.untranslated = { banner: await chinese.page.evaluate(bannerFacts), hasSwitcher: await chinese.page.evaluate(() => Boolean(document.querySelector(".mom-language-switcher"))), page: await chinese.page.evaluate(pageFacts) };
  await chinese.context.close();
  const traditional = await open(browser, { locale: "zh-TW" });
  await traditional.page.goto(origin + STEER, { waitUntil: "load" });
  await traditional.page.waitForTimeout(300);
  result.traditionalChinese = await traditional.page.evaluate(bannerFacts);
  await traditional.context.close();
  const spanish = await open(browser, { locale: "es-MX" });
  await spanish.page.goto(origin + STEER, { waitUntil: "load" });
  await spanish.page.waitForTimeout(300);
  result.spanishRegion = await spanish.page.evaluate(bannerFacts);
  await spanish.context.close();
  return result;
}

async function runPrimary(browser) {
  const { context, page } = await open(browser, { locale: "en-US", clock: true });
  await page.goto(origin + STEER_ES, { waitUntil: "load" });
  const result = { atLoad: await page.evaluate(bannerFacts), page: await page.evaluate(pageFacts) };
  await page.clock.runFor(120000);
  result.afterTwoMinutes = { banner: await page.evaluate(bannerFacts), page: await page.evaluate(pageFacts) };
  const chinese = await open(browser, { locale: "zh-CN", clock: true });
  await chinese.page.goto(origin + STEER_ZH, { waitUntil: "load" });
  await chinese.page.clock.runFor(120000);
  result.chinesePageChinesePreference = await chinese.page.evaluate(bannerFacts);
  await chinese.context.close();
  await context.close();
  return result;
}

async function runRemember(browser) {
  const result = {};
  const { context, page } = await open(browser, { locale: "zh-CN", clock: true });
  await page.goto(origin + STEER, { waitUntil: "load" });
  await page.getByRole("button", { name: "留在此页" }).click();
  result.afterStay = { banner: await page.evaluate(bannerFacts), page: await page.evaluate(pageFacts) };
  await page.reload({ waitUntil: "load" });
  await page.clock.runFor(20000);
  result.afterReload = { banner: await page.evaluate(bannerFacts), page: await page.evaluate(pageFacts) };
  await page.goto(origin + OTHER_ENGLISH_PAGE, { waitUntil: "load" });
  result.otherEnglishPage = { banner: await page.evaluate(bannerFacts), page: await page.evaluate(pageFacts) };
  await context.close();

  // a visitor with an English browser picks Chinese in the switcher; the next page they open that exists in Chinese opens in Chinese, with a note and Undo
  const picker = await open(browser, { locale: "en-US" });
  await picker.page.goto(origin + STEER, { waitUntil: "load" });
  await picker.page.locator(".mom-language-trigger").click();
  await picker.page.locator('.mom-language-list a[lang="zh-Hans"]').click();
  await picker.page.waitForURL(origin + STEER_ZH);
  result.afterPick = await picker.page.evaluate(pageFacts);
  await picker.page.goto(origin + STEER, { waitUntil: "load" });
  await picker.page.waitForURL(origin + STEER_ZH);
  result.remembered = { page: await picker.page.evaluate(pageFacts), banner: await picker.page.evaluate(bannerFacts), history: await picker.page.evaluate(() => history.length) };
  await picker.page.getByRole("button", { name: "撤销" }).click();
  await picker.page.waitForURL(origin + STEER);
  result.afterUndo = await picker.page.evaluate(pageFacts);
  await picker.page.waitForTimeout(300);
  result.afterUndoBanner = await picker.page.evaluate(bannerFacts);
  // the remembered language wins for a page that does not exist in it: the untranslated and the no-Chinese pages stay as they are
  await picker.page.evaluate(() => localStorage.setItem("papyrus.readingLanguage", "zh-Hans"));
  await picker.page.goto(origin + MONITOR, { waitUntil: "load" });
  await picker.page.waitForTimeout(300);
  result.rememberedButNoPage = { page: await picker.page.evaluate(pageFacts), banner: await picker.page.evaluate(bannerFacts) };
  await picker.context.close();

  // storage that throws: the page still works and the banner still offers
  const blocked = await browser.newContext({ viewport: { width: Number(width), height: 900 }, locale: "zh-CN" });
  await blocked.addInitScript(() => { Object.defineProperty(window, "localStorage", { get() { throw new Error("blocked"); } }); Object.defineProperty(window, "sessionStorage", { get() { throw new Error("blocked"); } }); });
  const blockedPage = await blocked.newPage();
  await blockedPage.route(/fonts\.(googleapis|gstatic)\.com|googletagmanager\.com/, (route) => route.abort());
  const errors = [];
  blockedPage.on("pageerror", (error) => errors.push(String(error)));
  await blockedPage.goto(origin + STEER, { waitUntil: "load" });
  await blockedPage.waitForTimeout(300);
  result.storageBlocked = { banner: await blockedPage.evaluate(bannerFacts), errors };
  await blocked.close();
  return result;
}

async function runNoShift(browser) {
  const result = {};
  for (const [name, locale, route] of [["offer", "zh-CN", STEER], ["none", "en-US", STEER]]) {
    const { context, page } = await open(browser, { locale });
    await page.addInitScript(() => {
      window.__tops = [];
      window.__shifts = 0;
      new PerformanceObserver((list) => { for (const entry of list.getEntries()) if (!entry.hadRecentInput) window.__shifts += entry.value; }).observe({ type: "layout-shift", buffered: true });
      const record = () => { const bar = document.querySelector(".mom-nav"); if (bar) window.__tops.push(Math.round(bar.getBoundingClientRect().top)); requestAnimationFrame(record); };
      requestAnimationFrame(record);
    });
    await page.goto(origin + route, { waitUntil: "load" });
    await page.waitForTimeout(800);
    result[name] = await page.evaluate(() => ({ tops: [...new Set(window.__tops)], shifts: window.__shifts, banner: (document.querySelector("[data-mom-language-banner]") || {}).hidden === false }));
    await context.close();
  }
  return result;
}

(async () => {
  const browser = await playwright.chromium.launch();
  const runners = { switcher: runSwitcher, offer: runOffer, nothing: runNothing, primary: runPrimary, remember: runRemember, noshift: runNoShift };
  const result = await runners[scenario](browser);
  await browser.close();
  console.log(JSON.stringify(result));
})().catch((error) => { console.error(error); process.exit(1); });
