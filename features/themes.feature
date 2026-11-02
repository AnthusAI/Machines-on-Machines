Feature: Day and Night are designed together
  By day every colored fill is bright with dark text. By night the fills become deep tints with
  light text. The site ships both from one set of tokens and follows the reader's system setting,
  with an explicit data-theme override for previews and screenshots.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The token stylesheet carries both themes
    Then the stylesheet "assets/mom-tokens.css" defines Day colors and Night colors
    And the stylesheet "assets/mom-tokens.css" gives "paper" a different value by night than by day
    And the stylesheet "assets/mom-tokens.css" gives "machine" a different value by night than by day

  Scenario: Every page links the tokens before the components
    When I open the page "/"
    Then "/assets/mom-tokens.css" comes before "/assets/mom-components.css"
    And "/assets/mom-components.css" comes before "/css/site-theme.css"

  Scenario: The browser chrome follows the theme
    When I open the page "/"
    Then the page contains "theme-color"
    And the page contains "prefers-color-scheme: dark"

  Scenario: The palette stays neutral, like a newspaper
    Then every color in the stylesheet "assets/mom-tokens.css" except the focus ring is close to gray or ink blue
