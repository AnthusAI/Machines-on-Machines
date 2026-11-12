Feature: A story card on an index page shows its date, not its byline
  A card in a list (the home page, a section page, the articles and posts lists, a section's article list, a tag page) is image, headline, date, blurb.
  The byline is left off: it belongs to the article page, which keeps it. The date sits between the headline and the blurb, in the design system's
  muted text colour (`ink-muted`, 14px regular), so it reads as secondary and stays readable in Day and Night.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario Outline: Index cards show no byline
    When I open the page "<route>"
    Then the page has story cards
    And no story card on the page contains a byline

    Examples:
      | route              |
      | /                  |
      | /security/         |
      | /articles/         |
      | /posts/            |
      | /field-notes/      |

  Scenario Outline: The date sits between the headline and the blurb
    When I open the page "<route>"
    Then every story card on the page puts its date between its headline and its blurb

    Examples:
      | route              |
      | /                  |
      | /security/         |
      | /articles/         |
      | /field-notes/      |

  Scenario: The date is drawn in the muted style, at or above the card text floor
    Then the date of a story card is styled with the muted text colour at 14px or more

  Scenario: An article page keeps its byline
    When I open the page "/field-notes/the-agents-are-writing-the-benchmarks-now/"
    Then the page contains "By various bots and Ada Reader"
