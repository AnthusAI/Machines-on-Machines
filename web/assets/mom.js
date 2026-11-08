/* Machines on Machines: the small behaviours the design asks for. Everything else works without a script.
   1. Loop bands slide sideways with scroll position; neighbours go opposite ways; hotter topics (data-speed) go faster.
   2. A card image that fails to load is swapped for the same seeded placeholder art the server would have drawn.
   3. The navigation bar shows the destinations that fit and moves the rest into a full-page menu behind the menu button.
   4. On a phone the lead headline takes the largest size at which it fits the card, so its lines fill the width.
   Under prefers-reduced-motion the bands stay still. */
(function () {
  "use strict";

  var reducedMotionQuery = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  var BAND_PIXELS_PER_SCROLL_PIXEL = 0.35;

  function clampBetweenZeroAndOne(value) {
    return Math.max(0, Math.min(1, value));
  }

  function moveBands() {
    if (reducedMotionQuery && reducedMotionQuery.matches) return;
    document.querySelectorAll(".mom-band").forEach(function (band, bandIndex) {
      var row = band.querySelector(".mom-band-row");
      if (!row) return;
      var repeatCount = Number(band.getAttribute("data-repeat")) || 4;
      var speed = Number(band.getAttribute("data-speed")) || 1;
      var patternWidth = row.scrollWidth / repeatCount;
      if (!patternWidth) return;
      var distance = (window.scrollY * BAND_PIXELS_PER_SCROLL_PIXEL * speed) % patternWidth;
      var offset = bandIndex % 2 === 0 ? -distance : distance - patternWidth;
      row.style.transform = "translateX(" + offset.toFixed(1) + "px)";
    });
  }

  var FNV_OFFSET_BASIS = 0x811c9dc5;
  var FNV_PRIME = 0x01000193;
  var compositionShapeCounts = { "sun-slab": 2, "rising": 1, "eclipse": 1, "moon": 1, "horizon": 1, "pages": 3 };
  var generalCompositions = ["sun-slab", "rising", "eclipse", "moon", "horizon"];
  var tones = ["brand", "machine", "human"];

  function hashSeed(seed) {
    var bytes = new TextEncoder().encode(String(seed || ""));
    var hashValue = FNV_OFFSET_BASIS;
    for (var byteIndex = 0; byteIndex < bytes.length; byteIndex++) {
      hashValue ^= bytes[byteIndex];
      hashValue = Math.imul(hashValue, FNV_PRIME) >>> 0;
    }
    return hashValue >>> 0;
  }

  function replaceBrokenImageWithArt(image) {
    if (image.dataset.artReplaced) return;
    var hashValue = hashSeed(image.getAttribute("data-art-seed"));
    var composition = image.getAttribute("data-art-kind") === "paper" ? "pages" : generalCompositions[hashValue % generalCompositions.length];
    var tone = tones[(hashValue >>> 8) % tones.length];
    var art = document.createElement("span");
    art.className = image.className.replace(/\s*\bmom-art[\w-]*/g, "") + " mom-art mom-art-" + composition + " mom-art-tone-" + tone;
    art.setAttribute("aria-hidden", "true");
    art.setAttribute("data-composition", composition);
    art.setAttribute("data-tone", tone);
    for (var shapeIndex = 1; shapeIndex <= compositionShapeCounts[composition]; shapeIndex++) {
      var shape = document.createElement("span");
      shape.className = "mom-art-shape mom-art-shape-" + shapeIndex;
      art.appendChild(shape);
    }
    image.dataset.artReplaced = "true";
    image.replaceWith(art);
  }

  document.addEventListener("error", function (event) {
    var target = event.target;
    if (target && target.tagName === "IMG" && target.hasAttribute("data-art-seed")) replaceBrokenImageWithArt(target);
  }, true);

  function onScrollOrResize() {
    moveBands();
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    var field = document.createElement("textarea");
    field.value = text;
    field.setAttribute("readonly", "");
    field.style.position = "fixed";
    field.style.opacity = "0";
    document.body.appendChild(field);
    field.select();
    var copied = document.execCommand("copy");
    document.body.removeChild(field);
    return copied ? Promise.resolve() : Promise.reject(new Error("copy failed"));
  }

  function setUpShare(share) {
    var toggle = share.querySelector(":scope > button");
    var panel = share.querySelector(".mom-share-panel");
    var status = share.querySelector(".mom-share-status");
    function setOpen(open) {
      panel.hidden = !open;
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (!open) status.textContent = "";
    }
    toggle.addEventListener("click", function () { setOpen(panel.hidden); });
    document.addEventListener("click", function (event) { if (!share.contains(event.target)) setOpen(false); });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !panel.hidden) { setOpen(false); toggle.focus(); }
    });
    panel.querySelectorAll("[data-share-path]").forEach(function (button) {
      button.addEventListener("click", function () {
        var address = new URL(button.getAttribute("data-share-path"), window.location.origin).href;
        if (navigator.share) {
          navigator.share({ title: share.getAttribute("data-title") || document.title, url: address }).then(function () { setOpen(false); }, function () {});
          return;
        }
        copyText(address).then(
          function () { status.textContent = "Link copied"; },
          function () { status.textContent = address; }
        );
      });
    });
  }

  document.querySelectorAll("[data-mom-share]").forEach(setUpShare);

  /* 3. The navigation bar and its menu. The head script has already set `mom-js` on <html>. The bar shows as many destinations as fit after the logo and
     marks the rest data-buried; the menu button appears when anything is buried (or on a phone, where the stylesheet hides the destinations). The menu is a
     full-page panel: it locks the page behind it, traps Tab, closes on Escape or on choosing a destination, and gives focus back to the button. */
  function setUpMenu(nav) {
    var header = nav.closest(".mom-masthead");
    var list = nav.querySelector(".mom-nav-items");
    var button = nav.querySelector(".mom-menu-button");
    var panel = button && document.getElementById(button.getAttribute("aria-controls"));
    if (!header || !list || !button || !panel) return;
    var root = document.documentElement;

    function fit() {
      var items = Array.prototype.slice.call(list.children);
      items.forEach(function (item) { item.removeAttribute("data-buried"); });
      nav.setAttribute("data-overflow", "none");
      if (getComputedStyle(list).display === "none") {
        nav.setAttribute("data-overflow", "some");
        return;
      }
      if (list.scrollWidth <= list.clientWidth + 1) return;
      nav.setAttribute("data-overflow", "some");
      for (var index = items.length - 1; index >= 0 && list.scrollWidth > list.clientWidth + 1; index--) {
        items[index].setAttribute("data-buried", "");
      }
    }

    function place() {
      panel.style.setProperty("--mom-menu-top", Math.max(0, Math.round(header.getBoundingClientRect().bottom)) + "px");
    }

    function setOpen(open, returnFocus) {
      if (open === !panel.hidden) return;
      panel.hidden = !open;
      button.setAttribute("aria-expanded", open ? "true" : "false");
      root.classList.toggle("mom-menu-open", open);
      if (open) {
        place();
        var first = panel.querySelector("a[href]");
        if (first) first.focus();
      } else if (returnFocus) {
        button.focus();
      }
    }

    function focusable() {
      return [button].concat(Array.prototype.slice.call(panel.querySelectorAll("a[href]")));
    }

    button.addEventListener("click", function () { setOpen(panel.hidden, true); });
    panel.addEventListener("click", function (event) {
      if (event.target.closest && event.target.closest("a")) setOpen(false, true);
    });
    document.addEventListener("keydown", function (event) {
      if (panel.hidden) return;
      if (event.key === "Escape") { event.preventDefault(); setOpen(false, true); return; }
      if (event.key !== "Tab") return;
      var stops = focusable();
      var position = stops.indexOf(document.activeElement);
      if (position === -1) { event.preventDefault(); stops[event.shiftKey ? stops.length - 1 : 0].focus(); }
      else if (event.shiftKey && position === 0) { event.preventDefault(); stops[stops.length - 1].focus(); }
      else if (!event.shiftKey && position === stops.length - 1) { event.preventDefault(); stops[0].focus(); }
    });
    window.addEventListener("pageshow", function () { setOpen(false, false); });

    function refit() {
      fit();
      if (nav.getAttribute("data-overflow") !== "some") setOpen(false, false);
      else if (!panel.hidden) place();
    }
    refit();
    if (window.ResizeObserver) new ResizeObserver(refit).observe(nav);
    else window.addEventListener("resize", refit);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(refit);
  }

  /* 4. On a phone a long display headline wraps early and leaves the right of the card empty, because whole words are wide. The lead headline
        picks the largest size (up to 40% bigger) at which no line overflows, no last line is a lone word, and the lines fill the most width. */
  var PHONE_MAX_WIDTH = 639;
  function headlineLines(element) {
    var box = element.getBoundingClientRect();
    var range = document.createRange();
    range.selectNodeContents(element);
    var tops = {};
    Array.prototype.forEach.call(range.getClientRects(), function (rectangle) {
      var key = Math.round(rectangle.top);
      tops[key] = Math.max(tops[key] || 0, rectangle.right - box.left);
    });
    return { widths: Object.keys(tops).sort(function (a, b) { return a - b; }).map(function (key) { return tops[key]; }), box: box.width };
  }
  function fitHeadline(element) {
    element.style.fontSize = "";
    if (window.innerWidth > PHONE_MAX_WIDTH) return;
    var base = parseFloat(window.getComputedStyle(element).fontSize);
    var baseLines = headlineLines(element).widths.length;
    var best = null;
    for (var size = base; size <= Math.round(base * 1.4); size += 1) {
      element.style.fontSize = size + "px";
      var lines = headlineLines(element);
      var widest = Math.max.apply(null, lines.widths);
      var last = lines.widths[lines.widths.length - 1];
      if (widest > lines.box + 0.5) continue;
      if (lines.widths.length > baseLines + 1) continue;
      if (lines.widths.length > 1 && last < lines.box * 0.35) continue;
      var total = lines.widths.reduce(function (sum, width) { return sum + width; }, 0);
      var fill = total / (lines.widths.length * lines.box);
      if (!best || fill > best.fill + 0.005) best = { size: size, fill: fill };
    }
    element.style.fontSize = best ? best.size + "px" : "";
  }
  function fitLeadHeadlines() {
    document.querySelectorAll(".mom-story-card-lead .mom-story-card-headline").forEach(fitHeadline);
  }
  fitLeadHeadlines();
  window.addEventListener("resize", fitLeadHeadlines);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitLeadHeadlines);

  document.querySelectorAll(".mom-nav").forEach(setUpMenu);

  window.addEventListener("scroll", onScrollOrResize, { passive: true });
  window.addEventListener("resize", onScrollOrResize);
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("img[data-art-seed]").forEach(function (image) {
      if (image.complete && image.naturalWidth === 0) replaceBrokenImageWithArt(image);
    });
    onScrollOrResize();
  });
})();
