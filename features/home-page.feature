Feature: The home page puts stories first and weaves the newsroom in
  A first-time reader should see journalism before tables. The home page leads with a story,
  then shows a few sources, and conversations as samples of the newsroom's public parts.
  Each slot is a stock Papyrus include drawn with the design system's cards.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The slots appear in the order the design recipe gives
    When I open the page "/"
    Then "mom-story-card-lead" comes before "mom-sticker"
    And "mom-sticker" comes before "mom-latest-posts"
    And "mom-latest-posts" comes before "Just Found"
    And "Just Found" comes before "How It Works"

  Scenario: Just Found leads with the How It Works card and shows each finding once
    When I open the page "/"
    Then the page contains "How It Works"
    And the page contains "Recommended by Cyclotron, not yet accepted"
    And the page contains "Very likely to be accepted"
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
    Then "mom-story-card-lead" comes before "mom-latest-posts"
    And "mom-latest-posts" comes before "Just Found"
    And the home page has 2 bands

  Scenario: The whole wire lists every accepted and recommended source
    When I open the page "/wire/"
    Then the page contains "Accepted automatically"
    And the page contains "Accepted by an editor"
    And the page contains "Found by machines"

  Scenario: The side of the lead holds no story cards
    When I open the page "/"
    Then the side of the lead has no story cards

  Scenario: Card groups split into three, two or one columns
    Then the home page asks for 16 suggested findings
    And the stylesheet "/css/site-theme.css" splits a panel of cards into three, two and one columns

  Scenario: The navigation offers articles, posts and findings
    When I open the page "/"
    Then the page contains ">Posts</a>"
    And the page contains ">Findings</a>"
    And the page contains ">Concepts</a>"
    And the page does not contain "Reading list"

  Scenario: The lead's blurb stays with its headline, and the rail lists posts that fit
    Then the home page lists the latest posts in the side column
    And a post in the rail shows its title, byline and date

  Scenario: The footer says who publishes the site and offers the standard links
    When I open the page "/"
    Then the page contains ">About</a>"
    And the page contains ">Corrections</a>"
    And the page contains "https://anth.us/privacy/"
    And the page contains "#cookie-settings"
    And the page contains "Built with <a href="https://p.apyr.us">Papyrus</a>"

  Scenario: The site counts visits in the Anthus analytics property, with the consent banner
    Then the site's analytics property is "G-31SC26SDGX" with consent mode on

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
    Then the page contains "Fixture talk: the cost of an evaluation run"
    And the videos page shows no References of another medium
    And the page contains "mom-wire"
    And the stylesheet "/css/site-theme.css" hides an empty not-accepted panel and keeps the card from covering the page when no accepted videos reserve room for it

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
    And "mom-home-purpose" comes before "mom-home-rail"
    And the page contains "Information About Information Systems"

  Scenario: The two home page bands each carry one phrase
    When I open the page "/"
    Then the first home page band repeats "Machines on Machines"
    And the second home page band repeats "Machines on Machines"

  Scenario: The nav and home page lead with the journalism
    When I open the page "/"
    Then the nav marks Findings, Videos, Conversations and Concepts as the newsroom group, and not Articles or Posts
    And the stylesheet "/css/site-theme.css" styles every nav pill the same
    And the stylesheet "/css/site-theme.css" shows every item of the home page lists and lays out the Latest Posts mosaic

  Scenario: The Concepts page says it is a page per concept
    When I open the page "/wiki/"
    Then the page contains "Every concept our knowledge base tracks gets a page here"

  Scenario: The Articles page has the same page header as the other pages
    When I open the page "/articles/"
    Then "mom-page-top" comes before "mom-section-title"
    And the page contains "Every article from Machines on Machines, by section."
    And the page does not contain "mom-grid-sticker"

  Scenario: Conversations and Videos have short subtitles
    When I open the page "/conversations/"
    Then the page contains "The forum. Editors and AI discuss our stories and sources."
    When I open the page "/videos/"
    Then the page contains "Videos we think are worth watching."

  Scenario: Findings has no Accepted heading and calls the suggested ones found by machines
    When I open the page "/wire/"
    Then the page does not contain ">Accepted</h2>"
    And the page contains ">Found by machines</h2>"
    And the page does not contain "Not accepted yet"

  Scenario: The sentence, the Latest posts heading and the post titles share one left edge
    Then the stylesheet "/css/site-theme.css" lines up the home sentence and the Latest posts heading with the post titles

  Scenario: Accepted findings and videos rank by stars within each week
    Then the page "/web/pages/wire.md" lists accepted findings by week, highest rated first
    And the page "/web/pages/videos.md" lists accepted findings by week, highest rated first
