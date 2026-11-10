# Advertising

Ads are data in `web/ads.json` that point at the advertiser's own picture files in `web/assets/ads/`; `advertisement()` in `web/mom_components.py` draws only the slot around them, `web/hooks.py` places them, and the "Advertisement" section of `design/system/components/bundle.css` styles only that slot. The design canvas is "Advertising on Machines on Machines" (placement, units, responsive behavior, and the first Papyrus house campaign in Day and Night). Every unit of every ad, and the aside set into a sample of article words, is on the component gallery at `/design/`.

## What an ad is

An ad is an asset entirely controlled by the advertiser. The advertiser supplies pictures, with their own words, type, colors and art drawn inside them, and a link. The site draws only the slot around a picture, and never styles what is inside it:

- the label **Advertisement · <advertiser>**, outside and above the picture, so nobody mistakes an ad for the publication's own words;
- the link, `rel="sponsored noopener"`, wrapped around the picture;
- the picture's alt text, `width` and `height`;
- the unit's size, where it sits on the page, and containment: a picture is never scaled up, only down to fit its column.

No headline, body, button, brand color or type face of an ad comes from the site's code or CSS. There is no template to fill in. A change to the advertiser's look is a change to its pictures.

## The house campaigns

Two house advertisers take turns: **Papyrus**, the publishing system behind this site, and **Anthus AI Solutions**, the company that makes it. Their creatives were drawn once from the design the site used to render for them and are now plain assets in `web/assets/ads/`, in Day and Night versions (each defines night colors). Papyrus is a dark ground with spot red by Day and paper with a deeper red by Night; Anthus is its night purple with hot pink by Day and pink by Night.

| Advertiser | Variants (`id`) and their line |
| --- | --- |
| Papyrus | `papyrus-newsroom`: "This publication *literally* writes itself." / "Almost." |
| Anthus AI Solutions | `anthus-brought-to-you-by`: "This site is brought to you by Anthus AI Solutions." `anthus-busywork`: "Got a job AI could do? We'll build it." `anthus-like-this-site`: "Like how this site works? We build things like it." |

The truth rules for their copy: agents draft and people approve; this site is an example, not a customer; no claims about speed, uptime, customers or present-tense production use; nothing about pricing or hosting that does not exist. Anthus copy is in plain words a stranger gets in two seconds, and never sells owning code or an AWS account (Ryan: most people do not want to own code). "Literally writes itself" is always followed by "Almost." where the unit has room for a sentence.

## How an advertiser supplies an ad

Add an object to `ads` in `web/ads.json` and the picture files under `web/assets/ads/`:

```json
{
  "id": "acme-spring",
  "advertiser": "Acme",
  "href": "https://example.com/landing?utm_source=machines-on-machines",
  "images": {
    "band": {
      "wide":   {"src": "/assets/ads/acme-band-wide.webp",   "src_dark": "/assets/ads/acme-band-wide-night.webp",   "alt": "Acme: Eval tooling that grades the graders. See how it works.", "width": 970, "height": 250},
      "medium": {"src": "/assets/ads/acme-band-medium.webp", "src_dark": "/assets/ads/acme-band-medium-night.webp", "alt": "...", "width": 728, "height": 250},
      "narrow": {"src": "/assets/ads/acme-band-narrow.webp", "src_dark": "/assets/ads/acme-band-narrow-night.webp", "alt": "...", "width": 300, "height": 250}
    },
    "rectangle": {"src": "/assets/ads/acme-rectangle.webp", "alt": "...", "width": 300, "height": 250}
  }
}
```

An ad offers exactly the units it has pictures for; there is no `units` list, headline, body, button text or brand to fill in. The build checks every ad (`validate_advertisement`) and fails with the reason, so a bad ad never reaches a page:

- `id`, `advertiser` and `href` are required, and `href` is an `https` address or a path on this site.
- Every picture has `src`, `alt`, `width` and `height`. `src` is a `.webp`, `.png`, `.jpg` or `.svg` file under `/assets/ads/` that exists in `web/assets/ads/`, at most 150,000 bytes, with no animation and no scripts. The `width` and `height` are the size it is drawn at; ship the file at twice those pixels so it is sharp on dense screens.
- **Alt text is required and must say what the creative says**: the advertiser, the headline, the sentence and the button words as a reader would hear them, at least 20 characters and never the advertiser's name alone. The picture is the only place the words exist, so the alt text is how a screen reader, a text-only reader and a search engine get them.
- Night pictures: `src_dark` is optional, shown when the theme is Night (the site's theme switch or the visitor's dark preference), and it is given for every size of a unit or for none. An advertiser whose brand has no night colors ships one picture.
- Units that stretch or squeeze with the page take sizes (below); `narrow` is always required, the size every width can show.

| Unit | Pictures | Sizes (CSS pixels, given at twice the pixels) |
| --- | --- | --- |
| `band` | `wide`, `medium`, `narrow` | 970×250 from 1042px of window, 728×250 from 800px, 300×250 below. 250 tall at every width, so it keeps its weight as the window narrows. In an article column only `narrow` is offered. |
| `rectangle` | one picture | 300×250 |
| `half-page` | one picture | 300×600 (wiki rail, 1100px and wider only) |
| `card` | `wide`, `narrow` | the card is drawn as a whole, art and words, to sit in the card grid: 241px wide in a three-across grid, 358px on a phone |
| `story` | `wide`, `narrow` | the article's reading column: 618px, and 358px on a phone |
| `pullquote` | `wide`, `narrow` | the same column widths; the creative is the large quote shape |
| `aside` | `wide`, `narrow` | 284px (floated beside the words), and 358px on a phone |

`wide` is used from a 600px window (where the site starts drawing at 75%); below that the `narrow` picture is shown. A picture larger than its column is scaled down to fit, never up.

There is no text-only unit. The earlier `inline` unit (a sentence set in the article's own type) was removed: a bare sentence in the site's typography is not something the advertiser controls and it passes for the article's own words. An advertiser that wants a text ad draws it as a picture, in a unit that has a frame.

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

The site draws every px at 75% on wider screens, but a standard ad size is a real pixel size, so the slot's own sizes and the breakpoints are written in `pt` (3pt is 4 real pixels), which the scale never touches. Wide is 1042 real pixels and up, medium 800 to 1041, narrow under 800. The Half page needs a rail, so it exists only at 1100 real pixels and wider, and a Rectangle takes its place in the flow below that. Nothing is scaled up, and nothing is sticky or animated.

## In-content units

These sit inside an article's words. Each says "Advertisement" and the advertiser's name in the site's label above the picture, and each picture is a link marked sponsored.

| Unit | What it is |
| --- | --- |
| `pullquote` | The advertiser's creative in a wide, short shape, after paragraph 3 |
| `aside` | A small poster floated right so the words flow around it with a gutter beside and below it (`--mom-ad-aside-gutter`); full width on a phone. After paragraph 2 |
| `story` | A panel in the reading column, after paragraph 4 |

## Known gaps

- The Card is inserted as the fifth card, so a full page of six cards becomes seven. Page size is not changed.
- The home page has no card grid of six, so it carries no Card.
- Ads have no start and end dates yet: add and remove them in the file. A date test would make a page change just because time passes.
- The house pictures were drawn at a wide window's scale (text at 75% of its designed size, as the site draws it), except the narrow band, which was drawn at a phone's. The text in a picture is part of the picture, so it does not follow the 75% rule.
- Papyrus's own ad links to `https://p.apyr.us/` with `utm_` parameters (confirmed by Ryan). Anthus's links to `https://anth.us/ai-solutions/` with `utm_` parameters (not yet confirmed).
