Feature: The home page puts stories first and weaves the newsroom in
  A first-time reader should see journalism before tables. The home page leads with a story,
  then shows a few sources, and conversations as samples of the newsroom's public parts.
  Each slot is a stock Papyrus include drawn with the design system's cards.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The slots appear in the order the design recipe gives
    When I open the page "/"
    Then "mom-story-card-lead" comes before "mom-sticker"
    And "mom-sticker" comes before "Recent findings"
    And "Recent findings" comes before "Talking now"
    And "Talking now" comes before "mom-band-brand"

  Scenario: Recent findings lists accepted sources and Up for consideration shows three
    When I open the page "/"
    Then the page shows 4 reference cards under "mom-recent-findings"
    And the page shows 3 reference cards under "mom-up-for-consideration"
    And the page contains "Recommended by Cyclotron, not yet accepted"
    And the page contains "91% confidence"

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
    Then "Up for consideration" comes before "mom-band-brand"

  Scenario: The whole wire lists every accepted and recommended source
    When I open the page "/wire/"
    Then the page contains "Accepted automatically"
    And the page contains "Accepted by an editor"
    And the page contains "Up for consideration"

  Scenario: The side of the lead holds the site title and a short reading list, not more stories
    When I open the page "/"
    Then the side of the lead has the wordmark and "Recent findings"
    And the side of the lead has no story cards

  Scenario: Card groups come in sixes and split into three, two or one columns
    Then the home page asks for 6 sources up for consideration
    And the stylesheet "/css/site-theme.css" splits a panel of cards into three, two and one columns

