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

  Scenario: The side of the lead holds the site title and nothing else
    When I open the page "/"
    Then the side of the lead holds only the wordmark

  Scenario: Card groups come in sixes and split into three, two or one columns
    Then the home page asks for 6 suggested findings
    And the stylesheet "/css/site-theme.css" splits a panel of cards into three, two and one columns

  Scenario: The navigation offers stories, posts and findings
    When I open the page "/"
    Then the page contains ">Posts</a>"
    And the page contains ">Findings</a>"
    And the page contains ">Concepts</a>"
    And the page does not contain "Reading list"

  Scenario: The lead's blurb fills the column under the site title card
    Then the stylesheet "/css/site-theme.css" sets the lead's blurb in the right column beside its headline

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

