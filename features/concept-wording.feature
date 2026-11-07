Feature: The site says "concept", never "topic", for a concept page
  In our knowledge graph a concept is an entity node. "Topic" means topic analysis, which is related but different, so a concept page is never
  labelled a topic, whatever its kind says in the data.

  Scenario: The concepts index labels every card a concept
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/wiki/"
    Then the page does not contain "Concept</span>"
    And the page does not contain "Topic</span>"

  Scenario: A concept card says how many associations it has, not what type it is
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/wiki/"
    Then the page contains "3 associations</span>"
    And the page contains "data-associations="
    And the page does not contain "mom-wiki-card-relation"

  Scenario: The connected terms of a concept carry no type label
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/wiki/durable-execution/"
    Then the page contains "papyrus-knowledge-chip-name"
    And the page does not contain "papyrus-knowledge-chip-kind"
    And the page does not contain "Topic</span>"

  Scenario: The concepts index lists the most connected concept first
    When I open the page "/wiki/"
    Then the concept cards appear in this order
      | concept           |
      | Agent evals       |
      | Durable execution |
      | Benchmarks        |

  Scenario: The site card holds one row of the concepts grid, not several
    Given the site's stylesheet source
    Then the concepts grid reserves the site card's column by height in proportion to the column
    And it does not reserve a fixed number of rows

  Scenario: An article headline fills its width
    Given the site's stylesheet source
    Then the article headline fills its width and does not balance its lines
