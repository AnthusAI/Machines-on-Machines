Feature: The site renders at three quarters of its designed size on screens 600 pixels wide and up
  The owner previewed the whole site at 75% on his own devices and chose to keep it. On a viewport 600 pixels wide or wider, every size on the
  site is three quarters of what the design system specifies: type, spacing, widths, and the window widths at which the layout changes columns.
  A phone, a viewport narrower than 600 pixels, keeps the designed sizes unchanged. Each published stylesheet carries both versions in one file,
  generated from its source, so the scale can be changed in a single place.

  Scenario: Every published stylesheet holds a phone version and a scaled version
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheet "assets/mom-tokens.css" applies its designed sizes below 600 pixels and its sizes at 75% from 600 pixels up
    And the stylesheet "assets/mom-components.css" applies its designed sizes below 600 pixels and its sizes at 75% from 600 pixels up
    And the stylesheet "css/site-theme.css" applies its designed sizes below 600 pixels and its sizes at 75% from 600 pixels up

  Scenario: The page text is 17 pixels on a phone and 12.75 pixels on a wider screen
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheet "css/site-theme.css" sets the page text to 17 pixels below 600 pixels and 12.75 pixels from 600 pixels up

  Scenario: The window widths where the layout changes are scaled with everything else
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheet "css/site-theme.css" opens its wide layout at 900 pixels in the phone version and at 675 pixels in the scaled version

  Scenario: Only lengths are scaled
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheet "css/site-theme.css" keeps its line height of 1.5 in both versions

  Scenario: Sizes written in rem follow the scale through the root font size
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheet "css/site-theme.css" sets the root font size to 75% from 600 pixels up and not below
