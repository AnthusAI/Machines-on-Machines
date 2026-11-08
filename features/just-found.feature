Feature: Just Found lists what our monitors brought back and no editor has accepted yet
  The Videos page and the Findings page list accepted References only. The References Cyclotron expects an editor to accept, which we have not written
  about, are on their own page, `/just-found/`: every one of them, highest confidence first, loading as the reader scrolls, with a Load more control and data
  files beside it. The home page's Just Found grid links there with "More Just Found…". Neither Videos nor Findings carries a pending panel.

  Scenario: The page lists only pending References, highest confidence first, and loads the rest
    Given the "none" Reference case is projected
    When I open the case page "/just-found/"
    Then the Just Found page shows only pending References, the most confident first
    And the Just Found page shows 59 cards, has a Load more control and data files under "reference-lists/just-found/recommended/" that reach all 80
    And the page has no heading other than its title

  Scenario: The home page's Just Found grid leads to the page
    When I open the page "/"
    Then the page contains "<a href="/just-found/">More Just Found…</a>"

  Scenario Outline: Videos and Findings have no panel of pending References
    When I open the page "<route>"
    Then the page does not contain "Found by machines"
    And the page does not contain "Not accepted yet"

    Examples:
      | route      |
      | /videos/   |
      | /findings/ |

  Scenario: The old Wire address has no redirect
    Then the projection has no redirect from "/wire/"
