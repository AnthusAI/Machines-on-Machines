Feature: The home page puts stories first and weaves the newsroom in
  A first-time reader should see journalism before tables. The home page leads with a story,
  then shows a few sources, and conversations as samples of the newsroom's public parts.
  Each slot is a stock Papyrus include drawn with the design system's cards.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The slots appear in the order the design recipe gives
    When I open the page "/"
    Then "mom-story-card-lead" comes before "mom-sticker"
    And "mom-sticker" comes before "mom-band-brand"
    And "mom-band-brand" comes before "Accepted findings"
    And "Accepted findings" comes before "Talking now"

  Scenario: Accepted and suggested findings are separate blocks
    When I open the page "/"
    Then the page shows 4 reference cards under "mom-accepted-findings"
    And the page shows 3 reference cards under "mom-suggested-findings"
    And the page contains "Recommended by Cyclotron, not yet accepted"
    And the page contains "91% confidence"
    And the page does not contain "Recent findings"
    And the page does not contain "Up for consideration"
  Scenario: Talking now shows the two most recently active conversations
    When I open the page "/"
    Then the page shows 2 thread cards under "mom-talking-now"
    And the page contains "Is a judge that shares training data still a judge?"

  Scenario: Proposals are not on the public site
    When I open the page "/"
    Then the page does not contain "Proposals"
    And the page does not contain "Placeholder proposal"

  Scenario: A band separates the blocks
    When I open the page "/"
    Then "mom-accepted-findings" comes before "mom-suggested-findings"
    And the home page has 2 bands

  Scenario: The whole wire lists every accepted and recommended source
    When I open the page "/wire/"
    Then the page contains "Accepted automatically"
    And the page contains "Accepted by an editor"
    And the page contains "Not accepted yet"

  Scenario: The side of the lead holds no story cards
    When I open the page "/"
    Then the side of the lead has no story cards

  Scenario: Card groups show six, more on a wide display, and split into three, two or one columns
    Then the home page asks for 12 suggested findings
    And the stylesheet "/css/site-theme.css" splits a panel of cards into three, two and one columns

  Scenario: The navigation offers stories, posts and findings
    When I open the page "/"
    Then the page contains ">Posts</a>"
    And the page contains ">Findings</a>"
    And the page contains ">Concepts</a>"
    And the page does not contain "Reading list"

  Scenario: The lead's blurb stays with its headline, and the rail lists posts that fit
    Then the home page lists the latest posts in the side column
    And a post in the rail shows its title and date

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

  Scenario: Stories has its own page, broken apart into sections
    When I open the page "/stories/"
    Then the page contains "mom-section-title"
    And the page contains "Field Notes"
    And the navigation links Stories to "/stories/"

  Scenario: The section with the most recent update comes first
    Then sections with newer updates come first on the Stories page

  Scenario: An accepted reference shows its star rating, and a suggested one does not
    Then an accepted card rated 4 shows "4 of 5 stars"
    And an accepted card with no rating shows no stars
    And a suggested card shows no stars
    And the card reads the rating from the stock tile's data-stars

