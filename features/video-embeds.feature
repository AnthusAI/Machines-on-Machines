Feature: A video on a platform the site can embed plays in its card when the reader presses Play, and any other video keeps its picture
  The Worth Watching panels and the Videos lists show References that are videos. When a video is on a platform the site embeds (the providers
  `projection.json` lists under "embeds", drawn 16:9; the site's Content-Security-Policy allows exactly those), its card shows the video's picture (the
  Reference's image, or the site's placeholder art) as a Play button, the same 16:9 box on the 4px rhythm. No player is loaded with the page: a page of
  sixty videos draws sixty pictures and no frames. Pressing the button (or Enter or Space on it) swaps the platform's own privacy-enhanced player
  (youtube-nocookie.com, player.vimeo.com with do-not-track) into the picture's place and starts it; the card is the same size, so nothing moves. The
  button is named "Play: <title>" and the player has a descriptive title. A button is interactive, so it cannot sit inside the card's link: the headline is
  the link, and the stars and the "site · date" line stay under it. A video on any other platform, or an address that is not one video, keeps its picture,
  which links out as before. How the swap behaves in a browser is in features/video-cards.feature.

  Scenario: A YouTube video card shows its picture as a Play button that starts the platform's player
    Given a reference tile for the address "https://www.youtube.com/watch?v=SnbkIm56TfI" titled "How I located a livestream"
    When the tile is drawn as a card
    Then the card has a Play button that starts the player at "https://www.youtube-nocookie.com/embed/SnbkIm56TfI?autoplay=1"
    And the Play button's face is the card's picture
    And the card has no player frame yet

  Scenario: The button and the player are named, and the player is allowed to start itself when its button is pressed
    Given a reference tile for the address "https://youtu.be/SnbkIm56TfI" titled "How I located a livestream"
    When the tile is drawn as a card
    Then the Play button is named "Play: How I located a livestream"
    And the Play button carries the player's title "How I located a livestream, video player"
    And the Play button lets the player start itself

  Scenario: A video with no picture of its own shows the site's placeholder art as its Play button
    Given a reference tile with no picture for the address "https://www.youtube.com/watch?v=SnbkIm56TfI" titled "How I located a livestream"
    When the tile is drawn as a card
    Then the Play button's face is the site's placeholder art

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

  Scenario: The Play button is a flat rounded button with the picture's own box, a visible focus mark and a word with its icon
    Then the stylesheet "/css/site-theme.css" draws the Play button without border, with a focus outline and a label beside its icon

  Scenario: Instagram is embeddable but not 16:9, so its card keeps the picture
    Given a reference tile for the address "https://www.instagram.com/reel/Cabcde12345/" titled "A reel"
    When the tile is drawn as a card
    Then the card has no player

  # The addresses below are fake: no real Vimeo video has these numbers or hashes.
  Scenario Outline: A Vimeo video card starts Vimeo's player when Play is pressed, with no tracking cookies
    Given a reference tile for the address "<address>" titled "A Vimeo talk"
    When the tile is drawn as a card
    Then the card has a Play button that starts the player at "<player>"
    And the Play button carries the player's title "A Vimeo talk, video player"
    And the card has no player frame yet

    Examples:
      | address                                          | player                                                             |
      | https://vimeo.com/123456789                      | https://player.vimeo.com/video/123456789?dnt=1&autoplay=1          |
      | https://player.vimeo.com/video/123456789         | https://player.vimeo.com/video/123456789?dnt=1&autoplay=1          |
      | https://vimeo.com/channels/fakechannel/123456789 | https://player.vimeo.com/video/123456789?dnt=1&autoplay=1          |
      | https://vimeo.com/123456789/abcdef1234           | https://player.vimeo.com/video/123456789?dnt=1&h=abcdef1234&autoplay=1 |

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
