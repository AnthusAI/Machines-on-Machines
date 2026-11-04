Feature: The home page puts stories first and weaves the newsroom in
  A first-time reader should see journalism before tables. The home page leads with a story,
  then shows a few sources, and conversations as samples of the newsroom's public parts.
  Each slot is a stock Papyrus include drawn with the design system's cards.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The slots appear in the order the design recipe gives
    When I open the page "/"
    Then "mom-story-card-lead" comes before "mom-sticker"
    And "mom-sticker" comes before "Talking now"
    And "Talking now" comes before "mom-band-brand"

  Scenario: Findings is the one list of sources on the home page
    When I open the page "/"
    Then the page shows 3 reference cards under "mom-findings"
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

  Scenario: The band stays below everything but the footer
    When I open the page "/"
    Then "mom-findings" comes before "mom-band-brand"

  Scenario: The whole wire lists every accepted and recommended source
    When I open the page "/wire/"
    Then the page contains "Accepted automatically"
    And the page contains "Accepted by an editor"
    And the page contains "Not accepted yet"

  Scenario: The side of the lead holds the site title and nothing else
    When I open the page "/"
    Then the side of the lead holds only the wordmark

  Scenario: Card groups come in sixes and split into three, two or one columns
    Then the home page asks for 6 findings
    And the stylesheet "/css/site-theme.css" splits a panel of cards into three, two and one columns

  Scenario: The navigation offers stories, posts and findings
    When I open the page "/"
    Then the page contains ">Posts</a>"
    And the page contains ">Findings</a>"
    And the page does not contain "Reading list"

