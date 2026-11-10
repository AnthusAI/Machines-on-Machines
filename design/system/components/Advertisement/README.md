Advertisements, in standard units. Built in Python in `web/mom_components.py` (`advertisement`), styled by `bundle.css`; there is no React version yet.

- **An ad is the advertiser's asset.** It supplies pictures (with its own words, type, colors and art inside) and a link. The site draws only the slot: the label, the sponsored link, alt text, size, placement and containment. The site never styles the inside of a creative. How to supply one: `docs/advertising.md`.
- **Units**: `band` (250 tall, drawn at the slot's width: 1263, 728, 618 and 358 wide; in an article column only 618 and 358), `half-page` (300×600, the wiki rail at 1100px and wider only), `card`, `story`, `pullquote` and `aside` (each a wide and a narrow picture). There is no text-only unit.
- **Provide**: `id`, `advertiser`, `href` (https or a site path), and `images` per unit: `{src, alt, width, height}` plus an optional `src_dark` Night picture. Alt text says what the creative says.
- **Fills its slot.** A block on its own in the text column is exactly as wide as the column, with the label's left edge, the picture's and the column's on one line and the label directly on top (8px). Only the floated aside is narrower.
- **Always** says "Advertisement" in words, with the advertiser, above the picture. Every link is `rel="sponsored noopener"`.
- **Never**: sticky, floating, animated, auto-refreshing, expanding. Never on the first screen, in the nav, the spine, a loop band or a margin note. Two per page at most.
- Where each unit goes and how it steps down: `docs/advertising.md`.
