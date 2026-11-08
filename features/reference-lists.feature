Feature: Every video and finding can be reached, however many are filed under a section
  The Videos page and the Findings page show every accepted Reference whether a publication files all, some or none of them under a newsroom
  section. References that are in no section never get a heading, not "All videos" and not "Not in a section yet": at the top a lead of the four most
  recent, best ones, then a block for each section with its best few (the section's name links to its own list and the block ends with "More <section>
  videos…"), then one list with no heading of the rest, which loads as the reader scrolls and ends with a Load more control. Every list is ordered by
  the site's rolling seven-day buckets, newest first, then an editor's stars, then Cyclotron's confidence, newest within a tie. Findings are the accepted
  References that are not videos. A Reference whose section has no page here counts as in no section, so it stays in the lead and the list, with its section
  named on its card. No Reference is shown twice on a page or across its data files, and no cap hides one: the data files reach every Reference.

  The same pages are drawn in a browser at 375, 820, 1440 and 2560 pixels wide when Playwright is installed:
  `PLAYWRIGHT_MODULE=<path to playwright> behave features/reference-lists.feature features/section-lists.feature --tags=@browser`

  Scenario Outline: Nothing filed under a section: a lead, then one list, and no heading but the page's own
    Given the "none" Reference case is projected
    When I open the case page "<route>"
    Then the page has no heading other than its title
    And the lead has 4 cards, in rows of 1 then 3, and no heading
    And the list has no heading, shows <first> cards on its first page and has a Load more link
    And the lead and the list reach all 200 <kind> exactly once
    And the page has no block for any section
    And the page does not contain "All videos"
    And the page does not contain "All findings"
    And the page does not contain "Not in a section yet"
    And the page does not contain "Found by machines"
    And the page does not contain "Not accepted yet"

    Examples:
      | route     | kind     | first |
      | /videos/  | videos   | 60    |
      | /findings/ | findings | 50    |

  Scenario Outline: Some filed under a section: the lead takes the best of the rest, and each section has a block
    Given the "some" Reference case is projected
    When I open the case page "<route>"
    Then the lead holds the 4 best unfiled <kind> in the shared order
    And the page has blocks for "Privacy & Security", "Math & Science" and "Agents" in that order and none for "Papyrus" or "History"
    And the list holds every unfiled <kind> that the lead does not
    And the "Papyrus" <kind> are in the lead or the list and say their section on the card
    And no address appears twice across the lead, the blocks, the list and its data files
    And every <kind> in a block is filed under that block's section

    Examples:
      | route      | kind     |
      | /videos/   | videos   |
      | /findings/ | findings |

  Scenario Outline: Everything filed under a section: only blocks, no lead, no list and no empty sentence
    Given the "all" Reference case is projected
    When I open the case page "<route>"
    Then the page has no lead, no list, no Load more link and no empty sentence
    And the first block is "Privacy & Security" with the "feature" layout

    Examples:
      | route      |
      | /videos/   |
      | /findings/ |

  Scenario Outline: Only a few References: the lead holds the unfiled ones and nothing else is drawn for them
    Given the "few" Reference case is projected
    When I open the case page "<route>"
    Then the lead holds both unfiled <kind> in one row of 2
    And the page has no list and no Load more link

    Examples:
      | route      | kind     |
      | /videos/   | videos   |
      | /findings/ | findings |

  Scenario Outline: Nothing accepted yet: the page says so and draws no block
    Given the "empty" Reference case is projected
    When I open the case page "<route>"
    Then the page contains "<sentence>"
    And the page has no block for any section
    And the page has no lead

    Examples:
      | route      | sentence                            |
      | /videos/   | No videos have been accepted yet.   |
      | /findings/ | Nothing has been accepted yet.      |

  Scenario: A publication that declares no sections has a lead and a list and nothing else
    Given the "some" Reference case is projected for a publication that declares no sections
    When I open the case page "/videos/"
    Then the lead and the list reach all 170 videos exactly once
    And the page has no block for any section
    And no page exists at "/security/videos/" in the case

  Scenario: This week's best come first and an older week follows, however high its stars
    Given the "none" Reference case is projected
    When I open the case page "/videos/"
    Then the first card of the lead is this week's highest-starred video
    And the video with five stars, accepted 20 days ago, comes after every video accepted in the last seven days

  Scenario Outline: A page of the list is a real page a reader without a script can follow
    Given the "none" Reference case is projected
    When I open the case page "<route>"
    Then a data file of the list is also a page with the site's chrome and Previous and Next links

    Examples:
      | route      |
      | /videos/   |
      | /findings/ |

  Scenario: Findings never show a video, on any page or in any data file
    Given the "some" Reference case is projected
    Then no videos appear on "/findings/", its data files, "/security/findings/" and the findings panel of "/security/"

  Scenario: The stylesheet hides an empty list and no longer has the old headed lists
    Given the "none" Reference case is projected
    Then the case stylesheet hides a stream with nothing in it, and has no ".mom-untagged" or ".mom-all-refs"
    And the file "js/papyrus-reference-list.js" exists in the case

  Scenario: Videos shows no pending References
    Given the "some" Reference case is projected
    When I open the case page "/videos/"
    Then the page does not contain "Not accepted yet"
    And the page does not contain "Case some recommended video"

  @browser
  Scenario Outline: Videos and Findings fill whole rows from a phone to a Studio Display
    Given the "some" Reference case is projected
    When I look at the list page "<route>" in a browser <width> pixels wide
    Then every row of the lead and of every block is full
    And the list's first page fills whole rows
    And the page does not scroll sideways and has no heading in its lead or list
    And the site title card touches no card

    Examples:
      | route      | width |
      | /videos/   | 375   |
      | /videos/   | 820   |
      | /videos/   | 1440  |
      | /videos/   | 2560  |
      | /findings/ | 375   |
      | /findings/ | 820   |
      | /findings/ | 1440  |
      | /findings/ | 2560  |

  @browser
  Scenario Outline: Scrolling to the end shows every video exactly once
    Given the "none" Reference case is projected
    When I look at the list page "/videos/" in a browser <width> pixels wide and scroll to the end
    Then every one of the 200 videos is shown exactly once and the list says "All 196 are shown."

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |
      | 2560  |

  @browser
  Scenario Outline: With everything filed, only blocks are drawn
    Given the "all" Reference case is projected
    When I look at the list page "/videos/" in a browser <width> pixels wide
    Then there is no lead, no list and no Load more control, and the first block has the feature layout
    And every row of the lead and of every block is full

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |
      | 2560  |

  @browser
  Scenario Outline: With nothing accepted the empty sentence is not covered by the site title card
    Given the "empty" Reference case is projected
    When I look at the list page "/videos/" in a browser <width> pixels wide
    Then the empty sentence is visible and the site title card does not cover it

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |
      | 2560  |
