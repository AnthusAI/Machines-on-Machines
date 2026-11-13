Feature: Videos and Findings show the best of each section
  The Videos page and the Findings page do not have one big "Accepted" list. After a lead of the best few References that are in no section, each newsroom
  section that has a page here gets a block: its name linking to the section's own list of videos (or findings), its best few References, and "More
  <section> videos…" when it has more. The section holding the best-ranked Reference comes first. A block's head shows no count. A section with nothing in it
  has no block, and a section that has no page here has no block either: its References are in the lead and the list. Inside a block the References keep the
  order the whole site gives them: this week's first (the rolling seven-day window), then an editor's stars, then the crowd's prediction, newest within a tie,
  then the weeks before. No Reference is listed twice. The Markdown twin of each page stays one ranked list.

  On Findings a block is rows of cards: with a lead the first block is "wide" (two rows of three) and no block is a feature; with no lead, the first block
  features its best Reference on a row of its own; later sections thin out to one row of three; every row is full at any width. On Videos a block is at most two
  rows of three video cards (see features/video-cards.feature), with its "More <section> videos…" link under them.

  Scenario Outline: Sections take the place of the big Accepted header
    When I open the page "<route>"
    Then the page does not contain ">Accepted</h2>"
    And the page does not contain "Not in a section yet"

    Examples:
      | route      |
      | /videos/   |
      | /findings/ |

  Scenario: Video blocks are ordered by their best-ranked video, and a section with no page here has no block
    When I open the page "/videos/"
    Then the references sections appear in this order
      | section            |
      | Privacy & Security |
      | Math & Science            |
    And the page does not contain "aria-label=\"Papyrus\""
    And the page does not contain "aria-label=\"Evaluation\""

  Scenario Outline: Blocks of a page with some sections are ordered by their best item
    Given the "some" Reference case is projected
    When I open the case page "<route>"
    Then the references sections appear in this order
      | section            |
      | Privacy & Security |
      | Math & Science            |
      | Agents             |

    Examples:
      | route      |
      | /videos/   |
      | /findings/ |

  Scenario: Inside the page an editor's stars order this week's items, and an older week follows however high its stars
    When I open the page "/videos/"
    Then "Fixture talk: agent traces in practice" comes before "Fixture talk: grading with judges"
    And "Fixture talk: cheaper evaluation runs" comes before "Fixture talk: an older evaluation keynote"

  Scenario Outline: On Findings, with a lead the first block is wide and none is a feature, and without one the first block is the feature
    Given the "<case>" Reference case is projected
    When I open the case page "/findings/"
    Then the references section "Privacy & Security" has the "<first>" layout
    And the references section "Math & Science" has the "<second>" layout

    Examples:
      | case | first   | second  |
      | some | wide    | wide    |
      | all  | feature | wide    |

  Scenario: The first block of a Findings page with no lead has one card on a row of its own
    Given the "all" Reference case is projected
    When I open the case page "/findings/"
    Then the references section "Privacy & Security" has the "feature" layout with one card on its own row

  Scenario: A Findings block's name links to the section's own list, and a block with more than it shows ends with a More link
    Given the "some" Reference case is projected
    When I open the case page "/findings/"
    Then the references section "Privacy & Security" links to "/security/findings/" and ends with "More Privacy & Security findings…"
    And the references section "Agents" links to "/agents/findings/" and has no More link

  Scenario: A Videos block's name links to the section's own list, and a block with more than its two rows ends with a More link
    Given the "some" Reference case is projected
    When I open the case page "/videos/"
    Then the references section "Privacy & Security" links to "/security/videos/" and ends with "More Privacy & Security videos…"
    And the references section "Agents" links to "/agents/videos/" and has no More link

  Scenario Outline: A block head shows no count
    Given the "some" Reference case is projected
    When I open the case page "<route>"
    Then no block head shows a count

    Examples:
      | route      |
      | /videos/   |
      | /findings/ |

  Scenario Outline: No Reference is listed twice
    When I open the page "<route>"
    Then no card on the page links to the same address twice

    Examples:
      | route      |
      | /videos/   |
      | /findings/ |

  Scenario: Videos only list videos
    When I open the page "/videos/"
    Then the page does not contain "Fixture paper: judges that grade themselves"

  Scenario: Every row is a whole row at any width
    Then the stylesheet "/css/site-theme.css" gives a row of one, two or three References its own columns on every width

  Scenario: The Markdown twin is one ranked list with no Accepted header
    When I read the Markdown twin "/videos/index.md"
    Then the page does not contain "## Accepted"
    And the page contains "Fixture talk: agent traces in practice"
