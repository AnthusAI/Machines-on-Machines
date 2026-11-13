/* @ds-bundle: {"format":4,"namespace":"MoM","components":[{"name":"Wordmark"},{"name":"Sticker"},{"name":"Spine"},{"name":"LoopBand"},{"name":"StoryCard"},{"name":"ReferenceCard"},{"name":"ThreadCard"},{"name":"ProposalRow"},{"name":"ProvenanceChip"},{"name":"Button"},{"name":"NavPill"},{"name":"WireCard"},{"name":"WikiCard"},{"name":"PullQuote"},{"name":"PlaceholderArt"}]} */
(function () {
  var React = window.React;
  var createElement = React.createElement;

  function joinClassNames() {
    return Array.prototype.filter.call(arguments, Boolean).join(" ");
  }

  var knownRoles = { brand: true, machine: true, human: true };
  function roleOrDefault(role, fallbackRole) {
    return knownRoles[role] ? role : fallbackRole;
  }

  function clampBetweenZeroAndOne(value) {
    var number = Number(value);
    if (!isFinite(number)) return 0;
    return Math.max(0, Math.min(1, number));
  }

  function Wordmark(props) {
    var layout = props.layout || "inline";
    var subject = props.subject || "Machines";
    var elementName = props.as || "span";
    return createElement(
      elementName,
      {
        className: joinClassNames("mom-wordmark", "mom-wordmark-" + layout, props.className),
        style: props.size ? { fontSize: props.size } : undefined
      },
      createElement("span", null, "Machines"),
      createElement("span", { className: "mom-wordmark-on" }, "on"),
      createElement("span", null, subject)
    );
  }

  function Sticker(props) {
    var taglineVariant = props.taglineVariant || "display";
    return createElement(
      "div",
      { className: joinClassNames("mom-sticker", props.flat ? "mom-sticker-flat" : null, props.className) },
      createElement("div", { className: "mom-sticker-backing", "aria-hidden": "true" }),
      createElement(
        "div",
        { className: "mom-sticker-face" },
        createElement(Wordmark, { layout: "stacked", subject: props.subject, as: props.headingLevel ? "h" + props.headingLevel : "span" }),
        props.tagline ? createElement("p", { className: "mom-sticker-tagline mom-sticker-tagline-" + taglineVariant }, props.tagline) : null,
        props.children ? createElement("div", { className: "mom-sticker-actions" }, props.children) : null
      )
    );
  }

  function Spine(props) {
    return createElement(
      "nav",
      { className: joinClassNames("mom-spine", props.className), "aria-label": "Site and section" },
      createElement(
        "div",
        { className: "mom-spine-content" },
        createElement("a", { className: "mom-spine-home", href: props.homeHref || "#", "aria-label": "Machines on Machines, home" }, createElement(Wordmark, { layout: "stacked" })),
        createElement("a", { className: "mom-spine-section", href: props.sectionHref || "#" }, createElement(Wordmark, { layout: "vertical", subject: props.subject || "Machines" }))
      )
    );
  }

  function LoopBand(props) {
    var role = roleOrDefault(props.role, "brand");
    var wordPattern = props.words && props.words.length ? props.words : ["Machines", "on", "Machines", "on"];
    var repeatCount = props.repeat || 4;
    var repeatedWords = [];
    for (var repetition = 0; repetition < repeatCount; repetition++) {
      repeatedWords = repeatedWords.concat(wordPattern);
    }
    return createElement(
      "div",
      { className: joinClassNames("mom-band", "mom-band-" + role, props.className) },
      createElement(
        "div",
        { className: "mom-band-row", "aria-hidden": "true", style: { transform: "translateX(" + (props.offset || 0) + "px)" } },
        repeatedWords.map(function (word, wordIndex) {
          var wordKind = word === "on" ? "on" : word.charAt(0) === "#" ? "tag" : "word";
          return createElement("span", { key: wordIndex, className: "mom-band-" + wordKind }, word);
        })
      ),
      props.label ? createElement("span", { className: "mom-band-label" }, props.label) : null
    );
  }

  function ProvenanceChip(props) {
    var role = roleOrDefault(props.role, "machine");
    return createElement("span", { className: joinClassNames("mom-chip", "mom-chip-" + role, props.className) }, props.children);
  }

  function Button(props) {
    var variant = props.variant === "brand" || props.variant === "quiet" ? props.variant : "human";
    var className = joinClassNames("mom-button", "mom-button-" + variant, props.className);
    if (props.href) {
      return createElement("a", { className: className, href: props.href }, props.children);
    }
    return createElement("button", { className: className, type: props.type || "button", onClick: props.onClick }, props.children);
  }

  function NavPill(props) {
    return createElement(
      "a",
      {
        className: joinClassNames("mom-nav-pill", props.active ? "mom-nav-pill-active" : null, props.className),
        href: props.href || "#",
        "aria-current": props.active ? "page" : undefined
      },
      props.children
    );
  }

  function WireCard(props) {
    var scoreFraction = clampBetweenZeroAndOne(props.score);
    return createElement(
      "a",
      { className: joinClassNames("mom-wire-card", props.className), href: props.href || "#" },
      props.section ? createElement("span", { className: "mom-wire-card-section" }, props.section) : null,
      createElement("span", { className: "mom-wire-card-title" }, props.title),
      createElement(
        "span",
        { className: "mom-wire-card-meta" },
        props.source,
        createElement(
          "span",
          { className: "mom-score-track", role: "img", "aria-label": "Classifier score " + scoreFraction.toFixed(2) },
          createElement("span", { className: "mom-score-bar", style: { width: Math.round(scoreFraction * 100) + "%" } })
        ),
        scoreFraction.toFixed(2)
      )
    );
  }

  function WikiCard(props) {
    return createElement(
      "a",
      { className: joinClassNames("mom-wiki-card", props.className), href: props.href || "#", "data-associations": props.associations || undefined },
      createElement(
        "span",
        { className: "mom-wiki-card-head" },
        createElement("span", { className: "mom-wiki-card-term" }, props.term),
        props.associations
          ? createElement("span", { className: "mom-wiki-card-associations" }, props.associations + (props.associations === 1 ? " association" : " associations"))
          : null
      ),
      props.definition ? createElement("span", { className: "mom-wiki-card-definition" }, props.definition) : null
    );
  }

  function PullQuote(props) {
    return createElement(
      "figure",
      { className: joinClassNames("mom-pull-quote", props.className) },
      createElement("blockquote", { className: "mom-pull-quote-text" }, props.children)
    );
  }

  var placeholderCompositionShapeCounts = { "sun-slab": 2, "rising": 1, "eclipse": 1, "moon": 1, "horizon": 1, "pages": 3 };
  var generalPlaceholderCompositions = ["sun-slab", "rising", "eclipse", "moon", "horizon"];
  var placeholderTones = ["brand", "machine", "human"];
  var researchPaperHosts = ["arxiv.org", "openreview.net", "aclanthology.org", "proceedings.mlr.press", "papers.nips.cc", "proceedings.neurips.cc", "dl.acm.org", "ieeexplore.ieee.org", "semanticscholar.org", "biorxiv.org"];

  function encodeSeedAsUtf8Bytes(seed) {
    if (typeof TextEncoder !== "undefined") return new TextEncoder().encode(seed);
    var escapedSeed = unescape(encodeURIComponent(seed));
    var bytes = [];
    for (var characterIndex = 0; characterIndex < escapedSeed.length; characterIndex++) bytes.push(escapedSeed.charCodeAt(characterIndex));
    return bytes;
  }

  function hashSeedToUnsignedInteger(seed) {
    var bytes = encodeSeedAsUtf8Bytes(String(seed || ""));
    var hashValue = 0x811c9dc5;
    for (var byteIndex = 0; byteIndex < bytes.length; byteIndex++) {
      hashValue ^= bytes[byteIndex];
      hashValue = Math.imul(hashValue, 0x01000193) >>> 0;
    }
    return hashValue >>> 0;
  }

  function isResearchPaperLocation(location) {
    if (!location) return false;
    var normalizedLocation = String(location).toLowerCase();
    if (/\.pdf($|[?#])/.test(normalizedLocation)) return true;
    return researchPaperHosts.some(function (paperHost) { return normalizedLocation.indexOf(paperHost) !== -1; });
  }

  function choosePlaceholderArt(seed, kind) {
    var hashValue = hashSeedToUnsignedInteger(seed);
    var composition = kind === "paper" ? "pages" : generalPlaceholderCompositions[hashValue % generalPlaceholderCompositions.length];
    var tone = placeholderTones[(hashValue >>> 8) % placeholderTones.length];
    return { composition: composition, tone: tone };
  }

  function PlaceholderArt(props) {
    var chosenArt = choosePlaceholderArt(props.seed, props.kind);
    var composition = placeholderCompositionShapeCounts[props.composition] ? props.composition : chosenArt.composition;
    var tone = knownRoles[props.tone] ? props.tone : chosenArt.tone;
    var shapes = [];
    for (var shapeIndex = 1; shapeIndex <= placeholderCompositionShapeCounts[composition]; shapeIndex++) {
      shapes.push(createElement("span", { key: shapeIndex, className: "mom-art-shape mom-art-shape-" + shapeIndex }));
    }
    return createElement(
      "span",
      { className: joinClassNames("mom-card-image", "mom-art", "mom-art-" + composition, "mom-art-tone-" + tone, props.className), "aria-hidden": "true", "data-composition": composition, "data-tone": tone },
      shapes
    );
  }

  function CardImage(props) {
    var imageFailedState = React.useState(false);
    var imageFailed = imageFailedState[0];
    var shapeClass = props.square ? "mom-card-image-square" : undefined;
    var picture = props.src && !imageFailed
      ? createElement("img", { className: joinClassNames("mom-card-image", shapeClass), src: props.src, alt: props.alt || "", loading: "lazy", onError: function () { imageFailedState[1](true); } })
      : createElement(PlaceholderArt, { seed: props.seed, kind: props.kind, tone: props.tone, composition: props.composition, className: shapeClass });
    return createElement("span", { className: joinClassNames("mom-media", props.className) }, picture);
  }

  function renderProvenanceChips(provenance) {
    if (!provenance || !provenance.length) return null;
    return createElement(
      "span",
      { className: "mom-chip-row" },
      provenance.map(function (chip, chipIndex) {
        return createElement(ProvenanceChip, { key: chipIndex, role: chip.role }, chip.label);
      })
    );
  }

  function StoryCard(props) {
    var size = props.size === "small" ? "small" : "large";
    return createElement(
      "a",
      { className: joinClassNames("mom-story-card", "mom-story-card-" + size, props.className), href: props.href || "#" },
      createElement(CardImage, { src: props.image, alt: props.imageAlt, tone: props.imageTone, seed: props.imageSeed || props.href || props.headline }),
      props.kicker ? createElement("span", { className: "mom-kicker" }, props.kicker) : null,
      renderProvenanceChips(props.provenance),
      createElement("span", { className: "mom-story-card-headline" }, props.headline),
      props.meta ? createElement("span", { className: "mom-card-date" }, props.meta) : null,
      props.blurb ? createElement("span", { className: "mom-blurb" }, props.blurb) : null
    );
  }

  var referenceStatusLabels = {
    "accepted-human": { label: null, role: "human" },
    "accepted-cyclotron": { label: "Accepted by Cyclotron", role: "machine" },
    "accepted-agent": { label: "Accepted by AI", role: "machine" },
    "accepted-rule": { label: "Accepted by a rule", role: "machine" },
    "recommended": { label: "Recommended by Cyclotron, not yet accepted", role: "pending" }
  };

  var STAR_POINTS = "12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2";
  function StarRating(props) {
    var count = Math.max(0, Math.min(5, Number(props.stars) || 0));
    return createElement(
      "span",
      { className: "mom-stars", role: "img", "aria-label": count + " of 5 stars" },
      [0, 1, 2, 3, 4].map(function(position) {
        return createElement(
          "svg",
          { key: position, className: "mom-icon", xmlns: "http://www.w3.org/2000/svg", width: 16, height: 16, viewBox: "0 0 24 24", fill: position < count ? "currentColor" : "none", stroke: "currentColor", strokeWidth: 2, strokeLinejoin: "round", "aria-hidden": "true", focusable: "false", "data-icon": "star" },
          createElement("polygon", { points: STAR_POINTS })
        );
      })
    );
  }

  var acceptancePredictions = ["Very unlikely to be accepted", "Unlikely to be accepted", "May be accepted", "Likely to be accepted", "Very likely to be accepted"];
  function ConfidenceMeter(props) {
    var filledSegmentCount = Math.min(Math.floor(clampBetweenZeroAndOne(props.confidence) * 5) + 1, 5);
    var prediction = acceptancePredictions[filledSegmentCount - 1];
    var segments = [];
    for (var segmentIndex = 0; segmentIndex < 5; segmentIndex++) {
      segments.push(createElement("span", { key: segmentIndex, className: segmentIndex < filledSegmentCount ? "mom-meter-segment mom-meter-segment-filled" : "mom-meter-segment" }));
    }
    return createElement(
      "span",
      { className: "mom-meter" },
      createElement("span", { className: "mom-meter-track", role: "img", "aria-label": "Prediction: " + filledSegmentCount + " of 5" }, segments),
      createElement("span", { className: "mom-meter-label" }, prediction)
    );
  }
  function ReferenceCard(props) {
    var statusKey = props.status === "recommended" ? "recommended" : "accepted-" + (props.actor || "human");
    var status = referenceStatusLabels[statusKey] || referenceStatusLabels["accepted-human"];
    return createElement(
      "a",
      { className: joinClassNames("mom-reference-card", props.className), href: props.href || "#" },
      createElement(
        "span",
        { className: "mom-reference-card-media" },
        createElement(CardImage, { src: props.image, alt: "", tone: props.imageTone, seed: props.imageSeed || props.href || props.title, kind: props.kind || (isResearchPaperLocation(props.href) || isResearchPaperLocation(props.host) ? "paper" : undefined) }),
        props.siteName ? createElement("span", { className: "mom-reference-card-site" }, props.siteName) : null
      ),
      status.label ? createElement("span", { className: "mom-reference-status mom-reference-status-" + status.role }, status.label) : null,
      createElement("span", { className: "mom-reference-card-title" }, props.title),
      props.summary ? createElement("span", { className: "mom-reference-card-summary" }, props.summary) : null,
      props.stars && props.status !== "recommended" ? createElement(StarRating, { stars: props.stars }) : null,
      props.confidence != null && props.status === "recommended" ? createElement(ConfidenceMeter, { confidence: props.confidence }) : null,
      createElement("span", { className: "mom-card-date" }, [props.host, props.age].filter(Boolean).join(" · "))
    );
  }

  var threadAuthorRoles = { AI: "machine", Editor: "human" };

  function ThreadCard(props) {
    var authorRole = threadAuthorRoles[props.author] || "reader";
    return createElement(
      "a",
      { className: joinClassNames("mom-thread-card", props.className), href: props.href || "#" },
      props.anchor ? createElement("span", { className: "mom-meta mom-thread-card-anchor" }, props.anchor) : null,
      createElement("span", { className: "mom-thread-card-title" }, props.title),
      createElement(CardImage, { src: props.image, alt: "", tone: props.imageTone, seed: props.imageSeed || props.href || props.title, className: "mom-thread-card-thumb", square: true }),
      props.latest ? createElement(
        "span",
        { className: "mom-thread-card-latest" },
        createElement("span", { className: "mom-author mom-author-" + authorRole }, props.author),
        createElement("span", null, props.latest)
      ) : null,
      createElement("span", { className: "mom-card-date mom-thread-card-meta" }, [props.messages != null ? props.messages + " messages" : null, props.lastAt].filter(Boolean).join(" · "))
    );
  }

  function ProposalRow(props) {
    var netVotes = Number(props.net) || 0;
    return createElement(
      "div",
      { className: joinClassNames("mom-proposal-row", props.className) },
      createElement(
        "span",
        { className: "mom-proposal-row-text" },
        createElement("a", { className: "mom-proposal-row-title", href: props.href || "#" }, props.title),
        createElement(
          "span",
          { className: "mom-chip-row" },
          createElement(ProvenanceChip, { role: "machine" }, "Proposed by AI"),
          props.state ? createElement("span", { className: props.approved ? "mom-chip mom-chip-human" : "mom-chip mom-chip-quiet" }, props.state) : null
        )
      ),
      createElement(
        "span",
        { className: "mom-vote" },
        createElement("button", { type: "button", className: "mom-vote-up", "aria-label": "Vote up", onClick: props.onVoteUp }, "▲"),
        createElement("span", { className: "mom-vote-count" }, (netVotes > 0 ? "+" : "") + netVotes),
        createElement("button", { type: "button", className: "mom-vote-down", "aria-label": "Vote down", onClick: props.onVoteDown }, "▼")
      )
    );
  }

  window.MoM = window.MoM || {};
  Object.assign(window.MoM, {
    Wordmark: Wordmark,
    Sticker: Sticker,
    Spine: Spine,
    LoopBand: LoopBand,
    StoryCard: StoryCard,
    ReferenceCard: ReferenceCard,
    ThreadCard: ThreadCard,
    ProposalRow: ProposalRow,
    ProvenanceChip: ProvenanceChip,
    Button: Button,
    NavPill: NavPill,
    WireCard: WireCard,
    WikiCard: WikiCard,
    PullQuote: PullQuote,
    PlaceholderArt: PlaceholderArt,
    choosePlaceholderArt: choosePlaceholderArt
  });
})();
