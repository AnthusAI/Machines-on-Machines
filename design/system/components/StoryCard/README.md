One of our own stories (an article or post) as a card: image, provenance, an Anton headline and a one-sentence blurb.

- **Provide**: `headline`, `blurb` (always; one sentence), `provenance` chips in Papyrus wording, `image` (the story's own image; without one, or if it fails to load, the card draws `PlaceholderArt` seeded by `href`), `kicker` ("Post · Models"), `meta` ("22 messages"), `href`, and `size`.
- `size="large"` (`story-headline`, 40px, 4:3 image) in grids of up to three; `size="small"` (`story-headline-small`, 34px, 16:9 image) under the sticker or in rails.
- Fed by the `listing` include; filter by `types` when a slot needs only articles or only posts.
- Never more than three across at 1280px. Never drop the blurb to fit more cards.
