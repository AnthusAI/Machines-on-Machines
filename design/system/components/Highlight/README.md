A phrase an editor chose, marked so a reader who skims finds the claim.

- **Author it** with two equals signs around the phrase: `==Employees and customers will be the ones it sees on its rounds.==`. Markus renders it as `<mark>`. It nests with emphasis and links (`==a *key* claim with [a source](https://example.com)==`) and may wrap across lines inside one paragraph.
- **Use it for** the one sentence or phrase in a section that carries the claim: what a skimming reader should leave with. At most about one or two per article section, three or four in a long article. Never a whole paragraph, never a heading, never a caption, and not a repeat of the pull quote.
- **Look**: the `human` fill with `on-human` text (a highlight is a choice a person made, which is what `human` means), a small rounded rectangle (`radius-sm`), padding in `em` so it follows the type, and `box-decoration-break: clone` so every line of a wrapped phrase keeps its fill and corners. No border, outline or underline.
- **The cue that is not colour**: weight 600, between the 400 of body text and the 800 of bold and links. Ryan and other colourblind readers see the weight even where the warm gray fill is faint, and the fill adds to it, not the other way round. A tint alone never carries the meaning.
- **Contrast**: `on-human` on `human` is 13.7:1 by day and 10.1:1 by night (WCAG AA asks 4.5:1). A link inside a highlight takes the highlight's text colour and keeps its underline.
- **Fallbacks**: in forced-colors mode the browser's `Mark` and `MarkText` system colours are used; in print, where fills are usually dropped, the phrase is set heavy and underlined.
- Citation numbers inside a highlight behave as everywhere else (small, raised, spaced when they run together).

There is no React component: the highlight is plain `<mark>` styled by `web/css-src/site-theme.src.css` (see "highlight"). Authors' guide: `docs/highlights.md`.
