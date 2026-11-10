Feature: Readers can compare two attributed statements

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: An article renders two quotations and preserves their attribution
    When I open the page "/field-notes/the-agents-are-writing-the-benchmarks-now/"
    Then the page contains "markus-two-up"
    And the page contains "markus-pull-quote--quiet"
    And "Product announcement" comes before "Technical disclosure"

  @browser
  Scenario Outline: The quotes fit the reading column at different screen widths
    When I measure paired quotes at <width> pixels in "<theme>" mode
    Then the attributed quotes are <arrangement> in readable type

    Examples:
      | width | theme | arrangement |
      | 375   | light | stacked     |
      | 375   | dark  | stacked     |
      | 1280  | light | side by side |
      | 1280  | dark  | side by side |
