# Handoff: from design to a running site

Written at the end of the design sessions on 2026-11-01. It records what was decided and why, how each part of the design maps onto Papyrus, and what to build next.

## Decisions

- **Its own Papyrus site.** Machines on Machines gets its own backend, newsroom app and corpus. The read.p.apyr.us knowledge base and articles (corpus `p-apyr-us`, repository `AnthusAI/p.apyr.us`) move here, and read.p.apyr.us redirects here. p.apyr.us stays the Papyrus marketing site.
- **Tagline:** "Information About Information Systems".
- **Palette N2:** pink-led (rosa mexicano `brand`), indigo-navy at night. Teal `machine` = made or done by machines, gold `human` = chosen by people. Day and Night are designed together; always check both.
- **Home page: B1 "Magazine first"** (`design/canvas/R10-Magazine.dc.html`). Stories first, then the newsroom's public parts woven in, so a first-time reader sees journalism before tables.
- **Section pages:** the "Machines on [Section]" sticker and topic pulse bands (`F-Section`).
- **Article pages:** a bold right-hand spine carrying the brand (`F-Leaf`). Branding is bold but secondary.
- **Wiki term pages:** "Machines on Meaning" (`F-Wiki`). Hashtags in stories link to wiki terms.
- **Wordmark:** MACHINES ON MACHINES in Anton, with "on" as the biggest word in a tilted gold seal behind the words (canvas Wordmark page, option D). Stacked in the sticker and spine, inline in the nav and footer. No drawn logo.
- **No "top readers"** or other community leaderboards until there are readers beyond the editors.
- **Placeholder art:** cards without an image draw seeded brand art; research papers get the `pages` composition (`components/PlaceholderArt`).

## The home page, mapped onto Papyrus

The order is in `design/system/README.md` ("Home page recipe"). Each slot is a stock Papyrus include on `web/pages/home.md`:

| Slot | Papyrus | Component |
| --- | --- | --- |
| Lead story | `::include{kind="listing" ... count="1"}` | lead markup in `F-Home` / `R10-Magazine` |
| Sticker and two side stories | `listing`, `card` hook | `Sticker`, `StoryCard size="small"` |
| Just accepted | `::include{kind="references" select="recent" count="3"}` | `ReferenceCard` |
| Three more stories | `listing` (use `types` to pick articles or posts) | `StoryCard` |
| Talking now | `::include{kind="threads" select="recent" count="2"}` | `ThreadCard` |
| First loop band | `::band` or a `block` hook | `LoopBand` |
| Cyclotron recommends | `::include{kind="references" select="recommended" count="3"}` | `ReferenceCard` with confidence meter |
| Proposals | proposals data, needs `proposals.publish` | `ProposalRow` |

Setup (see the Papyrus repository's `docs/home-page.md`):

- `projection.json`: `homePage` with `references` (corpus = this site's corpus), `threads: {"enabled": true}`, `forum: {}` for read-only thread pages at `/conversations/<key>/`, and `freshness`.
- `papyrus.config.ts`: `backend.plugins: ["home-page"]` so curation changes refresh the page without anyone running a command.

## Known gaps in Papyrus (checked against Papyrus 5.67)

- No voting on references (votes exist for items, submissions, stories, proposals and concepts).
- Forum posting is not implemented; thread pages are read-only. Do not promise readers they can reply.
- Reader writes (votes, sign-in) stay closed until Prospectus accounts are set up for the site.
- No hashtag pages; hashtags link to wiki term pages instead.
- The link from a story to the references it drew on is not public yet.

## Build plan

1. **Scaffold the site from `AnthusAI/Shipped-web`.** `papyrus.config.ts` (`defineSite`), `web/projection.json`, `web/css/site-theme.css`, `web/hooks.py`, `web/pages/`, `infra/site.json`, `requirements-publication.txt`, CI. Pin the current Papyrus version (5.67.0 at handoff) in all four places Shipped-web pins it. Pick a site id and corpus key (suggested: `machines-on-machines`).
2. **Theme.** Ship `design/system/tokens.css` and `components/bundle.css` as site stylesheets, and port the components to `web/hooks.py` with the same markup and `mom-` classes: `masthead`/`nav.brandHtml` for the wordmark, `card` for story, reference and thread cards (including `PlaceholderArt`'s seeded choice), `page_body`/`main` for the sticker and spine, `block` or `::band` for loop bands, `item_decorator` for provenance chips.
3. **Pages.** Home (B1), section index, article, wiki term, the wire (all accepted references), Conversations, Proposals.
4. **Fixtures and preview.** Sample content and `_data/home-page/*.json` under `tests/fixtures/` so every component renders locally:
   `papyrus ops content project --all --from-dir tests/fixtures/content --static-dir web --knowledge-dir tests/fixtures/knowledge --out /tmp/out`
5. **Tests.** Gherkin scenarios in `features/` for the home page slots, placeholder art, the attribution wording and both themes.

## Data migration from p.apyr.us

The articles and the knowledge base live in the backend, not in Git.

- **Content:** the `p-apyr-us` corpus. Sections today: "Papyrus" (`/papyrus/`) and "Newsroom How-To" (`/how-to/`). Decide whether they become Machines on Machines sections or fold into new ones.
- **Doctrine and sections:** `corpora/*.yml` in `AnthusAI/p.apyr.us` (publication doctrine approved 2026-10-21, newsroom sections, public topics, analysis profiles, steering). They mirror production records; re-create them for the new site in its newsroom, then rewrite the doctrine for the broader AI/ML mission.
- **Monitors and Cyclotron:** point the source monitors and the Cyclotron recommender and router at the new corpus so references arrive, are scored and are accepted here, which is what feeds "Just accepted" and "Cyclotron recommends".
- **Redirects:** read.p.apyr.us paths to their new URLs here, at the edge (read.p.apyr.us's CloudFront distribution is `E2EM0JLBC2W9WW`).

## Steps only a person can do

- Create AWS access (`aws sso login`) and deploy the app shell.
- Approve the GitHub App connection and fill in the numeric `ownerId` and `repoId` in `infra/site.json`.
- Google OAuth client for the newsroom.
- Certificate, edge stack and DNS for the production domain.
- `papyrus publication init` for the new publication.
