/* Machines on Machines: the small behaviours the design asks for. Everything else works without a script.
   1. Loop bands slide sideways with scroll position; neighbours go opposite ways; hotter topics (data-speed) go faster.
   2. A card image that fails to load is swapped for the same seeded placeholder art the server would have drawn.
   3. The navigation bar shows the destinations that fit and moves the rest into a full-page menu behind the menu button.
   4. On a phone the lead headline takes the largest size at which it fits the card, so its lines fill the width.
   5. Times on the forum pages read "2h ago" (the exact moment stays in the title), and each forum board shows its first rows with a Load more button for the rest.
   6. The halftone panel under the site card prints an abstract picture as dots on a fixed grid: a big sun in blue ink and a smaller moon in warm ink.
      On the home page it reaches down beside the next section's heading, whose right side is empty (or, when the latest posts sit under the top row, to the
      bottom of the card's column), and up to just under the sentence above, lined up with its text.
      On Articles, Posts, Findings and Videos it fills the last column beside the first row, under the page header's card.
      Scrolling slides the picture under the grid, the sun up and the moon down; when scrolling stops, it stops.
   7. The latest posts sit beside the lead on very wide windows and under it, as a grid, on narrower ones; the Top Posts section further down leaves out the ones shown there.
   8. House ads report to Google Analytics: view_promotion once when half of an ad is on screen, select_promotion when its link is opened.
   Under prefers-reduced-motion the bands and the halftone stay still. */
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

  /* The halftone is drawn in designed pixels on a 360-wide picture and scaled to the page's rendered size (75% from 600px up). */
  var HALFTONE_DOT_PITCH = 30;
  var HALFTONE_PICTURE_WIDTH = 360;
  var HALFTONE_SMALLEST_DOT = 3;
  var HALFTONE_DOT_GROWTH = 31;
  var HALFTONE_SHORTEST_PANEL = 48;

  function halftoneSceneForScroll(scrollDistanceInDesignedPixels) {
    return {
      sunX: 330 - scrollDistanceInDesignedPixels * 0.12,
      sunY: -30 + scrollDistanceInDesignedPixels * 0.35,
      moonX: 60 + scrollDistanceInDesignedPixels * 0.06,
      moonY: 360 - scrollDistanceInDesignedPixels * 0.3
    };
  }

  function discStrength(x, heightAboveBottom, centerX, centerY, radius, softEdge) {
    var distance = Math.hypot(x - centerX, heightAboveBottom - centerY);
    return distance <= radius ? 1 : Math.max(0, 1 - (distance - radius) / softEdge);
  }

  function halftoneInkAtPoint(x, heightAboveBottom, scene) {
    var distanceFromSunCenter = Math.hypot(x - scene.sunX, heightAboveBottom - scene.sunY);
    var sun = discStrength(x, heightAboveBottom, scene.sunX, scene.sunY, 210, 70) * (0.75 + 0.25 * Math.max(0, 1 - distanceFromSunCenter / 210));
    var distanceFromMoonCenter = Math.hypot(x - scene.moonX, heightAboveBottom - scene.moonY);
    var moon = discStrength(x, heightAboveBottom, scene.moonX, scene.moonY, 120, 60) * (0.7 + 0.2 * Math.max(0, 1 - distanceFromMoonCenter / 120));
    var ground = 0.04 + 0.06 * ((x / HALFTONE_PICTURE_WIDTH) + (1 - Math.min(heightAboveBottom, 600) / 600)) / 2;
    if (sun >= moon && sun > ground) return { ink: "sun", strength: sun };
    if (moon > ground) return { ink: "warm", strength: moon };
    return { ink: "ground", strength: ground };
  }

  function renderedPixelsPerDesignedPixel() {
    return (parseFloat(getComputedStyle(document.documentElement).fontSize) || 16) / 16;
  }

  function setHalftoneLength(panel, propertyName, pixels) {
    var value = pixels.toFixed(1) + "px";
    if (panel.style.getPropertyValue(propertyName) !== value) panel.style.setProperty(propertyName, value);
  }

  /* Each edge of the panel moves by how far it is from where it belongs. The panel is absolutely placed, so it adds nothing to the height around it. */
  function moveHalftoneEdges(panel, desiredTop, desiredBottom, desiredLeft) {
    var panelBox = panel.getBoundingClientRect();
    var panelStyles = getComputedStyle(panel);
    setHalftoneLength(panel, "--mom-halftone-bottom", (parseFloat(panelStyles.bottom) || 0) + (panelBox.bottom - desiredBottom));
    setHalftoneLength(panel, "--mom-halftone-top", (parseFloat(panelStyles.top) || 0) + (desiredTop - panelBox.top));
    setHalftoneLength(panel, "--mom-halftone-left", (parseFloat(panelStyles.left) || 0) + (desiredLeft - panelBox.left));
  }

  /* On the home page the panel fits the space around it:
     its bottom reaches down beside the next section's heading (whose right side is empty) to the heading's bottom edge;
     its top sits under the sentence above by the same gap that separates its bottom from the card images below;
     its left edge lines up with the sentence's first letter. */
  function fitHomeHalftone(panel, topRow) {
    var nextGroup = topRow.parentElement.querySelector(".mom-home-top + .rh-features > .rh-group:first-child");
    var nextHeading = nextGroup && nextGroup.querySelector(":scope > .papyrus-group-head");
    var firstCardBelow = nextGroup && nextGroup.querySelector(":scope > .mom-story-card");
    var desiredBottom = nextHeading ? nextHeading.getBoundingClientRect().bottom : topRow.getBoundingClientRect().bottom;
    /* Narrower than very wide, the latest posts are a panel under the lead and the card, so the halftone stops at the bottom of the card's column */
    var side = panel.closest(".mom-home-side");
    var postsPanel = topRow.querySelector(":scope > .mom-home-posts");
    if (side && postsPanel && getComputedStyle(postsPanel).display !== "none" && postsPanel.getBoundingClientRect().top >= side.getBoundingClientRect().bottom - 1) {
      desiredBottom = side.getBoundingClientRect().bottom;
    }
    var gapAboveCardImages = nextHeading && firstCardBelow
      ? Math.max(0, firstCardBelow.getBoundingClientRect().top - nextHeading.getBoundingClientRect().bottom)
      : parseFloat(getComputedStyle(panel.parentElement).rowGap) || 0;
    var sentence = topRow.querySelector(".mom-home-purpose");
    if (!sentence) return;
    var sentenceText = document.createRange();
    sentenceText.selectNodeContents(sentence);
    var sentenceBox = sentenceText.getBoundingClientRect();
    moveHalftoneEdges(panel, sentenceBox.bottom + gapAboveCardImages, desiredBottom, sentenceBox.left);
  }

  /* Under the page header's site card (Articles, Posts, Findings, Videos) the panel fills the last column beside the first row, which stops one column short of it:
     its bottom is that row's bottom, its top sits under the card's lowest corner by the gap between columns, and its left edge is the column's left edge. */
  var ROW_BESIDE_PAGE_CARD = [
    ".mom-stories-section[data-rank='0'] > .papyrus-group-head + .mom-stories-row",
    ".mom-refs-lead > .mom-refs-row:first-of-type",
    ".mom-refs-section[data-rank='0'] > .mom-refs-row:first-of-type"
  ].join(", ");

  function fitPageTopHalftone(panel, pageTop) {
    var card = pageTop.querySelector(".mom-sticker");
    var rowBeside = pageTop.parentElement.querySelector(ROW_BESIDE_PAGE_CARD);
    if (!card || !rowBeside) {
      panel.setAttribute("data-too-short", "");
      return false;
    }
    var columnGap = parseFloat(getComputedStyle(pageTop).columnGap) || 0;
    var rowBox = rowBeside.getBoundingClientRect();
    moveHalftoneEdges(panel, card.getBoundingClientRect().bottom + columnGap, rowBox.bottom, rowBox.right + columnGap);
    return true;
  }

  function fitHalftoneToItsSurroundings(panel) {
    if (getComputedStyle(panel).display === "none") return false;
    var topRow = panel.closest(".mom-home-top");
    if (topRow) {
      fitHomeHalftone(panel, topRow);
      return true;
    }
    var pageTop = panel.closest(".mom-page-top");
    return pageTop ? fitPageTopHalftone(panel, pageTop) : true;
  }

  function drawHalftone(panel) {
    if (!fitHalftoneToItsSurroundings(panel)) return;
    var canvas = panel.querySelector(".mom-halftone-canvas");
    if (!canvas || !canvas.getContext) return;
    var renderedWidth = panel.clientWidth;
    var renderedHeight = panel.clientHeight;
    var designScale = renderedPixelsPerDesignedPixel();
    if (!renderedWidth || renderedHeight < HALFTONE_SHORTEST_PANEL * designScale) {
      panel.setAttribute("data-too-short", "");
      return;
    }
    panel.removeAttribute("data-too-short");
    var devicePixels = window.devicePixelRatio || 1;
    var canvasWidth = Math.round(renderedWidth * devicePixels);
    var canvasHeight = Math.round(renderedHeight * devicePixels);
    if (canvas.width !== canvasWidth || canvas.height !== canvasHeight) {
      canvas.width = canvasWidth;
      canvas.height = canvasHeight;
    }
    var context = canvas.getContext("2d");
    var pixelsPerDesignedPixel = devicePixels * designScale;
    context.setTransform(pixelsPerDesignedPixel, 0, 0, pixelsPerDesignedPixel, 0, 0);
    var width = renderedWidth / designScale;
    var height = renderedHeight / designScale;
    context.clearRect(0, 0, width, height);
    var styles = getComputedStyle(panel);
    var inks = {
      sun: styles.getPropertyValue("--brand-progress").trim(),
      warm: styles.getPropertyValue("--on-human-accent").trim(),
      ground: styles.getPropertyValue("--ink-muted").trim()
    };
    var holdStill = reducedMotionQuery && reducedMotionQuery.matches;
    var scene = halftoneSceneForScroll(holdStill ? 0 : window.scrollY / designScale);
    var pictureXPerPanelX = HALFTONE_PICTURE_WIDTH / width;
    for (var rowFromBottom = 0; (rowFromBottom - 1) * HALFTONE_DOT_PITCH <= height; rowFromBottom++) {
      var rowIsShifted = rowFromBottom % 2 === 1;
      var centerY = height - rowFromBottom * HALFTONE_DOT_PITCH;
      for (var centerX = rowIsShifted ? HALFTONE_DOT_PITCH / 2 : 0; centerX <= width + HALFTONE_DOT_PITCH; centerX += HALFTONE_DOT_PITCH) {
        var found = halftoneInkAtPoint(centerX * pictureXPerPanelX, rowFromBottom * HALFTONE_DOT_PITCH, scene);
        context.fillStyle = inks[found.ink];
        context.beginPath();
        context.arc(centerX, centerY, (HALFTONE_SMALLEST_DOT + found.strength * HALFTONE_DOT_GROWTH) / 2, 0, Math.PI * 2);
        context.fill();
      }
    }
  }

  var halftoneFrameRequested = false;
  function drawHalftonesOnNextFrame() {
    if (halftoneFrameRequested) return;
    halftoneFrameRequested = true;
    window.requestAnimationFrame(function () {
      halftoneFrameRequested = false;
      document.querySelectorAll(".mom-halftone").forEach(drawHalftone);
    });
  }

  function setUpHalftones() {
    var panels = document.querySelectorAll(".mom-halftone");
    if (!panels.length) return;
    if (window.ResizeObserver) {
      var observer = new ResizeObserver(drawHalftonesOnNextFrame);
      panels.forEach(function (panel) {
        observer.observe(panel);
        /* The page header's panel follows the first row beside it, which grows as its pictures load */
        var page = panel.closest(".mom-page-top") && panel.closest(".mom-page");
        if (page) observer.observe(page);
      });
    }
    if (window.matchMedia) {
      var darkQuery = window.matchMedia("(prefers-color-scheme: dark)");
      if (darkQuery.addEventListener) darkQuery.addEventListener("change", drawHalftonesOnNextFrame);
    }
    if (window.MutationObserver) {
      new MutationObserver(drawHalftonesOnNextFrame).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "class"] });
    }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawHalftonesOnNextFrame);
    drawHalftonesOnNextFrame();
  }

  /* 7. The latest posts sit beside the home page's lead on very wide windows, showing only the whole ones that fit, and under it as a grid of whole rows on
     narrower ones. The Top Posts section further down leaves out the ones shown there at the current window size and shows its first twelve of the rest. */
  var POSTS_SECTION_LENGTH = 12;

  function postsShownBesideTheLead() {
    var shown = {};
    var column = document.querySelector(".mom-home-posts");
    var list = column && column.querySelector(".mom-home-posts-list");
    if (!list || getComputedStyle(column).display === "none") return shown;
    var listBox = list.getBoundingClientRect();
    list.querySelectorAll(".rh-brief").forEach(function (post) {
      var postBox = post.getBoundingClientRect();
      var wholeAndInside = postBox.width > 0 && postBox.left >= listBox.left - 1 && postBox.right <= listBox.right + 1 && postBox.bottom <= listBox.bottom + 1;
      if (wholeAndInside) shown[post.getAttribute("href")] = true;
    });
    return shown;
  }

  function leaveOutOfThePostsSectionWhatIsShownAbove() {
    var section = document.querySelector(".rh-posts .rh-brief-list");
    if (!section) return;
    var shownAbove = postsShownBesideTheLead();
    var keptCount = 0;
    section.querySelectorAll(":scope > .rh-brief").forEach(function (post) {
      var isShownAbove = shownAbove[post.getAttribute("href")] === true;
      post.toggleAttribute("data-shown-above", isShownAbove);
      if (!isShownAbove) keptCount++;
      post.toggleAttribute("data-beyond-twelve", !isShownAbove && keptCount > POSTS_SECTION_LENGTH);
    });
    section.setAttribute("data-leaves-out-posts-above", "");
  }

  var postsFrameRequested = false;
  function leaveOutPostsOnNextFrame() {
    if (postsFrameRequested) return;
    postsFrameRequested = true;
    window.requestAnimationFrame(function () {
      postsFrameRequested = false;
      leaveOutOfThePostsSectionWhatIsShownAbove();
    });
  }

  function setUpPostsBesideTheLead() {
    var list = document.querySelector(".mom-home-posts-list");
    if (list && window.ResizeObserver) new ResizeObserver(leaveOutPostsOnNextFrame).observe(list);
    window.addEventListener("resize", leaveOutPostsOnNextFrame);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(leaveOutPostsOnNextFrame);
    leaveOutOfThePostsSectionWhatIsShownAbove();
  }

  function onScrollOrResize() {
    moveBands();
    drawHalftonesOnNextFrame();
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

  function relativeTimeText(then, now) {
    var minutes = Math.floor((now - then) / 60000);
    if (minutes < 1) return "just now";
    if (minutes < 60) return minutes + "m ago";
    if (minutes < 60 * 24) return Math.floor(minutes / 60) + "h ago";
    if (minutes < 60 * 24 * 30) return Math.floor(minutes / (60 * 24)) + "d ago";
    return null;
  }

  function showRelativeTimes() {
    var now = Date.now();
    document.querySelectorAll("time.mom-when[datetime]").forEach(function (element) {
      var then = Date.parse(element.getAttribute("datetime"));
      if (isNaN(then) || then > now + 60000) return;
      var text = relativeTimeText(then, now);
      if (text) element.textContent = text;
    });
  }

  function setUpForumBoard(board, rowsPerPage) {
    var later = Array.prototype.slice.call(board.querySelectorAll(".mom-forum-row[data-later]"));
    if (!later.length) return;
    var holder = document.createElement("p");
    holder.className = "mom-forum-more";
    var button = document.createElement("button");
    button.type = "button";
    button.className = "mom-button mom-button-quiet mom-forum-load-more";
    var status = document.createElement("span");
    status.className = "mom-forum-words";
    status.setAttribute("role", "status");
    holder.appendChild(button);
    holder.appendChild(status);
    board.appendChild(holder);
    var total = later.length + board.querySelectorAll(".mom-forum-row:not([data-later])").length;
    function label() {
      button.textContent = "Load more conversations (" + later.length + " more)";
    }
    label();
    button.addEventListener("click", function () {
      var revealed = later.splice(0, rowsPerPage);
      revealed.forEach(function (row) { row.removeAttribute("data-later"); });
      status.textContent = "Showing " + (total - later.length) + " of " + total + " conversations.";
      var link = revealed[0] && revealed[0].querySelector("a");
      if (link) link.focus();
      if (later.length) label(); else holder.removeChild(button);
    });
  }

  function setUpForum() {
    document.querySelectorAll(".mom-forum").forEach(function (forum) {
      var rowsPerPage = Number(forum.getAttribute("data-rows-per-page")) || 10;
      forum.querySelectorAll(".mom-forum-board").forEach(function (board) { setUpForumBoard(board, rowsPerPage); });
      forum.setAttribute("data-paged", "");
    });
  }

  document.querySelectorAll(".mom-nav").forEach(setUpMenu);

  window.addEventListener("scroll", onScrollOrResize, { passive: true });
  window.addEventListener("resize", onScrollOrResize);
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("img[data-art-seed]").forEach(function (image) {
      if (image.complete && image.naturalWidth === 0) replaceBrokenImageWithArt(image);
    });
    showRelativeTimes();
    setUpForum();
    setUpHalftones();
    setUpPostsBesideTheLead();
    onScrollOrResize();
  });
})();

