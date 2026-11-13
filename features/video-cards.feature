Feature: A video card loads no player until the reader presses Play, and a section's videos are an ordinary grid that never scrolls sideways
  The Videos page is the most visited page, and it holds sixty or more videos at a time, so it must not load sixty players. Every video card the site can play
  (YouTube and Vimeo) shows a picture with a Play button: the Reference's image, or the site's placeholder art. The page loads no player and makes no request
  to a video platform. Pressing the button, or Enter or Space on it, swaps the platform's own player into the picture's place and starts it, and moves the
  keyboard focus into the player so it is not lost. Only one plays at a time: starting another puts the first back to its picture. The card keeps its size,
  so nothing around it moves. The same card is used on the home page (Worth Watching and Videos) and on every list of videos.

  On the Videos page the videos filed under a section are an ordinary wrapping grid of cards, the same grid the rest of the site uses: at most two whole rows of
  three, then "More <section> videos…" under it. No element on the page scrolls sideways (no row, no scroll buttons), and neither does the page, at 375, 820, 1440
  and 2560 pixels wide. The browser scenarios run when Playwright is installed:
  `PLAYWRIGHT_MODULE=<path to playwright> behave features/video-cards.feature --tags=@browser`

  Scenario: The Videos page draws every video as a picture with a Play button and loads no player
    Given the "some" Reference case is projected
    When I open the case page "/videos/"
    Then the page has Play buttons and no player frame
    And every Play button is named "Play: " followed by its video's title

  Scenario: The home page draws its videos the same way
    Given the "some" Reference case is projected
    When I open the case page "/"
    Then the page has Play buttons and no player frame

  Scenario: A section's list of videos draws its videos the same way
    Given the "some" Reference case is projected
    When I open the case page "/security/videos/"
    Then the page has Play buttons and no player frame

  Scenario: The site's script swaps the player in and keeps one player at a time
    Then the site script replaces a pressed Play button with an iframe taken from the button's data and puts back the one that was playing

  Scenario: A section's videos have no sideways-scrolling rule or scroll buttons anywhere in the stylesheet and the script
    Given the "some" Reference case is projected
    When I open the case page "/videos/"
    Then the stylesheet "/css/site-theme.css" and the site script have nothing that scrolls a row of videos sideways
    And a section's block of videos is at most two rows of the card grid, with no scroll buttons

  @browser
  Scenario Outline: No player loads with the page, and no element scrolls sideways
    Given the "some" Reference case is projected
    When I press nothing on "/videos/" in a browser <width> pixels wide
    Then the page loaded no player and made no request to a video platform
    And the page does not scroll sideways at load
    And no element on the page scrolls sideways, in light and in dark
    And each section's videos are a wrapping grid of at most two rows, and the page has no scroll buttons

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |
      | 2560  |

  @browser
  Scenario Outline: Pressing Play swaps the player into the card without moving anything, and a second video stops the first
    Given the "some" Reference case is projected
    When I press Play on three videos of "/videos/" in a browser <width> pixels wide
    Then the first card shows a player loaded with autoplay and keeps its size, and the focus is in the player
    And pressing Play on a second video puts the first card's picture back and leaves one player
    And pressing Enter on a third video's Play button plays it and stops the second
    And the page does not scroll sideways after each press

    Examples:
      | width |
      | 375   |
      | 1440  |
