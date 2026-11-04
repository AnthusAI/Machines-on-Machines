/* Machines on Machines: the small behaviours the design asks for. Everything else works without a script.
   1. Loop bands slide sideways with scroll position; neighbours go opposite ways; hotter topics (data-speed) go faster.
   2. A card image that fails to load is swapped for the same seeded placeholder art the server would have drawn.
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

  window.addEventListener("scroll", onScrollOrResize, { passive: true });
  window.addEventListener("resize", onScrollOrResize);
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("img[data-art-seed]").forEach(function (image) {
      if (image.complete && image.naturalWidth === 0) replaceBrokenImageWithArt(image);
    });
    onScrollOrResize();
  });
})();
