# Advertising

Ads are data in `web/ads.json`, drawn by `advertisement()` in `web/mom_components.py`, placed by `web/hooks.py`, and styled by the "Advertisement" section of `design/system/components/bundle.css`. The design canvas is "Advertising on Machines on Machines" (placement, units, responsive behavior, and the Papyrus house campaign in Day and Night).

## Making a real ad

Add an object to `ads` in `web/ads.json`:

```json
{
  "id": "acme-spring",
  "advertiser": "Acme",
  "units": ["band", "rectangle", "card", "story"],
  "href": "https://example.com/landing?utm_source=machines-on-machines",
  "headline": "Eval tooling that grades the graders.",
  "body": "One sentence about what it does.",
  "cta": "See how it works"
}
```

The build checks every ad (`validate_advertisement`) and fails with the reason, so a bad ad never reaches a page. Rules the check enforces: every required field, a headline of 60 characters or fewer, an `https` address or a site path, known unit names, and alt text plus pixel size on every picture.

- **Words only** is enough. The band, rectangle and half page draw the house creative (inverted ink) from the words; the card is a story card; the story panel is native.
- **Pictures:** under `images`, give a unit its own creative: `band` (`wide` 970×250, `medium` 728×250 and `narrow` 300×250, which is required, and the only one an article shows), `rectangle` (300×250) or `half-page` (300×600). Each is `{"src", "alt", "width", "height"}`; put the files under `web/assets/ads/`. PNG, JPG or WebP at twice the pixels, under 150 KB, no animation, no scripts. A unit with no picture falls back to the house creative.
- **Different words for one unit:** `unit_copy`, as the Papyrus ad does for its card, story panel and in-content units.
- **The advertiser's own look:** `brand` gives an ad its own name, mark and colors in place of the site's shapes: `{"name", "mark", "serif", "ground": {"day", "night"}, "ink": {"day", "night"}}`. Colors are `#rrggbb`; the build fails if a ground and ink pair has less than 4.5 contrast. `mark` names a drawing in `AD_BRAND_MARKS` (add a new advertiser's mark there); `serif` sets the headline in Playfair Display. An ad with no `brand` uses the site's own disc and slab.
- **Turn all ads off:** `"enabled": false`.
- **Choosing:** a page always shows the same ad (chosen from its path); when two ads can fill two slots on one page, they differ.

## Where ads go

| Page | Placements |
| --- | --- |
| Home | `home-band`: a Band at the end of the page, after the findings (never beside the animated brand band) |
| Section and tag pages | `listing-card`: a Card as the fifth card; `listing-end`: a Band after the grid |
| Article | One ad, chosen by the page's path from every unit the ads offer: a Band after the last paragraph (`article-end`, which offers only its 300×250 picture because the article column is narrower than a 728px one), or an in-content unit inside the words: `article-story` (after paragraph 4), `article-pullquote` and `article-inline` (after 3), `article-aside` (after 2, so the words flow around it). A story with fewer than 7 paragraphs always gets the Band |
| Wiki term | `wiki-rail`: a Half page in a 300px rail at 1100px and wider (below the first screen), a Rectangle in the flow below that |
| Findings, Conversations, wiki index, thread pages | none |

No page has more than two placements, and tests enforce it. Ads never appear on the first screen, in the nav, the spine, a loop band or a margin note.

## How units adapt

The site draws every px at 75% on wider screens, but a standard ad size is a real pixel size, so the units' own sizes and the breakpoints are written in `pt` (3pt is 4 real pixels), which the scale never touches. Wide is 1042 real pixels and up, medium 800 to 1041, narrow under 800. The band is 250px tall at every width (970, 728 and 300 wide), so it keeps its weight as the window narrows: the headline stays large and the button spans the unit on a phone. The Half page needs a rail, so it exists only at 1100 real pixels and wider, and a Rectangle takes its place in the flow below that. The Card follows the card grid: three, two, then one across. The Story panel is fluid to the 680px measure and drops its art on a phone. Nothing is scaled, and nothing is sticky or animated.

## In-content units

These sit inside an article's words, set in the article's own type, not in a box between sections. Each says "Advertisement" and the advertiser's name, and each is a link marked sponsored.

| Unit | What it is | Copy it reads |
| --- | --- | --- |
| `inline` | One sentence set as a paragraph of the story, with a tag and an underlined link | `body` |
| `pullquote` | The story's own large quote style carrying one line of the advertiser's | `headline` |
| `aside` | A note set into the text, floated right so the words flow around it; full width on a phone | `headline`, `body` |
| `story` | A panel in the reading column (house creative) | `headline`, `body` |

Offer a unit by listing it in the ad's `units`; give it its own words under `unit_copy`.

## Known gaps

- The Card is inserted as the fifth card, so a full page of six cards becomes seven. Page size is not changed.
- The home page has no card grid of six, so it carries no Card.
- Ads have no start and end dates yet: add and remove them in the file. A date test would make a page change just because time passed.
- Papyrus's own ad links to `https://p.apyr.us/` with `utm_` parameters (confirmed by Ryan).
