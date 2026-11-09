Advertisements, in five standard units. Built in Python in `web/mom_components.py` (`advertisement`), styled by `bundle.css`; there is no React version yet.

- **Units**: `band` (970×250 wide, 728×90 medium, 320×100 narrow; in an article column only 320×100), `rectangle` (300×250), `half-page` (300×600, the wiki rail at 1100px and wider only), `card` (native: a story card), `story` (native panel inside the article, up to the 680px measure).
- **Provide**: `id`, `advertiser`, `headline` (60 characters at most), `body` (one sentence or two), `cta` (words, never an arrow), `href` (https or a site path), `units`. Optional: `short_headline` and `note` (the narrow band), `points` (the half page's steps, each `by` machine or human), `unit_copy` (different words for one unit), `images` (the ad's own pictures per unit, each with alt text and pixel size), `card_image`.
- **Always** says "Advertisement" in words, with the advertiser, above the unit (on the card, in its kicker). Every link is `rel="sponsored noopener"`.
- **Look**: inverted `ink` with `paper` text, so an ad never reads as the publication's navy. Machine and human tints appear only on the half page's steps, each with the words "Machines" or "People".
- **Never**: sticky, floating, animated, auto-refreshing, expanding. Never on the first screen, in the nav, the spine, a loop band or a margin note. Two per page at most.
- Where each unit goes and how it steps down: `docs/advertising.md`.
