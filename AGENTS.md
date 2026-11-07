# Agent guide: Machines on Machines

Read this before changing anything. Then read [`docs/handoff.md`](docs/handoff.md) for the decisions behind the design and the build plan.

## What this repository is

The publication repository for Machines on Machines, a Papyrus site. Papyrus is the application (the published `@anthusai/papyrus` package and the `papyrus` CLI); this repository is the publication: its design, its configuration, its theme and its hooks. Model the site layout on `AnthusAI/Shipped-web`, the reference Papyrus site, and follow the Papyrus repository's own `AGENTS.md` for engine rules.

## The design system and the design canvas exist; use them

Two design sources live in this repository. Build from them; do not invent new visual language.

### `design/system/`: the design system

The source of truth for how the site looks and writes.

- `README.md`: the brand book. Voice, the three color roles, type, shape and layout, page types (home, section, article, wiki term), the home page recipe, motion, and the wordmark. Read it first.
- `tokens.json`: every color (light "Day" and dark "Night"), type style, spacing, radius, angle and fixed size. `tokens.css` is generated from it by `python3 tools/build_tokens_css.py`; never edit `tokens.css` by hand (and `web/assets/mom-*.css` are generated from it, see below). Run with `--check` in CI.
- `components/bundle.js`, `bundle.css`, `index.d.ts`: the reference components under the `MoM` namespace (Wordmark, Sticker, Spine, LoopBand, StoryCard, ReferenceCard, ThreadCard, ProposalRow, ProvenanceChip, Button, NavPill, WireCard, WikiCard, PullQuote, PlaceholderArt). They are React and define the exact markup and `mom-` class names.
- `components/<Name>/README.md`: when and how to use each component, and which Papyrus data feeds it. `preview.html` shows it rendered.
- `design-system.json`: the index the published design system artifact reads.

- `../figures/`: how to draw diagrams, charts and illustrations. Read `design/figures/README.md` before drawing any figure.

Papyrus renders the public site in Python, not React. Port each component to the site's `web/hooks.py` (or page includes) by emitting the same markup and `mom-` classes, and ship `bundle.css` plus `tokens.css` as the site's stylesheets. Where a component README states an algorithm, such as `PlaceholderArt`'s seeded choice of art, the Python version must give the same result as the JavaScript.

### Published stylesheets are generated, and everything renders at 75% from 600px up

