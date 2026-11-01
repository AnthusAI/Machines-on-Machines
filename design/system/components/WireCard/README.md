One item a research agent found, with the classifier's relevance score as a bar and a number.

- **Provide**: `section` (the section the classifier ranked it for), `title` (the found item's own title, not a rewrite), `source` (arXiv, GitHub, a filing), `score` from 0 to 1, and `href` to the original.
- Stack cards inside a `machine` panel headed "From the wire" or "Found for this section", with a one-line note that agents found them and classifiers ranked them.
- Order by score, highest first. Never present wire items as edited stories; once an editor picks one up, it becomes a story with a `human` chip.
