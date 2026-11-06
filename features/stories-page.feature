Feature: The Stories page shows every story, grouped by section
  Stories is the whole library of what Machines on Machines has published. Every story is on it, whether it is an article or a post,
  and nothing else is: no findings, no videos, no conversations, no wiki pages. Stories are grouped by section, and the section
  that was updated most recently comes first. The sections near the top make more of their first story, the way the home page does,
  and the sections further down thin out into plain grids. No section is left off, and every row is full at any width.

  Background:
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/stories/"

  Scenario: Articles and posts are both stories
    Then the page contains "Synthetic Security article 1"
    And the page contains "Synthetic Security post 2"
    And the page contains "Synthetic Law Policy post 2"

  Scenario: Findings and videos never appear on the Stories page
    Then the page does not contain "mom-reference-card"
    And the page does not contain "Fixture video number 1: talks on machines"
    And the page does not contain "mom-thread-card"
    And the page does not contain "mom-wiki-card"

  Scenario: The section updated most recently comes first
    Then the Stories page lists its sections in this order
      | section            |
      | Privacy & Security |
      | Law & Policy       |
      | Science            |
      | Field Notes        |

  Scenario: Stories within a section are newest first
    Then in the section "Privacy & Security" "Synthetic Security article 1" comes before "Synthetic Security post 2"
    And in the section "Privacy & Security" "Synthetic Security post 2" comes before "Synthetic Security article 3"

  Scenario: Only the first three sections have a featured story
    Then the section "Privacy & Security" has the "feature" layout
    And the section "Law & Policy" has the "wide" layout
    And the section "Science" has the "wide" layout
    And the section "Field Notes" has the "plain" layout

  Scenario: The first section features its newest story beside its picture
    Then the section "Privacy & Security" has one feature card drawn beside its picture
    And the section "Law & Policy" has one card across two columns

  Scenario: Later sections are plain grids with no featured card
    Then the section "Field Notes" has no featured card and no card across two columns

  Scenario: No section is hidden, and a section with more stories than shown says how many it has
    Then the Stories page has 4 sections
    And the section "Privacy & Security" says it has "8 stories"
    And the section "Field Notes" says it has "11 stories"
    And the section "Science" does not say how many stories it has

  Scenario: A link to more is offered only where the section has a page
    Then the section "Field Notes" links to "/field-notes/"
    And the section "Privacy & Security" has no link to a section page

  Scenario: Every row of a section is full
    Then every row on the Stories page is a whole row of one, two or three cards