Owner decision (Ryan, 2026-11): on viewports 600px wide and up the whole site renders at 75% of its designed size; phones (narrower than 600px) keep the designed sizes. Each published stylesheet is one generated file holding both versions: `@media (max-width: 599px) { ...the source rules... }` and `@media (min-width: 600px) { ...the same rules with every px scaled by 0.75... }`. The scaled block also sets `html { font-size: 75% }`, which scales every `rem` on the page, including the core `papyrus-home-page.css` (Papyrus's, in rem, not ours to edit) and Papyrus's inline styles.

- Edit the sources, never the generated files: `design/system/tokens.json` (then `python3 tools/build_tokens_css.py`), `design/system/components/bundle.css`, and `web/css-src/site-theme.src.css` (the hand-written site stylesheet; Papyrus publishes only `web/css/` and `web/assets/`, so the source folder is not published).
- Then run `python3 tools/sync_design_assets.py`. It writes `web/assets/mom-tokens.css`, `web/assets/mom-components.css` and `web/css/site-theme.css`. CI runs it with `--check` and fails when a generated file is stale. Never edit those three files by hand.
- Text has a floor in rendered pixels: 18px reading text, 14px interface and card text, 13px micro-labels, set in `tools/scale_css.py` and enforced there and by `features/text-size.feature`; see "Minimum text size" in `design/system/README.md`. Never write a sized text rule that relies on being small.
- Images have one shape (16:9, `--ratio-media`) and heights snapped to `--rhythm` (4px, 3px scaled); see "Images and the vertical rhythm" in `design/system/README.md` before adding an image slot. `features/image-ratio.feature` has browser scenarios; run them with `PLAYWRIGHT_MODULE=<path to playwright> behave features/image-ratio.feature` (they skip without Playwright).
- Write sizes in the sources as designed (phone) sizes in px. Breakpoints are written as designed too; the tool scales them for the wide version. Do not write your own `@media (min-width: 600px)` rule and do not scale sizes by hand.
- To change the scale (Ryan may try 80% or 85%), change `SCALE` (and `PHONE_MAX`) in `tools/scale_css.py` and re-run the sync tool. That is the only place the factor lives. The scaler multiplies `px` numbers (and `rem` numbers in media queries); it leaves unitless numbers, hex colors, comments, strings and `url()` contents alone.
- Not scaled and not ours: sizes in inline `style` attributes the Python hooks emit (the loop band's `translateX(...px)` start offset in `web/mom_components.py`, `--mom-spine-characters`, the component gallery's `size="48px"`) and Papyrus's inline `<style>` blocks' px (the 2px border of the cookie banner). `web/assets/mom.js` moves bands by scroll distance in CSS pixels, which already follows the scaled layout.

### `design/canvas/`: the design artboards

The mockups behind the system, as Claude Design canvas files (`*.dc.html`), indexed by `canvas.json`. Pages in `canvas.json`:

- **Public newsroom** (launch page): the home page. `R10-Magazine.dc.html` ("B1, Magazine first") is the chosen home page. `R10-Clusters`, `R10-Column`, `R10-Explained` and the `R9-*` boards are the alternatives it was chosen over.
- **Final**: `F-Home`, `F-Section`, `F-Leaf` (article with the right-hand spine) and `F-Wiki` (wiki term page) in the final palette.
- **Neutral color**: the current palette. D, Ink blue (`NP-D-Ink-Blue`), won after launch; the B1 layout is unchanged.
- **Color**: the first palette rounds; N2 (pink-led, indigo-navy night) was used until launch and is now history.
- **Winners** and **Brainstorm**: earlier rounds, kept for history. Their wordmark and palette are out of date; do not build from them.

Every board shows Day and Night side by side. When a mockup and the design system disagree, the design system wins.

To change the design, edit these files and republish the artifacts (links in `README.md`), or ask Ryan; do not drift from them silently in the site code.

## Development policy (Ryan, 2026-11-04)

- Develop and verify on a local dev server: `npm run dev` (runs `papyrus-app sync`, then `next dev` on port 3001; it needs a backend's `amplify_outputs.json`, gitignored), or `python3 tools/preview_local.py /tmp/out` for the static publication with no backend. For the seeded console with no AWS, run `npm run dev:preview` in a Papyrus checkout. Do not deploy to see whether something works.
- **Merge** means merging a pull request into `develop`; that is where things are reviewed. `develop` builds nothing in Amplify.
- **Release** means merging `develop` into `main`, which deploys. Aim for once or twice a day, batching what is ready. An extra release needs Ryan's say-so.
- Papyrus version bumps go to this site's `develop` and ship in this site's release. A Papyrus release can add a GSI and a deploy can add only one per table, so a site cannot skip a release that adds one.
- Say "merged to develop" or "released" precisely.

## House rules

- Attribution wording follows Papyrus: "Drafted by AI", "Approved by <name>"; author labels "AI" and "Editor". Never write the word "desk".
- The palette is Ink blue and stays neutral, like a newspaper: navy (`brand`) is the publication and the only strong color; a cool blue-gray tint (`machine`) marks what machines made or did, a warm gray tint (`human`) what people chose. Color is never the only signal; every chip and badge carries words.
- No thin, high-contrast lines: separate things with fills and space, never hairline borders or rules.
- Every card has an image and a one-sentence blurb. Cards without an image draw `PlaceholderArt`, never a stock photo or a gray box.
- No more than three cards across at a 1280px page width.
- Mission and doctrine are backend data edited in the newsroom, not files the build reads.
- Never run `ampx pipeline-deploy` locally. Deploys go through CI, on a release.
- Behavior changes need tests and a Gherkin scenario in `features/`.
- Code: long, descriptive names instead of comments; comments only for high-level concepts.

## Project planning with Kanbus

Planning lives in the Kanbus board under `project/`, with issue prefix `MOM`. Read [`CONTRIBUTING_AGENT.md`](CONTRIBUTING_AGENT.md) for board commands. Use the Kanbus CLI to create, inspect and update issues and events; do not read or edit their JSON files directly.

Share planning-only changes on `develop`. Keep the branding plan as an epic with ordered tasks, rather than a milestone or behavior stories. Record outstanding design and copy decisions before implementing them. The branding epic is a handoff for Claude to implement and for subsequent review; filing its tasks does not complete or start them.
