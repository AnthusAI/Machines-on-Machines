A full-width band of giant repeating words that separates page sections and slides sideways as the reader scrolls.

- **Provide**: `role` (`brand`, `machine` or `human`), `words` (defaults to the brand loop "Machines on Machines on"), an `offset` in px that the page updates from scroll position, and an optional `label`.
- **Home page**: brand loops only, no labels, in brand, human and machine bands down the page. Neighbouring bands move in opposite directions at the same rate.
- **Section pages**: the section name alternating with its live hashtags, with a label that says why the band exists ("Rising fast" in `machine`, "Editors are watching" in `human`, "New this week" in `brand`). Hotter topics move faster.
- The band's words are decorative and hidden from assistive technology; put real links to the same hashtags elsewhere on the page.
- Never place a band directly under the hero. On the home page, the first band goes far enough down (after at least two content sections) that it is never on screen at the same time as the sticker. Keep at least one content block between two bands.
- Hold the row still under `prefers-reduced-motion`.

## On the home page

The home page has exactly two bands, each repeating one phrase. First: "Information About Information Systems" (`words`). Second: "Machines on Machines", the default, whose continuous pattern reads "Machines on Machines on". Don't add other slogans. Section pages keep their topic bands.
