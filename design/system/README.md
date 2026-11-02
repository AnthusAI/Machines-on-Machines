Machines on Machines is an AI newsroom that covers AI: research agents find stories, classifiers rank them, writing agents draft them, and editors steer. The subject is dry, so the page reads like a newspaper: ink on paper, one ink-blue signature, and bold type and shapes doing the shouting instead of color. Content always leads. Load Anton and Archivo from Google Fonts in every surface that uses this system.

## Voice and content

- **The name** is *Machines on Machines*: title case with a lowercase "on" in running text, all caps in Anton when it is set as the wordmark, with "on" as the biggest word, stamped in a tilted seal behind MACHINES. Never abbreviate it in public copy.
- **The tagline** is *Information About Information Systems*. Set it in title case, or in Anton capitals beside the wordmark.
- **Sections are named with the same pattern**: *Machines on Agents*, *Machines on Research*, *Machines on Policy*. The wiki's spine reads *Machines on Meaning*.
- **Say who made what, in Papyrus's words.** Every story, post, reference and wiki entry carries provenance labels: "Drafted by AI", "Approved by <name>", "Written by <name>", "Editor's pick", "Accepted by an editor", "Accepted by Cyclotron", "Recommended by Cyclotron, not yet accepted", "Edited by AI on <date>", "Reviewed by <name> on <date>". In conversations, authors are a public handle or the role labels **Editor** and **AI**. Never hide that a machine wrote something, never imply a person wrote what AI drafted, and never write "desk".
- **Headlines** are plain, specific statements or questions ("Who owns an agent's mistakes?"), set uppercase in Anton. Deks are one sentence.
- **Hashtags** are links into the knowledge base: CamelCase, no spaces (`#DurableExecution`, `#AgentEvals`). Every hashtag on the site resolves to a wiki entry.
- Address readers as "you" in calls to action ("Steer this story", "Suggest an edit"). No emoji anywhere.

## Color: three roles

The palette is **Ink blue**: near-black ink on cool white paper, with navy as the one strong color. Machine and human are quiet tints, not colors to notice. Color still carries meaning, so learn the three roles before using any fill.

| Role | Fill | Text on it | Means |
| --- | --- | --- | --- |
| Brand | `brand` (navy) | `on-brand` | The publication itself: sticker, spine, loop bands, the active section tab |
| Machine | `machine` (cool blue-gray) | `on-machine` | Made or found by machines: agent bylines, the wire, classifier scores, trends, the wiki |
| Human | `human` (warm gray) | `on-human` | Chosen by people: editor's picks, "Approved by", pull quotes, steering buttons |

- Ground every page in `paper`; group with `panel`; set cards that sit on a colored fill in `card`.
- Body text is `ink`; metadata is `ink-muted`. Links into the knowledge base and score bars use `machine-text`.
- **Never use a machine color for something a person decided, or the reverse.** If a story was drafted by an agent and edited by a person, it gets both chips.
- Inside loop bands, the word "on" and any hashtags take the band's accent (`on-brand-accent`, `on-machine-accent`, `on-human-accent`).
- **Keep it neutral.** Navy is the only strong fill, and it belongs to the brand structures (sticker, spine, bands, the active tab). Never add another hue; never fill a large content area with `machine` or `human` when `panel` will do.
- **Day and Night are designed together.** By day, the tints are pale and carry `ink`; navy carries light text. By night, the paper turns blue-black, navy lifts to slate blue and the tints deepen. Always show both themes when presenting work.
- The focus ring is a solid 3px `focus` outline with a 2px offset.

## Type

- **Anton** (`display`) for the wordmark, headlines, panel heads, pull quotes and loop bands: always uppercase, tight leading (`masthead`, `headline-article`, `headline-lead`, `pull-quote`, `panel-head`, `display-term`).
- **Archivo** (`text`) for everything read at length or operated: `dek`, `body`, `card-title`, `item-title`, `ui`, `caption`, `label`.
- Keep body copy to the `measure` (680px). Balance headline wrapping.
- `label` is the only letter-spaced style: uppercase, 0.08em, used on chips and section tags.

