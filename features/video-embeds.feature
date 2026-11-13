Feature: A video on a platform the site can embed plays in its card, and any other video keeps its picture
  The Worth Watching panels and the Videos lists show References that are videos. When a video is on a platform the site embeds (the providers
  `projection.json` lists under "embeds", drawn 16:9; the site's Content-Security-Policy allows exactly those), its card shows the platform's own
  player in the picture's place, the same 16:9 box on the 4px rhythm, so the card is the same size and nothing moves when the player loads. The
  player is the privacy-enhanced one (youtube-nocookie.com), loads lazily so a player below the fold costs nothing until the reader scrolls near it,
  never starts by itself, and has a descriptive title. A player is interactive, so it cannot sit inside the card's link: the headline is the link, and
  the stars and the "site · date" line stay under it. A video on any other platform, or an address that is not one video, keeps its picture, which links
  out as before.

  Scenario: A YouTube video card plays in place of its picture
    Given a reference tile for the address "https://www.youtube.com/watch?v=SnbkIm56TfI" titled "How I located a livestream"
    When the tile is drawn as a card
    Then the card has a player from "https://www.youtube-nocookie.com/embed/SnbkIm56TfI"
    And the card has no picture

  Scenario: The player waits to load, never autoplays and is named
    Given a reference tile for the address "https://youtu.be/SnbkIm56TfI" titled "How I located a livestream"
    When the tile is drawn as a card
    Then the player loads lazily
    And the player does not autoplay
    And the player's title is "How I located a livestream, video player"

  Scenario: The headline, the stars and the source line stay below the player
    Given a reference tile for the address "https://www.youtube.com/watch?v=SnbkIm56TfI" titled "How I located a livestream"
    When the tile is drawn as a card
    Then the card's headline links to "https://www.youtube.com/watch?v=SnbkIm56TfI"
    And the card is not itself a link
    And the card shows the source and the date under the headline

  Scenario: A video on a platform the site does not embed keeps its picture, which links out
    Given a reference tile for the address "https://video.example/talk-1" titled "A talk"
    When the tile is drawn as a card
    Then the card has no player
    And the card is a link to "https://video.example/talk-1" with a picture

  Scenario: A YouTube address that is not one video keeps its picture
    Given a reference tile for the address "https://www.youtube.com/@somechannel" titled "A channel"
    When the tile is drawn as a card
    Then the card has no player

  Scenario: The stylesheet reserves the picture's 16:9 box for the player and keeps it inside the card
    Then the stylesheet "/css/site-theme.css" gives the player the picture's ratio, no border and the full width of its slot

  Scenario: Instagram is embeddable but not 16:9, so its card keeps the picture
    Given a reference tile for the address "https://www.instagram.com/reel/Cabcde12345/" titled "A reel"
    When the tile is drawn as a card
    Then the card has no player

  # The addresses below are fake: no real Vimeo video has these numbers or hashes.
  Scenario Outline: A Vimeo video card plays in Vimeo's player, with no tracking cookies and no autoplay
    Given a reference tile for the address "<address>" titled "A Vimeo talk"
    When the tile is drawn as a card
    Then the card has a player from "<player>"
    And the player loads lazily
    And the player does not autoplay
    And the player's title is "A Vimeo talk, video player"
    And the card has no picture

    Examples:
      | address                                         | player                                                 |
      | https://vimeo.com/123456789                     | https://player.vimeo.com/video/123456789?dnt=1         |
      | https://player.vimeo.com/video/123456789        | https://player.vimeo.com/video/123456789?dnt=1         |
      | https://vimeo.com/channels/fakechannel/123456789 | https://player.vimeo.com/video/123456789?dnt=1        |
      | https://vimeo.com/123456789/abcdef1234          | https://player.vimeo.com/video/123456789?dnt=1&h=abcdef1234 |

  Scenario: A Vimeo address that is not one video keeps its picture
    Given a reference tile for the address "https://vimeo.com/channels/fakechannel" titled "A channel"
    When the tile is drawn as a card
    Then the card has no player

  Scenario: The site's embeds setting lists Vimeo, so its Content-Security-Policy lets the player's frame load
    Then the site's frame-src policy allows "https://player.vimeo.com" and "https://www.youtube-nocookie.com"

  Scenario: A platform the site does not embed keeps its picture beside the embedded ones
    Given a reference tile for the address "https://www.dailymotion.com/video/x1fake" titled "A Dailymotion talk"
    When the tile is drawn as a card
    Then the card has no player
