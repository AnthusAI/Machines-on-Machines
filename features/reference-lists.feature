Feature: Every Reference on a list page can be reached
  The Videos page and the Findings page group the References that have a newsroom section by section, thinned to the best of each, and every group links
  to its section's page. A Reference in no section is never hidden: all of them are in one list headed "Not in a section yet", newest first with this week's
  best first (the site's rolling seven-day buckets), whose first page has 24 cards and which ends with a Load more control. The control loads static data
  files, so the list reaches every one, and each data file is also an ordinary page a reader without a script can follow. When nothing at all is in a section
  (the live situation at first) there are no groups, and the list is the whole page, headed "All videos" or "All findings". A section's own page ends its
  videos with "More videos…", which leads to the full list of that section's videos.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario Outline: The References in no section are one list that reaches all of them
    When I open the page "<route>"
    Then the list headed "Not in a section yet" shows only References with no section and has no link
    And the first page of the list has at most 24 cards
    And the list has a Load more control and a data file that reaches the rest
    And the list reaches every <kind> with no section exactly once
    And the list is newest first

    Examples:
      | route    | kind    |
      | /videos/ | video   |
      | /wire/   | finding |

  Scenario Outline: The list's pages are real pages too
    When I open the page "<route>"
    Then a page of the list that a reader without a script can follow is in the site

    Examples:
      | route    |
      | /videos/ |
      | /wire/   |

  Scenario Outline: The groups at the top hold only References that have a section
    When I open the page "<route>"
    Then the page has a section named "Privacy & Security"
    And the page has a section named "Science"
    And no card on the page links to the same address twice

    Examples:
      | route    |
      | /videos/ |
      | /wire/   |

  Scenario: Every video of a section is on the section's own list
    Then the full video list of the section "Privacy & Security" at "/security/videos/" shows all 7 of its videos
    And the full video list of the section "Science" at "/science/videos/" shows all 1 of its videos

  Scenario: A section with no videos has a list that says so
    When I open the page "/history/videos/"
    Then the page contains "No videos in History yet."

  Scenario: The page of a list with nothing in a section is the whole list, headed with what it holds
    Then a Reference list page with no section groups is headed "All videos" and one with groups is headed "Not in a section yet"

  Scenario: The site publishes the list files
    Then the stylesheet "/css/site-theme.css" gives the list of everything its own room and hides it when it is empty
    And the file "js/papyrus-reference-list.js" exists in the site
