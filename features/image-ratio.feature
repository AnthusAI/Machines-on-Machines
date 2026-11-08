Feature: Every content image has one shape, and its height sits on the vertical rhythm
  The images used to have several shapes: 4:3 on the home page's story cards, 16:9 on the lead story and the reference cards, 4:3 again on a
  conversation's picture, and a lone card's picture that followed the height of the text beside it. The design system now has one shape for a
  content image, 16:9, defined once as a token, and one vertical rhythm unit, 4px on a phone and 3px from 600px up (the 75% scale). The only other
  shape is a small square thumbnail. An image's height is its width at 16:9, rounded down to a whole number of rhythm units, so the text under it
  starts on the grid at every card width. A card never stretches its image to fill a grid row; the text may leave space instead.

  Scenario: The shape and the rhythm are each defined once, as tokens
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheet "assets/mom-tokens.css" defines "ratio-media" as 16 over 9 and "rhythm" as 4 pixels below 600 pixels and 3 pixels from 600 pixels up
    And the stylesheet "assets/mom-tokens.css" defines "ratio-square" as 1

  Scenario: No component writes its own aspect ratio
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheets "assets/mom-components.css" and "css/site-theme.css" write no aspect ratio except the media tokens, the square thumbnail and the decorative strip
    And the stylesheets define no "mom-ratio-photo" or "mom-ratio-wide" class

  Scenario: The home page marks no image with a ratio class and gives each one a frame
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/"
    Then the page does not contain "mom-ratio-"
    And every image on the page sits in a "mom-media" frame

  Scenario: An image falls back to 16:9 where the browser cannot snap it
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheet "assets/mom-components.css" snaps image heights only inside a feature test for rounding and container units
    And the stylesheet "assets/mom-components.css" keeps the 16:9 aspect ratio outside that test

  @browser
  Scenario Outline: Every content image on the home page has the one ratio
    Given the Machines on Machines site is projected from the fixtures
    When I view the page "/" in a browser <width> pixels wide
    Then every content image is 16:9 to within one rhythm unit of height

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |

  @browser
  Scenario Outline: No card stretches its image
    Given the Machines on Machines site is projected from the fixtures
    When I view the page "/" in a browser <width> pixels wide
    Then every content image is exactly as tall as its own width gives
    And every content image fills its frame

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |

  @browser
  Scenario Outline: No image on a section page is stretched
    Given the Machines on Machines site is projected from the fixtures
    When I view the page "/security/" in a browser <width> pixels wide
    Then every content image is exactly as tall as its own width gives
    And every content image fills its frame

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |
      | 2200  |

  @browser
  Scenario Outline: The height of every image is a whole number of rhythm units
    Given the Machines on Machines site is projected from the fixtures
    When I view the page "<route>" in a browser <width> pixels wide
    Then every content image has a height that is a whole number of rhythm units
    And the rhythm unit is <unit> pixels

    Examples:
      | route          | width | unit |
      | /              | 375   | 4    |
      | /              | 820   | 3    |
      | /              | 1440  | 3    |
      | /field-notes/  | 375   | 4    |
      | /field-notes/  | 820   | 3    |
      | /security/     | 375   | 4    |
      | /security/     | 820   | 3    |
      | /security/     | 1440  | 3    |
      | /videos/       | 375   | 4    |
      | /videos/       | 1440  | 3    |
