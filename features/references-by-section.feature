Feature: Videos and Findings are grouped by section
  The Videos page and the Findings page do not have one big "Accepted" list. Each is broken into sections, the way the Articles page is.
  A Reference is filed under a newsroom section, and its section is the group it belongs to. The section that holds the best-ranked
  Reference comes first, so the first card on the page is the best one, and that section gets the most room: a feature card on a row of its own, then rows of three, while
  later sections thin out. Inside a section the References keep the order the home page gives them: this week's first (the site's rolling
  seven-day window), then an editor's stars, then the crowd's prediction, newest within a tie, then the weeks before. A Reference with no
  section is never given one; those wait at the end. A section with nothing in it has no heading, no Reference is listed twice, and every
  row is full at any width. The Markdown twin of each page stays one ranked list.

  Scenario Outline: The big Accepted header is gone and sections take its place
    When I open the page "<route>"
    Then the page does not contain ">Accepted</h2>"
    And the page has a section named "Evaluation"
    And the page has a section named "Papyrus"

    Examples:
      | route    |
      | /videos/ |
      | /wire/   |

  Scenario: Video sections are ordered by their best-ranked video, and videos with no section come last
    When I open the page "/videos/"
    Then the references sections appear in this order
      | section            |
      | Evaluation         |
      | Papyrus            |
      | Privacy & Security |
      | Science            |
      | More videos        |

  Scenario: Findings sections are ordered the same way, by their best-ranked finding, and findings with no section come last
    When I open the page "/wire/"
    Then the references sections appear in this order
      | section            |
      | Evaluation         |
      | Papyrus            |
      | Privacy & Security |
      | Science            |
      | More findings      |

  Scenario: Inside a section an editor's stars order this week's items, and an older week follows however high its stars
    When I open the page "/videos/"
    Then in the references section "Papyrus" "Fixture talk: agent traces in practice" comes before "Fixture talk: grading with judges"
    And in the references section "Evaluation" "Fixture talk: cheaper evaluation runs" comes before "Fixture talk: an older evaluation keynote"

  Scenario: The first section features its best Reference, and later sections are smaller
    When I open the page "/wire/"
    Then the references section "Evaluation" has the "feature" layout with one card on its own row
    And the references section "Papyrus" has the "wide" layout
    And the references section "More findings" has the "plain" layout

  Scenario Outline: A section's name links to its page, and a section with more than one item ends with a More link
    When I open the page "<route>"
    Then the references section "Privacy & Security" links to "/security/" and ends with "More Privacy & Security…"
    And the references section "Science" links to "/science/" and has no More link

    Examples:
      | route    |
      | /videos/ |
      | /wire/   |

  Scenario Outline: A section with no page and the group of unsectioned items get no link
    When I open the page "<route>"
    Then the references section "Papyrus" has no link to a section page
    And the references section "<unsectioned>" has no link to a section page

    Examples:
      | route    | unsectioned   |
      | /videos/ | More videos   |
      | /wire/   | More findings |

  Scenario Outline: No Reference is listed twice
    When I open the page "<route>"
    Then no card on the page links to the same address twice

    Examples:
      | route    |
      | /videos/ |
      | /wire/   |

  Scenario: Videos only list videos
    When I open the page "/videos/"
    Then the page does not contain "Fixture paper: judges that grade themselves"

  Scenario: Every row is a whole row at any width
    Then the stylesheet "/css/site-theme.css" gives a row of one, two or three References its own columns on every width

  Scenario: The not-accepted sources fill whole rows too
    When I open the page "/wire/"
    Then the not-accepted list is one row of three
    And sixteen not-accepted sources are in rows of three, with a closing two rows of two

  Scenario: An empty page says so plainly and draws no section heading
    Then a page with no accepted References keeps its plain empty text and has no section

  Scenario: The Markdown twin is one ranked list with no Accepted header
    When I read the Markdown twin "/videos/index.md"
    Then the page does not contain "## Accepted"
    And the page contains "Fixture talk: agent traces in practice"