## Shape and layout

- **No hairline rules or thin borders, ever.** Separate and group with fills (`panel`, `card`, colored blocks) and space.
- Corners are generous and consistent: chips `radius-md`, buttons `radius-lg`, cards `radius-xl`, panels and images `radius-2xl`, the sticker `radius-sticker`, nav pills `radius-pill`.
- The **sticker** and the wordmark's **seal** are the only tilted elements (`sticker-tilt`, `wordmark-seal-tilt`). The sticker has a solid `machine` backing offset 16px down and right. No drop shadows anywhere.
- Desktop pages use a 12-column grid with a `space-7` gutter and a `space-12` page margin; phones keep at least a `space-4` gutter.

## The brand on each page type

The brand is bold but secondary: it never sits above the first piece of content.

- **Home page: stories first, the newsroom as samples.** Content leads; the community tables live on their own pages (Wire, Conversations, Proposals) and the home page shows a few of each. In order:
  1. The lead story (16:9 image, provenance chips, `headline-lead`, dek) top-left; the `Sticker` over the top edge in the right column with two `StoryCard`s under it.
  2. **Just accepted**: three `ReferenceCard`s (`references` include, `select="recent"`, `count="3"`), linking to the whole wire.
  3. Three `StoryCard`s.
  4. **Talking now**: two `ThreadCard`s (`threads` include, `select="recent"`), linking to all conversations.
  5. The first `LoopBand`, never higher than this, so it is never on screen with the sticker.
  6. Side by side: **Cyclotron recommends** (`select="recommended"`, three, with confidence) in a `machine` panel and **Proposals** (three `ProposalRow`s) in a `panel`.
  7. Footer.
- **Cards carry the content.** Every card has an image and a one-sentence blurb. When a story or source has no image, or its image fails to load, the card draws `PlaceholderArt`: brand shapes chosen from the item's URL, so the same item always gets the same art. Research papers get the `pages` composition. Never use a stock photo or a generic gray box instead. Our own stories use Anton (`story-headline`, `story-headline-small`); outside sources and threads use bold Archivo (`reference-title`). No grid runs more than three across at a 1280px page width.
- **Section pages.** The sticker names the section ("Machines on Agents"). The site name shrinks to a brand-colored pill at the start of the nav. Loop bands carry the section's live topics with a label ("Rising fast" in machine, "Editors are watching" in human, "New this week" in brand), and hotter topics slide faster.
- **Article pages.** A `Spine` runs down the right edge: the stacked wordmark at the top as the home link, the section name ("Machines on Research") running down it, and a `brand-progress` reading fill rising from the bottom. Margin notes sit beside the paragraph they explain: wiki and source notes in `machine`, editor's notes in `human`. Close every article by telling readers what the colors mean.
- **Wiki term pages.** The spine reads "Machines on Meaning". The term is set in `display-term` with a `machine-text` "#". Provenance chips, a mentions-over-time chart in a `machine` panel, connected terms with their relationship, the stories that use the term, and the sources the agents found.

## Motion

- Loop bands translate sideways at a rate tied to scroll position; neighbouring bands move in opposite directions. On section pages, a band's speed reflects how fast its topics are rising.
- The spine's progress fill tracks reading position.
- Under `prefers-reduced-motion`, bands stay still and the fill updates without animation. Nothing else moves.

## Logo and iconography

- There is no drawn logo. The wordmark is type: render it with the `Wordmark` component (inline, stacked or vertical), never as an image.
- There is no icon set yet. Use words on buttons and labels. If an icon becomes necessary, use a single-weight outline at the size of the adjacent text, colored with the surrounding text token.

## Newsletter

The Weekly is light mode only, in the Papyrus email template: a navy `brand` header band with the wordmark as an image and the list name in mono capitals, a white card, navy links (`brand-text`), and a navy footer band. The lead story leads with its image; every story carries its provenance line in italics. Body type falls back to Helvetica/Arial because mail clients drop web fonts. The theme and a sample issue are in `design/newsletter/` in the site repository.
