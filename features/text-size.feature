Feature: No text on the site is too small to read
  The site is operated by an editor in his fifties who has trouble reading tiny text, especially on a phone. The minimum is a
  policy about rendered sizes, the size a reader actually sees after the 75% scale: reading text (article, wiki and post bodies
  and other long paragraphs) is at least 18 pixels, interface and card text (dek, blurb, meta lines, chips, navigation, captions,
  form labels) at least 14 pixels, and nothing anywhere, uppercase micro-labels included, below 13 pixels. The scale tool owns the
  numbers and raises any size in the stylesheets that would fall below its floor, on phones as well as wider screens, so no future
  stylesheet can break the policy.

  Scenario: The scale tool states the three floors
    Then the scale tool's floors are 18 pixels for reading text, 14 for interface text and 13 for micro-labels

  Scenario: No size in a published stylesheet is below the smallest floor
    Given the Machines on Machines site is projected from the fixtures
    Then no font size in "css/site-theme.css" and "assets/mom-components.css" is below 13 pixels in either version

  @browser
  Scenario Outline: Every visible piece of text on a page is drawn at or above its floor
    Given the Machines on Machines site is projected from the fixtures
    When I check the text sizes of "<route>" in a browser <width> pixels wide
    Then no visible text is drawn below its floor

    Examples:
      | route                                                | width |
      | /                                                    | 375   |
      | /                                                    | 820   |
      | /                                                    | 1440  |
      | /articles/                                           | 375   |
      | /posts/                                              | 820   |
      | /field-notes/                                        | 375   |
      | /field-notes/                                        | 820   |
      | /field-notes/the-agents-are-writing-the-benchmarks-now/ | 375   |
      | /field-notes/the-agents-are-writing-the-benchmarks-now/ | 820   |
      | /field-notes/the-agents-are-writing-the-benchmarks-now/ | 1440  |
      | /wiki/                                               | 375   |
      | /wiki/durable-execution/                             | 375   |
      | /wiki/durable-execution/                             | 820   |
      | /wiki/durable-execution/                             | 1440  |
      | /findings/                                               | 375   |
      | /findings/                                               | 820   |
      | /videos/                                             | 1440  |
      | /conversations/                                      | 820   |
      | /conversations/b1c2d3e4f501/                         | 375   |
      | /conversations/b1c2d3e4f501/                         | 1440  |
      | /about/                                              | 375   |

  Scenario: Article, post and wiki body text is 18 pixels on every screen, on the rhythm, in a column of about 65 characters
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheet "css/site-theme.css" sets the article body to 18 pixels on a line of 28 pixels below 600 pixels and 18 pixels on a line of 30 pixels from 600 pixels up
    And the stylesheet "assets/mom-tokens.css" sets the text measure to 840 pixels below 600 pixels and 630 pixels from 600 pixels up

  Scenario: An article keeps a comfortable gutter on a phone
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheet "css/site-theme.css" gives the article a 16 pixel side gutter below 600 pixels

  Scenario: The mentions chart on a wiki page does not clip its caption into the next heading
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheet "css/site-theme.css" sets no maximum height on the knowledge chart figure