/* promotion-events:start
   House ads report through Papyrus's shared analytics helper (window.papyrusAnalytics.track), which keeps only the allowed parameters and sends
   nothing without gtag or when the reader has opted out. Each ad's <aside> carries data-promotion-id (the ad), data-promotion-name (the
   advertiser), data-ad-unit (the creative) and data-ad-placement (where it sits). An ad is viewed once per page, when half of it is on screen;
   every open of its link (click or middle click) is a select_promotion. Analytics never changes what the reader sees. */
(function () {
  "use strict";
  function promotion(slot) {
    return {
      promotion_id: slot.getAttribute("data-promotion-id"),
      promotion_name: slot.getAttribute("data-promotion-name"),
      creative_name: slot.getAttribute("data-ad-unit"),
      location_id: slot.getAttribute("data-ad-placement")
    };
  }
  function report(name, slot) {
    var analytics = window.papyrusAnalytics;
    if (!analytics || typeof analytics.track !== "function") return;
    try { analytics.track(name, promotion(slot)); } catch (error) {}
  }
  function onOpen(event) {
    var link = event.target && event.target.closest ? event.target.closest("a[href]") : null;
    var slot = link && link.closest("[data-promotion-id]");
    if (slot) report("select_promotion", slot);
  }
  document.addEventListener("click", onOpen);
  document.addEventListener("auxclick", onOpen);
  function watchViews() {
    var slots = document.querySelectorAll("[data-promotion-id]");
    if (!slots.length || typeof window.IntersectionObserver !== "function") return;
    var observer = new window.IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        report("view_promotion", entry.target);
      });
    }, { threshold: 0.5 });
    slots.forEach(function (slot) { observer.observe(slot); });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", watchViews);
  else watchViews();
})();
/* promotion-events:end */
