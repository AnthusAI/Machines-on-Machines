---
name: papyrus-review-associations
description: Review and curate associations for recent Papyrus Stories and References, including Concept tags, related Articles and Posts, and links among sources. Use for a newsroom association pass over a time window or a specified set of records.
---

# Review Papyrus associations

Use the selected newsroom. Review the last 48 elapsed hours by default. Accept a different duration, explicit start and end, or a supplied set of records. Fix the cutoff at the start of the run and report it with the time zone. Use Story update time and Reference intake time to select recent records. When comparing candidates for recency, use publication or source date where available, so editing a record does not make old material look new.

Use `papyrus stories list --sort updated --bucket none` and `papyrus references list --order newest` as starting points. Check the available flags and returned timestamps in the installed CLI. Include Articles, Posts, and draft Stories unless the user narrows the scope. Increase limits or use supported pagination until the oldest row crosses the cutoff. If an endpoint caps results before the cutoff, report what was covered. The window selects records to review. Older records remain eligible as association targets.

## Decide what belongs together

For each record, inspect its text or source and inventory the current associations, including incoming links where available. Use the newsroom record view if the CLI omits links. Discover candidates with `papyrus stories suggest-associations` when available. Otherwise use `papyrus stories suggest-links`, accepted Concept search, and newsroom search. Suggestions, shared tags, and search scores are leads. Read enough of both records to identify what a reader gains from the link.

Evaluate existing and proposed associations together. For each, decide whether it earns its place, adds something distinct, duplicates a better link, or needs removal review.

- A Concept tag should describe a substantive subject, method, or idea in the record. Prefer an existing specific Concept over a vague category or a near synonym.
- A related Story, Article, or Post should supply useful context, a concrete example, a contrasting result, or a meaningful follow-up. A shared keyword or section is insufficient.
- A source relationship should reflect actual use or a documented relationship between sources. Preserve accurate citation, consultation, and provenance links. Replacing a related reading suggestion does not change what a story actually used.
- Rank by relevance and value to the reader first. When candidates serve the same purpose comparably well, prefer the higher editorial quality rating. At equal quality, prefer the more recent item. Give an older primary source its place when it adds something newer material cannot. There is no link quota.

Collapse duplicate targets, mirrored related links, and redundant coverage. Keep multiple links when each has a distinct purpose. Use published Articles and Posts and accepted References for public recommendations. Draft relationships can be useful for newsroom planning when the user has asked for them.

## Apply and verify

Use `papyrus guide tag-and-link` and the installed commands' help for exact syntax.

| Intended association | Papyrus command |
| --- | --- |
| Story, Article, or Post → Concept | `stories link-concept --story … --concept …` |
| Reference → Concept | `references link-concept --reference … --concept …` |
| Story ↔ Story, Article, or Post | `stories link-story --story … --to …` |
| Story ↔ accepted Reference for further reading | `stories link-story --story … --reference …` |
| Story → Reference actually used | `stories link-reference --story … --reference … --role consulted\|cited\|based_on` |
| Reference → Reference | `references link --reference … --to-reference … --predicate related_to\|cites\|supports\|contradicts` |

Use stable IDs or lineage keys and a short note that explains the connection. Respect predicate direction. Resolve ambiguous Concepts by key. A citation edge records source use and does not add a citation to the article text.

Apply well-supported additions when the request authorizes changes. For review-only requests, present recommendations. For pruning, identify the exact edge and why it should go. Remove it only when authorized and through a supported operation. If the current Papyrus lane cannot remove it, report it as pending. Avoid stacking a redundant new link on top of a weak link that still needs removal. Do not change ratings, publish drafts, or create Concepts as part of an ordinary association pass.

Read back affected records to confirm the saved edges. After a timeout, check whether the edge exists before retrying. If it is still absent, retry once and report any unresolved result. Distinguish a saved link from a public page refresh. Report the review window, records covered, verified changes, and any recommended removals or gaps in coverage.
