Feature: The top navigation turns into a menu when it runs out of room
  A phone cannot hold seven pills in a row, and a row that scrolls sideways hides what is in it. So the bar shows only the destinations that fit after
  the Machines on Machines logo and buries the rest behind a menu button. On a phone that means the logo and the button and nothing else. The button opens
  a menu that covers the whole page under the bar and lists every destination with a line about what it is, taken from the site's own data. The bar does
  its sorting in the browser; without JavaScript the same destinations show as a wrapped row, so every page stays reachable.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: Every page carries the menu button, the menu and a wrapped row of destinations
    When I open the page "/articles/"
    Then the navigation has a button named "Menu" that controls the menu and starts collapsed
    And the menu is hidden until it is opened
    And the navigation row lists "Home, Articles, Posts, Findings, Videos, Conversations, Concepts"
    And the page loads a script that marks it as having JavaScript before it is first drawn

  Scenario: The menu lists every destination with a subtitle from the site's data
    When I open the page "/articles/"
    Then the menu lists "Home, Articles, Posts, Findings, Videos, Conversations, Concepts" in that order
    And every destination in the menu has a subtitle
    And the subtitle of "Articles" is the Articles page lead
    And the subtitle of "Posts" is the Posts page lead
    And the subtitle of "Concepts" is the description of the Concepts section in the projection
    And the subtitle of "Videos" is the description of the Videos page in the projection

  Scenario: The current page is marked in words as well as colour
    When I open the page "/videos/"
    Then the menu marks "Videos" as the current page with "You are here"
    And the menu marks no other destination as the current page

  Scenario: The home page marks Home
    When I open the page "/"
    Then the menu marks "Home" as the current page with "You are here"

  Scenario: The menu icons are Lucide icons
    When I open the page "/"
    Then the menu button holds the Lucide "menu" icon and the Lucide "x" icon

  Scenario: The menu type is large enough to read
    Given the site's stylesheet
    Then the menu names are set at 24 pixels and the subtitles at 19 pixels, which are 18 and 14.25 pixels once the 75 percent scale applies
    And the menu destinations are at least 72 pixels tall

  Scenario: The bar no longer scrolls sideways
    Given the site's stylesheet
    Then the rule for ".mom-nav" does not set "overflow-x"

  @browser
  Scenario Outline: A phone shows only the wordmark and a menu button
    When I view the navigation on "/videos/" in a browser <width> pixels wide
    Then the bar shows the wordmark and the menu button and no destinations
    And the page does not scroll sideways

    Examples:
      | width |
      | 375   |
      | 599   |

  @browser
  Scenario: A tablet in portrait shows some destinations and buries the rest
    When I view the navigation on "/videos/" in a browser 700 pixels wide
    Then the bar shows some destinations in order and the menu button
    And every destination the bar does not show is in the menu
    And the page does not scroll sideways

  @browser
  Scenario Outline: A wide screen shows every destination and no menu button
    When I view the navigation on "/videos/" in a browser <width> pixels wide
    Then the bar shows every destination and no menu button

    Examples:
      | width |
      | 1024  |
      | 1440  |

  @browser
  Scenario: The menu covers the page under the bar and locks the page
    When I view the navigation on "/videos/" in a browser 375 pixels wide
    Then the menu opens from the bottom of the bar to the bottom of the screen
    And the page behind it cannot scroll
    And the menu button is expanded and shows the close icon
    And every destination in the open menu is at least 48 pixels tall
    And the open menu's names are at least 18 pixels and its subtitles at least 14 pixels

  @browser
  Scenario: Escape closes the menu and gives focus back to the button
    When I view the navigation on "/videos/" in a browser 375 pixels wide
    Then Escape closes the menu and focus returns to the menu button

  @browser
  Scenario: Choosing a destination closes the menu
    When I view the navigation on "/videos/" in a browser 375 pixels wide
    Then choosing a destination closes the menu and focus returns to the menu button

  @browser
  Scenario: Keyboard focus stays inside the open menu
    When I view the navigation on "/videos/" in a browser 375 pixels wide
    Then Tab and Shift+Tab keep focus on the menu button and the menu's links

  @browser
  Scenario Outline: Without JavaScript every destination is still reachable
    When I view the navigation on "/videos/" in a browser <width> pixels wide without JavaScript
    Then the bar shows every destination and no menu button
    And the page does not scroll sideways

    Examples:
      | width |
      | 375   |
      | 820   |
