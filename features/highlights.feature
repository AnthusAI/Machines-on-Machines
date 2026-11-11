Feature: An editor can highlight the phrase a skimming reader should keep
  A reader who skims should still leave with the claim. An editor wraps the phrase in two equals signs and the site draws it as a
  rounded fill in the warm gray that means "chosen by people". The look never relies on colour: the text is heavier, which also
  holds when the fill is dropped by print or forced colors. There is no border, outline or underline, which the house rules forbid.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: Equals signs around a phrase become a mark, and nest with a link and emphasis
    When I open the page "/field-notes/a-highlight-helps-a-reader-skim/"
    Then the page contains "<mark>Employees and customers will be the ones it sees on its rounds"
    And the highlight that holds a link and emphasis keeps both inside the mark

  Scenario: The stylesheet draws a highlight as a flat rounded fill with heavier text
    Then the stylesheet "css/site-theme.css" draws a highlight as a flat rounded fill with heavier text and no outline

  Scenario: A highlight has fallbacks for forced colors and print
    Then the stylesheet "css/site-theme.css" gives a highlight a forced-colors fallback and a print fallback that keep the emphasis

  Scenario: A highlight uses a design-system pair that meets the contrast standard
    Then the highlight's text color on its fill reaches 4.5 to 1 in Day and in Night

  @browser
  Scenario Outline: A highlight is readable, flat and cued without colour on every line it wraps across
    When I measure highlights at <width> pixels in "<theme>" mode
    Then every highlight is a rounded fill with no border or outline, heavier than body text, repeated on each wrapped line
    And every highlight's text, and the link inside one, reaches 4.5 to 1 against its fill

    Examples:
      | width | theme |
      | 1440  | light |
      | 1440  | dark  |
      | 375   | light |
      | 375   | dark  |
