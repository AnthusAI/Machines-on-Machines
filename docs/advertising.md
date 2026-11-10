# Advertising

Ads are data in `web/ads.json`, drawn by `advertisement()` in `web/mom_components.py`, placed by `web/hooks.py`, and styled by the "Advertisement" section of `design/system/components/bundle.css`. The design canvas is "Advertising on Machines on Machines" (placement, units, responsive behavior, and the first Papyrus house campaign in Day and Night). Every unit of every ad, and the aside set into a sample of article words, is on the component gallery at `/design/`.

## The house campaigns

Two house advertisers take turns: **Papyrus**, the publishing system behind this site, and **Anthus AI Solutions**, the company that makes it. Each wears its own brand, never the site's navy, and inverts against the page: dark by Day, light (Papyrus) or pink (Anthus) by Night.

| | Papyrus | Anthus AI Solutions |
| --- | --- | --- |
| Mark | The papyrus plant (`papyrus-plant`), from the plant on p.apyr.us | The pixel-A lockup "ANTHUS AI SOLUTIONS" from anth.us (`anthus-lockup`) |
| Face | `serif`: Playfair Display headlines, Georgia text, Arial capitals on the button | `pixel`: Jersey 25 headlines, Jersey 10 capitals on the button |
| Colors | ink `#1b1d20`, paper `#f4f1ea`, spot red `#e2725f` / `#a3271f` (p.apyr.us) | night `#150f20`, ice `#f3eef8`, hot pink `#ff57b4` (anth.us) |
| Art | `papyrus-sun`: the plant standing in a red disc | `anthus-pixels`: the pixel A on its tile, with a trail of loose pixels |
| Line | "This publication *literally* writes itself." / "Almost." | Three variants: "This site is brought to you by Anthus AI Solutions." (`anthus-brought-to-you-by`), "Got a job AI could do? We’ll build it." (`anthus-busywork`), "Like how this site works? We build things like it." (`anthus-like-this-site`) |

The truth rules for their copy: agents draft and people approve; this site is an example, not a customer; no claims about speed, uptime, customers or present-tense production use; nothing about pricing or hosting that does not exist. Anthus copy is in plain words a stranger gets in two seconds, and never sells owning code or an AWS account (Ryan: most people do not want to own code). "Literally writes itself" is always followed by "Almost." where the unit has room for a sentence (the phone band keeps its sentence for that reason).

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
- **The advertiser's own look:** `brand` gives an ad its own name, mark, type and colors in place of the site's shapes: `{"name", "mark" or "wordmark", "face", "art", "ground": {"day", "night"}, "ink": {"day", "night"}, "accent": {"day", "night"}}`. Colors are `#rrggbb`; the build fails if ink or accent has less than 4.5 contrast on the ground (the accent is the button, with the ground color as its text, the emphasized headline words and the art; without one, the ink does those jobs). `mark` names a small drawing in `AD_BRAND_MARKS`, shown before the name; `wordmark` names a whole lockup in `AD_BRAND_WORDMARKS`, shown instead of mark and name and labelled with the name; `art` names a composition in `AD_BRAND_ART`, drawn beside the words of the band and story panel, in a corner of the rectangle, between the headline and the steps of the half page, and as the card's picture; `face` is `serif` or `pixel`. Add a new advertiser's drawings to those tables. An ad with no `brand` uses the site's own disc and slab.
- **Emphasis:** `*words*` in a headline are set in italics and the brand's accent (italics, so the emphasis never depends on color). The marks do not count toward the 60 characters.
- **Turn all ads off:** `"enabled": false`.
- **Variants:** an advertiser can run several ads (same `advertiser`, different `id`). The advertisers take turns, and the page then picks one of the chosen advertiser's variants, so an advertiser with three variants gets no more turns than one with one.
- **Choosing:** a page always shows the same ad (chosen from its path); when two advertisers can fill two slots on one page, the slots show different advertisers. An article first takes its advertiser and variant from its path, then one of the units that ad offers. There is no tracking and no campaign scheduling yet.

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

These sit inside an article's words. The inline sentence is set in the article's own type; the aside and a branded pull-quote wear the advertiser's colors, so an ad never passes for the publication's own furniture. Each says "Advertisement" and the advertiser's name, and each is a link marked sponsored.

| Unit | What it is | Copy it reads |
| --- | --- | --- |
| `inline` | One sentence set as a paragraph of the story, with a tag and an underlined link | `body` |
| `pullquote` | The story's large quote shape carrying one line of the advertiser's, on the advertiser's ground, so it never passes for an editor's quote | `headline` |
| `aside` | A small poster in the advertiser's colors set into the text, floated right so the words flow around it with a gutter beside and below it (`--mom-ad-aside-gutter`); full width on a phone | `headline`, `body` |
| `story` | A panel in the reading column (house creative) | `headline`, `body` |

Offer a unit by listing it in the ad's `units`; give it its own words under `unit_copy`.

## Known gaps

- The Card is inserted as the fifth card, so a full page of six cards becomes seven. Page size is not changed.
- The home page has no card grid of six, so it carries no Card.
- Ads have no start and end dates yet: add and remove them in the file. A date test would make a page change just because time passed.
- Papyrus's own ad links to `https://p.apyr.us/` with `utm_` parameters (confirmed by Ryan). Anthus's links to `https://anth.us/ai-solutions/` with `utm_` parameters (not yet confirmed).
