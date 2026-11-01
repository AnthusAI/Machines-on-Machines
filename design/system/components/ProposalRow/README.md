A story idea AI proposed, with its state and the readers' net vote.

- **Provide** from `_data/proposals/` and `_data/reader/votes/proposal.json`: `title`, `net` (order by it), `state` ("Open for votes", "Approved by <name>", "Declined") with `approved` when an editor approved it, `href`, and vote handlers that call the reader API.
- Every row says "Proposed by AI" in `machine`; the up vote is `human` because voting is a person's choice.
- Needs the site's `proposals.publish` setting and, for votes, reader sign-in. Until reader writes open, show the rows without the vote buttons' handlers and say "Sign in to vote" once, not on every row.
