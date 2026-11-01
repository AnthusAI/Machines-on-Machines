Feature: Cards without an image draw brand art
  Every card has an image. When a story, a source or a thread has none, the card draws flat brand
  shapes chosen from its address, so the same item looks the same on every page and every visit.
  The Python site and the design system's JavaScript must choose the same art.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: No card on the home page is a gray box
    When I open the page "/"
    Then every card on the page has an image or placeholder art

  Scenario: Research papers draw the pages composition
    When I open the page "/wire/"
    Then the reference card for "https://arxiv.org/abs/0000.10001" is drawn with the "pages" placeholder art
    And the reference card for "https://reports.fixture.example/open-evals.pdf" is drawn with the "pages" placeholder art

  Scenario: The seed fixes the art
    Then the same address always draws the same art
    And the seed "seed-one" chooses the "horizon" composition in the "brand" tone
