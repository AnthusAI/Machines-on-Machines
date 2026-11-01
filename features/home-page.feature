Feature: The home page puts stories first and weaves the newsroom in
  A first-time reader should see journalism before tables. The home page leads with a story,
  then shows a few sources, conversations and proposals as samples of the newsroom's public parts.
  Each slot is a stock Papyrus include drawn with the design system's cards.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The slots appear in the order the design recipe gives
    When I open the page "/"
    Then "mom-story-card-lead" comes before "mom-sticker"
    And "mom-sticker" comes before "Just accepted"
    And "Just accepted" comes before "Talking now"
    And "Talking now" comes before "mom-band-brand"
    And "mom-band-brand" comes before "Cyclotron recommends"
    And "Cyclotron recommends" comes before "mom-proposals"

  Scenario: Just accepted shows three accepted sources and Cyclotron recommends shows three more
    When I open the page "/"
    Then the page shows 3 reference cards under "mom-just-accepted"
    And the page shows 3 reference cards under "mom-recommends"
    And the page contains "Recommended by Cyclotron, not yet accepted"
    And the page contains "91% confidence"

  Scenario: Talking now shows the two most recently active conversations
    When I open the page "/"
    Then the page shows 2 thread cards under "mom-talking-now"
    And the page contains "Is a judge that shares training data still a judge?"

  Scenario: The proposals slot says it is a placeholder until the feed is on
    When I open the page "/"
    Then the page contains "Placeholder"
    And the page contains "Proposed by AI"

  Scenario: The whole wire lists every accepted and recommended source
    When I open the page "/wire/"
    Then the page contains "Accepted automatically"
    And the page contains "Accepted by an editor"
    And the page contains "Recommended, not yet accepted"
