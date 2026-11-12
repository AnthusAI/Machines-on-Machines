Feature: Every page has a link preview picture
  When someone shares a link to any page, chat apps and social sites show a picture. Articles
  use their own picture. Every other page, the home page and the index pages included, uses
  one default picture: the Machines on Machines wordmark on navy, 1200 by 630 pixels.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The home page has a link preview picture
    When I open the page "/"
    Then the page names the default link preview picture in its Open Graph and Twitter tags
    And the page asks for a large Twitter card

  Scenario: An index page has a link preview picture
    When I open the page "/findings/"
    Then the page names the default link preview picture in its Open Graph and Twitter tags

  Scenario: The default picture is published
    Then the default link preview picture is published as a 1200 by 630 picture
