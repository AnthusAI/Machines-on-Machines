Feature: The home page puts stories first and weaves the newsroom in
  A first-time reader should see journalism before tables. The home page leads with a story,
  then shows a few sources, and later conversations and concepts as samples of the newsroom's public parts (see home-sections.feature).
  Each slot is a stock Papyrus include drawn with the design system's cards.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The slots appear in the order the design recipe gives
    When I open the page "/"
    Then "mom-story-card-lead" comes before "mom-sticker"
    And "mom-sticker" comes before "mom-top-posts"
    And "mom-top-posts" comes before the Findings grid

  Scenario: The home page ends with a Findings grid of accepted References, with a link to all of them
    The bottom of the home page used to show References no editor had accepted, under "Just Found". It now shows this week's best accepted References, never a video, in the order the Findings page uses, and "More Findings…" leads to /findings/. Public pages no longer show a Reference nobody has accepted.
    When I open the page "/"
    Then the home page ends with a "Findings" grid of accepted References, none of them a video
    And the page contains "<a href="/findings/">More Findings…</a>"
    And the page does not contain "Just Found"
    And the page does not contain "How It Works"
    And the page does not contain "Recommended by Cyclotron, not yet accepted"
    And the page does not contain "% confidence"
    And the page does not contain "Recent findings"
    And the page does not contain "Up for consideration"
    And the page does not contain "Talking now"

  Scenario: Proposals are not on the public site
    When I open the page "/"
    Then the page does not contain "Proposals"
    And the page does not contain "Placeholder proposal"

  Scenario: A band separates the blocks
    When I open the page "/"
    Then "mom-story-card-lead" comes before "mom-top-posts"
    And "mom-top-posts" comes before the Findings grid
    And the home page has 2 bands

  Scenario: The findings page lists accepted sources only
    When I open the page "/findings/"
    Then the page contains "Accepted automatically"
    And the page does not contain "Accepted by an editor"
    And the page does not contain "Not accepted yet"
    And the page does not contain "Found by machines"

  Scenario: No page links to the retired Just Found page
    Then no projected page links to "/just-found/" and none is projected there
    And the projection has no redirect from "/wire/"

  Scenario: The side of the lead holds no story cards
    When I open the page "/"
    Then the side of the lead has no story cards

  Scenario: A decorative halftone panel fills the height the lead leaves under the site card
    The lead sets the row's height, so the space under the site card varies from nothing to most of a screen. A panel of halftone dots fills it:
    decoration with no words or links, hidden from screen readers, drawn by the script, and shown only where the card sits beside the lead.
    When I open the page "/"
    Then the side of the lead ends with the halftone panel, after the site title card
    And the halftone panel is hidden from screen readers and holds no words or links
    And the stylesheet "/css/site-theme.css" shows the halftone panel only beside the lead
    And the halftone panel reaches down beside the next section's heading, which keeps to the lead's columns
    And the halftone panel sits under the sentence above by the gap it leaves above the cards, lined up with the sentence's text
    And the halftone panel's corners are the article cards' corners

  Scenario: The site card's column on the home page is one of the article columns under it
    On a wide window the article rows keep three columns until they go two sections across, so the top row keeps the same three there.
    Then the stylesheet "/css/site-theme.css" keeps the home page's top row on the article rows' three columns until they go two across
    And the stylesheet "/css/site-theme.css" starts the home page's sentence on the column's left edge, the edge of the pictures below

  Scenario Outline: The Articles, Posts, Findings and Videos pages carry the home page's halftone under the site card
    The page header's site card takes the home page's card column at every width, so it keeps its size and place from page to page, and the halftone
    fills the space under it beside the first row, which stops one of those columns short of the card.
    When I open the page "<page>"
    Then the page header ends with the halftone panel, after the site title card
    And the stylesheet "/css/site-theme.css" gives the page header the home page's columns where it has the halftone
    And the script "/assets/mom.js" fits the page header's halftone under the site card, beside the first row

    Examples:
      | page       |
      | /articles/ |
      | /posts/    |
      | /findings/ |
      | /videos/   |

  Scenario: Other page headers have no halftone
    When I open the page "/about/"
    Then the page has no halftone panel

  Scenario: The Top Posts section always follows Videos
    When I open the page "/"
    Then the Top Posts section comes right after the Videos block

  Scenario: The latest posts sit beside the lead on very wide windows and under it on narrower ones, and Top Posts leaves them out
    The latest posts are their own item in the top row, newest first. Once the article rows go two sections across, the row has a column
    between the lead and the site card, which the posts fill, showing only the whole posts that fit. Narrower, they are a full-width grid of
    whole rows under the lead and the card, above the first section. The section further down is Top Posts: the site's ranking, the same as
    Top Articles (this week first, the editors' best-rated first inside it). It leaves out whichever posts are shown above at the current
    width, and shows twelve of the rest.
    When I open the page "/"
    Then the top row holds a Latest Posts panel of posts with covers after the site card's column, linking to all posts
    And the Latest Posts panel lists posts newest first and the Top Posts section lists them in the site's ranking
    And the Top Posts section further down holds the posts shown above too, with enough beyond them to show twelve
    And the stylesheet "/css/site-theme.css" shows the latest posts beside the lead on very wide windows and as a full-width grid under it narrower, only with the script
    And the script "/assets/mom.js" leaves out of the Top Posts section the posts shown whole above
    And the script "/assets/mom.js" stops the home page's halftone at the bottom of the card's column when the latest posts sit under the top row
    And the script "/assets/mom.js" prints the halftone, moves it with scrolling and holds it still under reduced motion

  Scenario: Findings are quiet compact rows, like posts, and each says it leaves the site
    Findings lead to other people's pages, so they must not outweigh our own work. Each is a small picture, a headline, the site and the date, opens in a new tab and carries the external-link icon.
    When I open the page "/"
    Then the home page ends with a "Findings" grid of accepted References, none of them a video

  Scenario: Card groups split into three, two or one columns
    Then the home page shows 12 findings, accepted ones only
    And the stylesheet "/css/site-theme.css" splits a panel of cards into three, two and one columns

  Scenario: The navigation offers articles, posts and findings
    When I open the page "/"
    Then the page contains ">Posts</a>"
    And the page contains ">Findings</a>"
    And the page contains ">Concepts</a>"
    And the page does not contain "Reading list"

  Scenario: The most recently active conversations are a section of their own near the bottom, not a rail beside the lead
    Then the home page lists the most recent conversations in a section of their own
    When I open the page "/"
    Then the page contains "All conversations"
    And the page contains "What counts as a crash for a long-running agent?"
    And the page contains "2 messages"
    And the page does not contain "This Week"

  Scenario: The footer says who publishes the site and offers the standard links
    When I open the page "/"
    Then the page contains ">About</a>"
    And the page contains ">Corrections</a>"
    And the page contains "https://anth.us/privacy/"
    And the page contains "#cookie-settings"
    And the page contains "Built with <a href="https://p.apyr.us" data-cta-location="footer">Papyrus</a>"

  Scenario: The site counts visits in the Anthus analytics property, with the consent banner
    Then the site's analytics property is "G-31SC26SDGX" with consent mode on

  Scenario: The cookie notice asks the site's own edge where the visitor is, and stays hidden until it knows
    The notice is region-aware (Papyrus `chrome.consent_mode.region_lookup`). Every consent signal starts denied, the page makes one anonymous request to the same site's /_papyrus/consent with a short timeout, and the notice markup is hidden until the answer says it is needed.
    When I open the page "/"
    Then the page asks "/_papyrus/consent" on its own origin without credentials
    And the cookie notice is in the page but hidden
    And the page contains "#cookie-settings"

  Scenario Outline: The notice fails closed
    A visitor skips the notice only when the edge answers that no notice is needed and names a two-letter country. Anything else, including no answer, shows the notice and keeps everything denied.
    When I open the page "/"
    Then the page's notice decision for the answer <answer> is <decision>

    Examples:
      | answer                                  | decision  |
      | {"country":"US","notice":false}         | no notice |
      | {"country":"DE","notice":true}          | notice    |
      | {"country":"US","notice":"false"}       | notice    |
      | {"notice":false}                        | notice    |
      | {"country":"USA","notice":false}        | notice    |
      | null                                    | notice    |
      | []                                      | notice    |

  Scenario: About and Corrections pages exist
    When I open the page "/about/"
    Then the page contains "various bots"
    When I open the page "/corrections/"
    Then the page contains "silently change a fact"

  Scenario: Every page uses the same site title card
    Then the home page and a type's listing both use the one site title card

  Scenario: Articles has its own page, broken apart into sections
    When I open the page "/articles/"
    Then the page contains "mom-section-title"
    And the page contains "Field Notes"
    And the navigation links Articles to "/articles/"

  Scenario: The section with the most recent update comes first
    Then sections with newer updates come first on the Articles page

  Scenario: An accepted reference shows its star rating, and a suggested one does not
    Then an accepted card rated 4 shows "4 of 5 stars"
    And an accepted card with no rating shows no stars
    And a suggested card shows no stars
    And the card reads the rating from the stock tile's data-stars
    And an accepted Reference rated 4 stars in the published data shows as our card with "4 of 5 stars" on Findings

  Scenario: The videos page lists only References of the video medium
    When I open the page "/videos/"
    Then the page contains "Fixture talk: cheaper evaluation runs"
    And the videos page shows no References of another medium
    And the page contains "mom-wire"
    And the stylesheet "/css/site-theme.css" keeps the card from covering the page when no accepted videos reserve room for it

  Scenario: The home page hides its post and story blocks when they have nothing in them
    Then the stylesheet "/css/site-theme.css" hides an empty post rail and an empty story section, even with whitespace inside

  Scenario: A card with a Night image draws both and the theme picks one
    Then a card with a Night image holds a Day picture and a Night picture
    And a card with no Night image holds one picture
    And the stylesheet "/css/site-theme.css" shows the Night card image on a dark theme

  Scenario: Conversation cards line up across a row, with the picture at the top right
    Then a thread card puts its anchor, title, picture, latest message and meta directly in the card
    And the stylesheet "/css/site-theme.css" shares the rows of thread cards across a row of cards

  Scenario: Story and finding cards line up across a row
    Then the stylesheet "/css/site-theme.css" shares the rows of story and finding cards across a row of cards

  Scenario: A conversation titled after its source doesn't say the title twice
    Then a thread card whose title repeats its source shows the title once

  Scenario Outline: A suggested source says in words how likely it is to be accepted
    Then a suggested card with confidence <confidence> says "<prediction>"

    Examples:
      | confidence | prediction                |
      | 1.00       | Very likely to be accepted |
      | 0.80       | Very likely to be accepted |
      | 0.79       | Likely to be accepted      |
      | 0.50       | May be accepted            |
      | 0.30       | Unlikely to be accepted    |
      | 0.05       | Very unlikely to be accepted |

  Scenario: The home page says what the publication is, under the site title card
    When I open the page "/"
    Then the page contains "What happens when machines shape the world, and each other? Machines report it, people steer them, and you can watch it all happen."
    And "mom-sticker" comes before "mom-home-purpose"
    And the page does not contain "mom-home-rail"
    And the page contains "Information About Information Systems"

  Scenario: The two home page bands each carry one phrase
    When I open the page "/"
    Then the first home page band repeats "Machines on Machines"
    And the second home page band repeats "Machines on Machines"

  Scenario: The nav and home page lead with the journalism
    When I open the page "/"
    Then the nav marks Findings, Videos, Conversations and Concepts as the newsroom group, and not Articles or Posts
    And the stylesheet "/css/site-theme.css" styles every nav pill the same
    And the stylesheet "/css/site-theme.css" shows every item of the home page lists and lays out the Top Posts mosaic

  Scenario: The Concepts page says it is a page per concept
    When I open the page "/wiki/"
    Then the page contains "Every concept our knowledge base tracks gets a page here"

  Scenario: The Articles page has the same page header as the other pages
    When I open the page "/articles/"
    Then "mom-page-top" comes before "mom-section-title"
    And the page contains "The top articles in each section, with a link to the rest of each section."
    And the page does not contain "mom-grid-sticker"

  Scenario: Conversations and Videos have short subtitles
    When I open the page "/conversations/"
    Then the page contains "The forum. Editors and AI discuss our stories and sources."
    When I open the page "/videos/"
    Then the page contains "Videos we think are worth watching."

  Scenario: Findings has no Accepted heading and no panel of suggested ones
    When I open the page "/findings/"
    Then the page does not contain ">Accepted</h2>"
    And the page does not contain ">Found by machines</h2>"
    And the page does not contain "Not accepted yet"

  Scenario: The sentence, the Latest posts heading and the post titles share one left edge
    Then the stylesheet "/css/site-theme.css" lines up the home sentence and the Latest posts heading with the post titles

  Scenario: Accepted findings and videos rank by stars within each week
    Then the page "/web/pages/findings.md" lists accepted findings by week, highest rated first
    And the page "/web/pages/videos.md" lists accepted findings by week, highest rated first

  Scenario: A source an editor accepted carries no acceptance chip
    When I open the page "/videos/"
    Then the page does not contain "Accepted by an editor"
    And the page does not contain "mom-reference-status-human"

  Scenario: A story's picture on a card is a path from the site root
    The newsroom stores a picture as media/assets/<slug>/<file>. A card read that path relative to its own page and showed no picture, so cards use the path from the site root.
    When I open the page "/"
    Then the page does not contain "media/assets/"

  Scenario: On a very wide window the cards stay the size they are on a laptop
    The Top Posts mosaic gains columns of the same width as every other grid instead of stretching three columns across the window, and the featured sections sit two across, so no card grows with the window.
    Then the stylesheet "css/site-theme.css" gives the mosaic and the featured sections more columns on a very wide window

  Scenario: A story group's section name links to the section's page, and a group of more than one story ends with More
    When I open the page "/"
    Then the home page group "Privacy & Security" links to "/security/" and ends with "More Privacy & Security…"
    And the home page group "Law & Policy" links to "/law-policy/" and ends with "More Law & Policy…"
    And the home page group "Math & Science" links to "/science/" and has no More link

  Scenario: The More links under the video and finding blocks say what they lead to
    When I open the page "/"
    Then the page contains "<a class="mom-section-link" href="/videos/">All videos</a>"
    And the page contains "<a href="/findings/">More Findings…</a>"
    And the page does not contain ">More</a>"

  @browser
  Scenario Outline: On a phone the lead headline fills its card instead of leaving the right side empty
    A long display headline wraps early on a phone because whole words are wide. The script lets the lead headline take the largest size at which it fits, so its lines fill the width and no line is a lone word.
    Given the Machines on Machines site is projected from the fixtures
    When I measure the lead headline of "/" in a browser <width> pixels wide
    Then the lead headline fills at least 70 percent of its width and leaves no lone last word

    Examples:
      | width |
      | 360   |
      | 375   |
      | 430   |

  Scenario: On a very wide window the blocks of a row start on the same line
    The featured sections sit two across with a real row gap, and none of their blocks carries a top margin of its own, so a Worth Watching panel starts level with the section beside it.
    Then the stylesheet "css/site-theme.css" gives the featured sections a row gap and no block margin on a very wide window

  Scenario: Articles get most of the page and posts are set apart as compact rows
    The home page shows up to ten sections of articles, with large cards. Posts sit in their own quieter band below, each a small square picture beside the headline and by-line, so they read as lighter than an article. The Findings grid at the bottom is short.
    When I open the page "/"
    Then the page contains "Latest Posts"
    And the page contains "class="rh-brief"
    And the page does not contain "rh-mosaic"

  Scenario: The first branding band sits halfway through the articles
    The band used to follow every article section, far down the page. It now divides the article sections into two halves, so a reader meets it early.
    When I open the page "/"
    Then the first branding band on the home page comes after half of the article sections and before the rest

  Scenario: The second branding band sits between the articles and the posts
    When I open the page "/"
    Then the home page has two branding bands, the second between the last article section and the Top Posts

  Scenario: The article sections hold only articles, and a section without articles is left out
    When I open the page "/"
    Then no article section of the home page links to a post

  Scenario: Post cards and article cards carry a date and no by-line
    A post is not written by anyone, and a card in a list no longer names an author for articles either: the by-line belongs to the article page. See story-card-date.feature.
    When I open the page "/"
    Then the Top Posts cards and the article cards show no by-line
