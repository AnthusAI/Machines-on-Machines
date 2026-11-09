Feature: A section's own list of videos and of findings
  Every newsroom section has a list of every video filed under it (`/<section>/videos/`) and a list of every accepted source filed under it that is not a
  video (`/<section>/findings/`), this week's best first. Each begins with a lead of the best four, then one list with no heading that loads as the reader
  scrolls. A section with nothing says so. These are the pages the "More <section> videos…" and "More <section> findings…" links on Videos and Findings,
  and the Findings panel on the section's front page, lead to.

  Scenario Outline: A section's list reaches all of its References
    Given the "all" Reference case is projected
    When I open the case page "<route>"
    Then the page title is "<title>" and its sentence is "<sentence>"
    And the page has no heading other than its title
    And the lead has 4 cards, in rows of 1 then 3, and no heading
    And the lead and the list reach all 70 <kind> filed under "Privacy & Security" exactly once
    And no address appears twice across the lead, the blocks, the list and its data files

    Examples:
      | route              | kind     | title                          | sentence                                                                                                         |
      | /security/videos/  | videos   | Privacy & Security videos      | Every video filed under Privacy & Security, this week's best first.                                              |
      | /security/findings/ | findings | Privacy & Security findings    | Every source filed under Privacy & Security that our editors and Cyclotron have accepted, this week's best first. |

  Scenario: A section's list of findings has no video
    Given the "all" Reference case is projected
    Then no videos appear on "/security/findings/", its data files, "/science/findings/" and the findings panel of "/security/"

  Scenario Outline: A section with nothing says so
    Given the "all" Reference case is projected
    When I open the case page "<route>"
    Then the page contains "<sentence>"
    And the page has no lead, no Load more link and no block

    Examples:
      | route              | sentence                    |
      | /history/videos/   | No videos in History yet.   |
      | /history/findings/ | No findings in History yet. |

  Scenario Outline: Every section in the list has both
    Then the page "<route>" was projected

    Examples:
      | route                     |
      | /security/videos/         |
      | /security/findings/       |
      | /ai-safety/videos/        |
      | /ai-safety/findings/      |
      | /agents/videos/           |
      | /agents/findings/         |
      | /science/videos/          |
      | /science/findings/        |
      | /history/videos/          |
      | /history/findings/        |
      | /gaming/videos/           |
      | /gaming/findings/         |
      | /art/videos/              |
      | /art/findings/            |
      | /law-policy/videos/       |
      | /law-policy/findings/     |
      | /full-self-driving/videos/ |
      | /full-self-driving/findings/ |
      | /music/videos/            |
      | /music/findings/          |

  @browser
  Scenario Outline: Scrolling to the end of a section's list shows every video once
    Given the "all" Reference case is projected
    When I look at the list page "/security/videos/" in a browser <width> pixels wide and scroll to the end
    Then all 70 videos are shown exactly once

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |
      | 2560  |

  @browser
  Scenario Outline: A section's list fills whole rows
    Given the "all" Reference case is projected
    When I look at the list page "/security/findings/" in a browser <width> pixels wide
    Then every row of the lead and of every block is full
    And the list's first page fills whole rows
    And the page does not scroll sideways and has no heading in its lead or list
    And the site title card touches no card

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |
      | 2560  |

  Scenario: A card under its section's heading does not repeat the section name
    On the Articles and Posts pages, in the home page's section groups and on a section's own pages, the section is already the heading, so the small label above each headline is not shown. Pages that mix sections, such as a tag page, keep it.
    Then the stylesheet "css/site-theme.css" hides the section label above a headline where the section is already the heading
