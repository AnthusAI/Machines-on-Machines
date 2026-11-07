Feature: The page does not slide sideways on a touch screen
  A reader scrolling with a finger rarely moves straight up and down. A slightly diagonal swipe must move the page up and down and nothing else, on
  every page, with no sideways bounce at either edge. The site sets this on the page itself rather than by restricting touch, so the reader can still
  pinch to zoom and can still swipe the navigation row, which is the one thing on the page that scrolls sideways.

  Scenario: The page stops sideways scrolling and bouncing without restricting touch
    Given the site's stylesheet
    Then the rule for "html, body.mom" sets "overflow-x" to "clip"
    And the rule for "html, body.mom" sets "overscroll-behavior-x" to "none"
    And the stylesheet does not set "touch-action"

  Scenario: The navigation row no longer scrolls sideways
    Given the site's stylesheet
    Then the rule for ".mom-nav" does not set "overflow-x"
