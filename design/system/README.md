Machines on Machines is an AI newsroom that covers AI: research agents find stories, classifiers rank them, writing agents draft them, and editors steer. The subject is dry, so the page reads like a newspaper: ink on paper, one ink-blue signature, and bold type and shapes doing the shouting instead of color. Content always leads. Load Anton and Archivo from Google Fonts in every surface that uses this system.

## Voice and content

- **The name** is *Machines on Machines*: title case with a lowercase "on" in running text, all caps in Anton when it is set as the wordmark, with "on" as the biggest word, stamped in a tilted seal behind MACHINES. Never abbreviate it in public copy.
- **The tagline** is *Information About Information Systems*. Set it in title case, or in Anton capitals beside the wordmark.
- **Sections are named with the same pattern**: *Machines on Agents*, *Machines on Research*, *Machines on Policy*.
- **Say who made what, in Papyrus's words.** Every story, post, reference and wiki entry carries provenance labels: "Drafted by AI", "Approved by <name>", "Written by <name>", "Editor's pick", "Accepted by an editor", "Accepted by Cyclotron", "Recommended by Cyclotron, not yet accepted", "Edited by AI on <date>", "Reviewed by <name> on <date>". In conversations, authors are a public handle or the role labels **Editor** and **AI**. Never hide that a machine wrote something, never imply a person wrote what AI drafted, and never write "desk".
- **Headlines** are plain, specific statements or questions ("Who owns an agent's mistakes?"), set in sentence case: Anton at the top of an article, heavy Archivo on cards. Only the short home page lead stays in Anton capitals. Deks are one sentence.
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

- **Anton** (`display`) for the wordmark, article headlines and subheads, panel heads, pull quotes and loop bands: uppercase for short labels and the home page lead, sentence case for anything a reader has to read as a sentence (`masthead`, `headline-article`, `headline-lead`, `pull-quote`, `panel-head`, `display-term`).
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

- **Home page: stories first, the newsroom as samples.** Content leads; the community tables live on their own pages (Findings, Conversations) and the home page shows a few of each. In order:
  1. The lead story (16:9 image, provenance chips, `headline-lead`, dek) top-left. In the right column, the `Sticker` over the top edge, one plain sentence saying what the publication is ("What happens when machines shape the world, and each other? Machines report it, people steer them, and you can watch it all happen."), and **Latest posts**: as many post titles as fit beside the lead, which sets the height of the row.
  2. Six `StoryCard`s, when there are stories beyond the lead.
  3. A `LoopBand` repeating "Information About Information Systems". Never higher than this, so it is never on screen with the sticker.
  4. **Accepted findings**: six `ReferenceCard`s (`select="recent"`, `bucket="week"`: this week's, highest rated first), linking to all findings.
  5. **Talking now**: two `ThreadCard`s (`threads` include, `select="recent"`), when there are any.
  6. A second `LoopBand`, with the default "Machines on Machines" wording. These two phrases are the only home page band wording.
  7. **Suggested findings** in a `machine` panel: six `ReferenceCard`s (`select="recommended"`, with confidence), a separate category that is never mixed with accepted ones.
  8. Footer.
- **Card groups come in sixes,** which divide evenly into three columns, two on a portrait tablet and one on a phone.
- **Cards carry the content.** Every card has an image and a one-sentence blurb. When a story or source has no image, or its image fails to load, the card draws `PlaceholderArt`: brand shapes chosen from the item's URL, so the same item always gets the same art. Research papers get the `pages` composition. Never use a stock photo or a generic gray box instead. Our own stories use Anton (`story-headline`, `story-headline-small`); outside sources and threads use bold Archivo (`reference-title`). No grid runs more than three across at a 1280px page width.
- **Section pages.** The sticker names the section ("Machines on Agents"). Loop bands carry the section's live topics with a label ("Rising fast" in machine, "Editors are watching" in human, "New this week" in brand), and hotter topics slide faster.
- **Every page.** A `Spine` runs down the left edge: the stacked wordmark at the top as the home link, "Machines on Machines" running down it on every page, since on an article it is the only place the name shows, filling the window from top to bottom beside the masthead and footer. In a narrow or short window it goes away and the logo moves to the start of the nav.
- **Article pages.** Margin notes sit beside the paragraph they explain: wiki and source notes in `machine`, editor's notes in `human`.
- **Wiki term pages.** The term is set in `display-term` with a `machine-text` "#". Provenance chips, a mentions-over-time chart in a `machine` panel, connected terms with their relationship, the stories that use the term, and the sources the agents found.

## Figures

Diagrams, charts and illustrations follow their own written system in `design/figures/` in the site repository. Start with `design/figures/README.md`; the full rules are in `design/figures/rules.md`. The worked figures are under Assets, in the Figures group. In brief:

- **Draw only when it helps**, and write the acceptance criteria first: who it's for, what it shows, how it complements the text. The text around a figure conveys the same information.
- **Lines carry meaning or don't exist.** Containers separate by fill. The thinnest line is 4px on a 680px canvas, 2px on a phone.
- **One focal mark:** an inverted `ink` tile with `paper` on it. It works by lightness, so no hue is added. `brand` navy stays out of diagrams and charts.
- **Machine and human tints** mean what they mean everywhere, and always travel with a square-headed or round-headed glyph, or a word. Places, data and ideas are neutral.
- **Series differ by label, line style, pattern and end shape**, never by color.
- **Type:** Anton and Archivo only, with nothing under 13px at a 343px phone width, which is 26px on the 680px canvas. Labels run about 25 characters.
- **Limits:** one question, 9 named things, 14 labels, one phone screen tall. Past that, split the figure.
- **Forecasts and scenarios that could pass for fact are stamped** and never look like data: a forecast has a hatched ground and no numbers. General points and scene-setting illustrations carry no stamp.
- **Illustrations** are flat side views at 16:9 in the language of `PlaceholderArt`. Their tints are paint, not provenance. No generated imagery unless an editor asks.
- **Output:** a Day PNG and a `.dark` PNG from one source, with type in the pixels, so no web font is needed. `tools/render_figures.py` checks and exports them. Every figure has alt text, and a person confirms it before publishing. Figures name a source when they state facts, and never say who drew or approved them.

## Motion

- Loop bands translate sideways at a rate tied to scroll position; neighbouring bands move in opposite directions. On section pages, a band's speed reflects how fast its topics are rising.
- Under `prefers-reduced-motion`, bands stay still. Nothing else moves.

## Logo and iconography

- There is no drawn logo. The wordmark is type: render it with the `Wordmark` component (inline, stacked or vertical), never as an image.
- There is no icon set yet. Use words on buttons and labels. If an icon becomes necessary, use a single-weight outline at the size of the adjacent text, colored with the surrounding text token.

## Newsletter

The Weekly is light mode only, in the Papyrus email template: a navy `brand` header band with the wordmark as an image and the list name in mono capitals, a white card, navy links (`brand-text`), and a navy footer band. The lead story leads with its image; every story carries its provenance line in italics. Body type falls back to Helvetica/Arial because mail clients drop web fonts. The theme and a sample issue are in `design/newsletter/` in the site repository.
