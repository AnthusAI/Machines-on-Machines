A source the monitors found: its preview image and site name, who accepted it, its own title and summary.

- **Provide** the fields of `_data/home-page/references.json`: `title`, `summary`, `image`, `siteName`, `host`, an age from `acceptedAt` or `arrivedAt`, `status` (`accepted` or `recommended`), `actor` (`human`, `cyclotron`, `agent`, `rule`) and, for recommended ones, `confidence`.
- The status chip follows the actor: "Accepted by an editor" in `human`; "Accepted by Cyclotron", "Accepted by AI" or "Accepted by a rule" in `machine`; "Recommended by Cyclotron, not yet accepted" in `machine-text` on `card`, with the five-segment confidence meter.
- Titles are the source's own words in `reference-title`, never rewritten and never set in Anton.
- Fed by the `references` include: `select="recent"` for "Just accepted" (three on the home page), `select="recommended"` for "Cyclotron recommends". Three across at most.
- Without an `image`, or if it fails to load, the card draws `PlaceholderArt` seeded by `href`. Links to arXiv, OpenReview, ACL Anthology, PMLR, NeurIPS, ACM, IEEE, Semantic Scholar, bioRxiv or any `.pdf` are treated as papers and get the `pages` composition; pass `kind="paper"` for other paper hosts.
