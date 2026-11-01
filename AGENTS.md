# Agent guide: Machines on Machines

Read this before changing anything. Then read [`docs/handoff.md`](docs/handoff.md) for the decisions behind the design and the build plan.

## What this repository is

The publication repository for Machines on Machines, a Papyrus site. Papyrus is the application (the published `@anthusai/papyrus` package and the `papyrus` CLI); this repository is the publication: its design, its configuration, its theme and its hooks. Model the site layout on `AnthusAI/Shipped-web`, the reference Papyrus site, and follow the Papyrus repository's own `AGENTS.md` for engine rules.

## The design system and the design canvas exist; use them

Two design sources live in this repository. Build from them; do not invent new visual language.

### `design/system/`: the design system

The source of truth for how the site looks and writes.

- `README.md`: the brand book. Voice, the three color roles, type, shape and layout, page types (home, section, article, wiki term), the home page recipe, motion, and the wordmark. Read it first.
- `tokens.json`: every color (light "Day" and dark "Night"), type style, spacing, radius, angle and fixed size. `tokens.css` is generated from it by `python3 tools/build_tokens_css.py`; never edit `tokens.css` by hand. Run with `--check` in CI.
- `components/bundle.js`, `bundle.css`, `index.d.ts`: the reference components under the `MoM` namespace (Wordmark, Sticker, Spine, LoopBand, StoryCard, ReferenceCard, ThreadCard, ProposalRow, ProvenanceChip, Button, NavPill, WireCard, WikiCard, PullQuote, PlaceholderArt). They are React and define the exact markup and `mom-` class names.
- `components/<Name>/README.md`: when and how to use each component, and which Papyrus data feeds it. `preview.html` shows it rendered.
- `design-system.json`: the index the published design system artifact reads.

Papyrus renders the public site in Python, not React. Port each component to the site's `web/hooks.py` (or page includes) by emitting the same markup and `mom-` classes, and ship `bundle.css` plus `tokens.css` as the site's stylesheets. Where a component README states an algorithm, such as `PlaceholderArt`'s seeded choice of art, the Python version must give the same result as the JavaScript.

### `design/canvas/`: the design artboards

The mockups behind the system, as Claude Design canvas files (`*.dc.html`), indexed by `canvas.json`. Pages in `canvas.json`:

- **Public newsroom** (launch page): the home page. `R10-Magazine.dc.html` ("B1, Magazine first") is the chosen home page. `R10-Clusters`, `R10-Column`, `R10-Explained` and the `R9-*` boards are the alternatives it was chosen over.
- **Final**: `F-Home`, `F-Section`, `F-Leaf` (article with the right-hand spine) and `F-Wiki` (wiki term page) in the final palette.
- **Color**: palette rounds; N2 (pink-led, indigo-navy night) won, shown in `PL-Led-Indigo`.
- **Winners** and **Brainstorm**: earlier rounds, kept for history. Their wordmark and palette are out of date; do not build from them.

Every board shows Day and Night side by side. When a mockup and the design system disagree, the design system wins.

To change the design, edit these files and republish the artifacts (links in `README.md`), or ask Ryan; do not drift from them silently in the site code.

## House rules

- Attribution wording follows Papyrus: "Drafted by AI", "Approved by <name>"; author labels "AI" and "Editor". Never write the word "desk".
- Teal (`machine`) marks what machines made or did, gold (`human`) what people chose, pink (`brand`) is the publication. Color is never the only signal; every chip and badge carries words.
- No thin, high-contrast lines: separate things with fills and space, never hairline borders or rules.
- Every card has an image and a one-sentence blurb. Cards without an image draw `PlaceholderArt`, never a stock photo or a gray box.
- No more than three cards across at a 1280px page width.
- Mission and doctrine are backend data edited in the newsroom, not files the build reads.
- Never run `ampx pipeline-deploy` locally. Deploys go through CI.
- Behavior changes need tests and a Gherkin scenario in `features/`.
- Code: long, descriptive names instead of comments; comments only for high-level concepts.
