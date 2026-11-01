Feature: An article page fits its content
  A reading page puts the story first. The spine down the right edge must hold the section's name
  however long it is, and a story with no picture gets a slim band of brand art rather than a giant block.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The spine fits a long section name
    When I open the page "/how-to/steer-a-story/"
    Then the page contains "Newsroom How-To"
    And the spine tells the stylesheet its name is 27 characters long
    And the stylesheet "/css/site-theme.css" sizes the spine's section name to fit the room it has

  Scenario: A short page gets the top band instead of a vertical spine
    Then the stylesheet "/css/site-theme.css" collapses the spine to a band on a page shorter than 520px

  Scenario: An article with no image gets a slim band of art
    When I open the page "/papyrus/a-team-byline-and-no-picture/"
    Then the article's picture is a slim band of placeholder art

  Scenario: An article with an image keeps its wide picture
    When I open the page "/papyrus/the-agents-are-writing-the-benchmarks-now/"
    Then the article's picture is the wide image
