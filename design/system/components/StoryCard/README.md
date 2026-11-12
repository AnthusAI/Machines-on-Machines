One of our own stories (an article or post) as a card: image, provenance, an Anton headline, the date and a one-sentence blurb, in that order.

- **Provide**: `headline`, `blurb` (always; one sentence), `provenance` chips in Papyrus wording, `image` (the story's own image; without one, or if it fails to load, the card draws `PlaceholderArt` seeded by `href`), `kicker` ("Post · Models"), `meta` (the date, "30 Oct 2026"), `href`, and `size`.
- `size="large"` (`story-headline`, 40px, 16:9 image) in grids of up to three; `size="small"` (`story-headline-small`, 34px, 16:9 image) under the sticker or in rails.
- Fed by the `listing` include; filter by `types` when a slot needs only articles or only posts.
- Never more than three across at 1280px. Never drop the blurb to fit more cards.
- **Date, no byline.** On every card the date sits between the headline and the blurb, in `mom-story-card-date`: `ink-muted` (6.2:1 on `paper` in Day, 7.8:1 in Night; 5.1:1 and 5.3:1 on the `machine` and `human` panels at the lowest), 14px regular, so it reads as secondary but stays above the 4.5:1 and 14px floors. A card never shows a byline; the byline belongs to the article page. The date is one rhythm row (a 20px line, an 8px gap), so cards in a row still line up.
