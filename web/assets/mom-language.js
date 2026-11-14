/* Language switching for pages that exist in more than one language. Loaded in the head, without `defer`, on those pages only, so a remembered choice
   switches the page before it is drawn. It reads the page's own translations from <link rel="alternate" hreflang> (the page lists itself too) and the
   words it needs from the JSON in #mom-language-data, so it makes no request.

   1. A remembered reading language (localStorage "papyrus.readingLanguage", set only by a visitor's action) wins: a page that exists in it is replaced by
      it at once, with a quiet "Switched to ..." note and Undo on the page that opens; a page that does not exist in it is left alone.
   2. Otherwise the browser's language list is matched against the page's languages. A different language the page exists in gets a banner with a 15 second
      countdown; the countdown never goes toward the site's primary language (a quiet "Read in ..." link is offered instead), so a crawler that runs
      scripts and prefers English cannot be sent away from a translated page.
   3. The language switcher in the bar stores the language the visitor picks and closes itself on Escape or an outside click.
   Everything is client side: no cookie, no request, and with localStorage blocked the page simply works and asks again. */
(function () {
  "use strict";

  var READING_LANGUAGE_KEY = "papyrus.readingLanguage";
  var NOTE_KEY = "papyrus.languageNote";
  var LINK_DISMISSED_KEY = "papyrus.languageLinkDismissed";
  var COUNTDOWN_SECONDS = 15;
  var NOTE_VISIBLE_MILLISECONDS = 10000;
  var NOTE_MAXIMUM_AGE_MILLISECONDS = 15000;
  var root = document.documentElement;

  function read(storage, key) { try { return window[storage].getItem(key); } catch (error) { return null; } }
  function write(storage, key, value) {
    try {
      if (value === null) window[storage].removeItem(key); else window[storage].setItem(key, value);
    } catch (error) { /* private window or blocked storage: the choice is simply not remembered */ }
  }

  function dataFromPage() {
    var element = document.getElementById("mom-language-data");
    try { return element ? JSON.parse(element.textContent) : null; } catch (error) { return null; }
  }

  function translationsFromHead() {
    var found = [];
    Array.prototype.forEach.call(document.querySelectorAll('link[rel="alternate"][hreflang]'), function (link) {
      var tag = link.getAttribute("hreflang");
      if (tag === "x-default") return;
      try { found.push({ tag: tag, path: new URL(link.getAttribute("href"), location.href).pathname }); } catch (error) { /* an address that does not parse is not a translation */ }
    });
    return found;
  }

  /* Does a browser language preference mean this page language? zh-CN, zh-SG and zh-Hans are Simplified; zh-TW, zh-HK and zh-Hant are Traditional,
     which this site does not have, so they match nothing. Any es-* is Spanish. */
  function preferenceMeansLanguage(preference, tag) {
    var wanted = String(preference).toLowerCase();
    var offered = tag.toLowerCase();
    if (wanted === offered) return true;
    if (offered === "zh-hans") return wanted === "zh" || /^zh-(cn|sg|my|hans)(-|$)/.test(wanted);
    if (offered === "zh-hant") return /^zh-(tw|hk|mo|hant)(-|$)/.test(wanted);
    if (offered === "es-419") return wanted.split("-")[0] === "es"; /* the one Spanish edition is Latin American; any Spanish preference means it */
    return offered.indexOf("-") === -1 && wanted.split("-")[0] === offered;
  }

  function bestMatch(translations) {
    var preferences = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language];
    for (var index = 0; index < preferences.length; index++) {
      for (var offer = 0; offer < translations.length; offer++) {
        if (preferenceMeansLanguage(preferences[index], translations[offer].tag)) return translations[offer].tag;
      }
    }
    return null;
  }

  function pathFor(translations, tag) {
    for (var index = 0; index < translations.length; index++) if (translations[index].tag === tag) return translations[index].path;
    return null;
  }

  function track(from, to, method) {
    if (typeof window.gtag === "function") window.gtag("event", "language_switch", { from_language: from, to_language: to, method: method });
  }

  var translations = translationsFromHead();
  var data = dataFromPage();
  var pageTag = root.getAttribute("lang");
  if (translations.length < 2 || !data || !pageTag) return;
  var primary = data.primary;
  var plan = null; // what the banner should show once it is in the page

  var remembered = read("localStorage", READING_LANGUAGE_KEY);
  if (remembered && remembered !== pageTag && pathFor(translations, remembered)) {
    write("sessionStorage", NOTE_KEY, JSON.stringify({ to: remembered, from: pageTag, fromPath: location.pathname + location.search, at: Date.now() }));
    location.replace(pathFor(translations, remembered));
    return;
  }

  var note = null;
  try { note = JSON.parse(read("sessionStorage", NOTE_KEY)); } catch (error) { note = null; }
  write("sessionStorage", NOTE_KEY, null);
  if (note && note.to === pageTag && Date.now() - note.at < NOTE_MAXIMUM_AGE_MILLISECONDS) {
    plan = { mode: "note", language: pageTag, from: note.from, fromPath: note.fromPath };
  } else if (!remembered) {
    var best = bestMatch(translations);
    if (best && best !== pageTag) {
      if (best === primary) {
        if (!read("sessionStorage", LINK_DISMISSED_KEY)) plan = { mode: "read", language: primary, target: best };
      } else {
        plan = { mode: "offer", language: best, target: best };
      }
    }
  }

  function remember(tag) { write("localStorage", READING_LANGUAGE_KEY, tag); }

  function mountBanner() {
    var banner = document.querySelector("[data-mom-language-banner]");
    if (!banner || !plan || banner.getAttribute("data-mounted")) return;
    banner.setAttribute("data-mounted", "true");
    var strings = data.strings[plan.language];
    var message = banner.querySelector(".mom-language-banner-message");
    var count = banner.querySelector(".mom-language-banner-count");
    var live = banner.querySelector(".mom-language-banner-live");
    var progress = banner.querySelector(".mom-language-banner-progress");
    var buttons = {};
    Array.prototype.forEach.call(banner.querySelectorAll("[data-action]"), function (button) { buttons[button.getAttribute("data-action")] = button; });
    function label(name, text) { buttons[name].querySelector("span").textContent = text; }
    function show(names) {
      Object.keys(buttons).forEach(function (name) { buttons[name].hidden = names.indexOf(name) === -1; });
    }
    banner.setAttribute("lang", plan.language);
    banner.setAttribute("data-mode", plan.mode);
    banner.hidden = false;

    if (plan.mode === "read") {
      message.textContent = "";
      label("read", strings.readInThisLanguage);
      buttons.read.setAttribute("href", plan.target ? pathFor(translations, plan.target) : "#");
      buttons.read.setAttribute("lang", plan.language);
      buttons.read.setAttribute("hreflang", plan.language);
      label("stay", strings.dismiss);
      show(["read", "stay"]);
      progress.hidden = true;
      buttons.read.addEventListener("click", function () { remember(plan.target); track(pageTag, plan.target, "button"); });
      buttons.stay.addEventListener("click", function () { write("sessionStorage", LINK_DISMISSED_KEY, "yes"); banner.hidden = true; });
      return;
    }

    if (plan.mode === "note") {
      message.textContent = strings.switched;
      label("undo", strings.undo);
      label("stay", strings.dismiss);
      show(["undo", "stay"]);
      progress.hidden = true;
      track(plan.from, pageTag, "remembered");
      buttons.undo.addEventListener("click", function () {
        remember(plan.from);
        track(pageTag, plan.from, "undo");
        location.replace(plan.fromPath);
      });
      buttons.stay.addEventListener("click", function () { banner.hidden = true; });
      window.setTimeout(function () {
        if (banner.contains(document.activeElement) || banner.matches(":hover")) return;
        banner.classList.add("mom-language-banner-fading");
        window.setTimeout(function () { banner.hidden = true; }, 400);
      }, NOTE_VISIBLE_MILLISECONDS);
      return;
    }

    var target = plan.target;
    var remaining = COUNTDOWN_SECONDS * 1000;
    var running = true;
    var last = Date.now();
    var timer = null;
    message.textContent = strings.noticed;
    label("switch", strings.switchNow);
    label("stay", strings.stay);
    label("pause", strings.pause);
    show(["switch", "stay", "pause"]);
    progress.style.setProperty("--mom-language-countdown", COUNTDOWN_SECONDS + "s");
    live.textContent = strings.announce.replace("{seconds}", String(COUNTDOWN_SECONDS));

    function seconds() { return Math.max(0, Math.ceil(remaining / 1000)); }
    function draw() { count.textContent = running ? strings.countdown.replace("{seconds}", String(seconds())) : strings.paused; }
    function setRunning(next) {
      running = next;
      last = Date.now();
      banner.classList.toggle("mom-language-banner-paused", !running);
      label("pause", running ? strings.pause : strings.resume);
      draw();
    }
    function leave(method) {
      window.clearInterval(timer);
      remember(target);
      track(pageTag, target, method);
      location.replace(pathFor(translations, target));
    }
    timer = window.setInterval(function () {
      var now = Date.now();
      if (running) remaining -= now - last;
      last = now;
      draw();
      if (remaining <= 0) leave("countdown");
    }, 250);
    draw();

    buttons.switch.addEventListener("click", function () { leave("button"); });
    buttons.pause.addEventListener("click", function () { setRunning(!running); });
    buttons.stay.addEventListener("click", function () {
      window.clearInterval(timer);
      remember(pageTag);
      banner.hidden = true;
    });
    /* Reading has started: scrolling, typing or selecting text pauses the clock; the visitor can resume it or choose */
    function readerStarted(event) {
      if (!running || (event && event.target && banner.contains(event.target))) return;
      setRunning(false);
    }
    window.addEventListener("scroll", readerStarted, { passive: true });
    window.addEventListener("keydown", function (event) { if (event.key !== "Tab") readerStarted(event); });
    document.addEventListener("selectionchange", function () {
      var selection = window.getSelection();
      if (selection && !selection.isCollapsed) readerStarted(null);
    });
  }

  /* The switcher in the bar and the language list in the menu: store the choice; close the bar's list on Escape, on an outside click and on a choice */
  function setUpSwitchers() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-mom-language-switcher] a[data-language]"), function (link) {
      link.addEventListener("click", function () {
        var tag = link.getAttribute("data-language");
        remember(tag);
        if (tag !== pageTag) track(pageTag, tag, "switcher");
      });
    });
    var details = document.querySelector(".mom-language-details");
    if (!details) return;
    document.addEventListener("click", function (event) { if (details.open && !details.contains(event.target)) details.open = false; });
    details.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && details.open) { details.open = false; details.querySelector("summary").focus(); }
    });
    details.addEventListener("focusout", function (event) {
      if (details.open && event.relatedTarget && !details.contains(event.relatedTarget)) details.open = false;
    });
  }

  window.momLanguage = { mountBanner: mountBanner };
  document.addEventListener("DOMContentLoaded", function () { mountBanner(); setUpSwitchers(); });
}());
