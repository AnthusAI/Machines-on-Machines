Feature: The site says "concept", never "topic", for a concept page
  In our knowledge graph a concept is an entity node. "Topic" means topic analysis, which is related but different, so a concept page is never
  labelled a topic, whatever its kind says in the data.

  Scenario: The concepts index labels every card a concept
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/wiki/"
    Then the page contains "Concept</span>"
    And the page does not contain "Topic</span>"
