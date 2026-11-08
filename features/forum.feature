Feature: The conversations page is a forum
  Ryan: "The conversations page needs to look more like a web forum. A modern design, but still that old paradigm." /conversations/ is a
  list of boards. A board is a newsroom section; its heading row names the section, says what it is, how many conversations it holds and when
  it was last active, and the conversations follow as dense rows, newest activity first. Boards are ordered by their latest activity. A
  conversation that belongs to no section sits on a last board, "General", so none is ever hidden. A thread page is a forum topic: a breadcrumb
  to its board, the title, what it discusses, then the posts in order, each with an author block, a number and a time.

  Which board a conversation is on: the section its thread data names (a Papyrus feature newer than the engine this site pins, read from
  the card when the engine prints it), otherwise the section of the story it is about, otherwise General. The site is static, so the forum
  is read-only; there is no reply form. The engine does not page its list of conversations (it pages Reference lists), so the page holds every
  conversation and the site's script shows the first ten rows of a board with a Load more button for the rest; without a script every row shows.
  The look follows the design system: flat tones and rounded rectangles, no border, outline or hairline, Lucide icons, and no meaning carried by
  colour alone (a mark is an icon with words beside it).

  Scenario: Conversations are grouped under a board for each section, most recently active board first, with General last
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then the conversations page has the boards in this order
      | board             |
      | Privacy & Security |
      | Field Notes       |
      | Math & Science           |
      | Law & Policy      |
      | General           |

  Scenario: A board's heading links to its section page only when that page exists
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then the board "Privacy & Security" heading links to "/security/"
    And the board "Law & Policy" heading links to "/law-policy/"
    And the board "Field Notes" heading does not link anywhere
    And the board "General" heading does not link anywhere

  Scenario: A board's heading row says what the section is, how many conversations it has and when it was last active
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then the board "Privacy & Security" says "How machines are attacked, defended and watched, and who gets to know." in its heading row
    And the board "Privacy & Security" says "2 conversations" in its heading row
    And the board "Privacy & Security" says "Last activity" in its heading row
    And the board "General" says "Conversations that are not about a story in one of our sections." in its heading row

  Scenario: A conversation about a story belongs to the story's section and one about a reference to General
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then the board "Field Notes" has 1 conversations
    And the board "Math & Science" has 1 conversations
    And the board "General" has 2 conversations
    And in the board "General" the conversations come in this order
      | title                                                  |
      | Is a judge that shares training data still a judge?    |
      | Who should approve a benchmark?                        |

  Scenario: A card that names its section is on that board, whatever its story, and one that names none falls back to its story and then to General
    Given a conversation card in the engine's markup that names its section "Math & Science" and is about a story of the section "Privacy & Security"
    And a conversation card in the engine's markup that names no section and is about a reference
    Then the first is on the board "Math & Science" and the second is on the board "General"

  Scenario: Each board lists its conversations newest activity first
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then in the board "Privacy & Security" the conversations come in this order
      | title                          |
      | Who audits the audit log?      |
      | Is a leaked prompt a breach?   |

  Scenario: A row shows the title, what it is about, who spoke last, how many replies and when
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then the row "Who audits the audit log?" shows the title, "Synthetic Security article 1" as what it is about, the latest author "ada", "2 replies" and a last activity time with an exact moment
    And the row "Who audits the audit log?" links its title to "/conversations/b1c2d3e4f504/" and what it is about to "/articles/synthetic-security-article-1/"
    And the row "What counts as a crash for a long-running agent?" shows the title, "Durable execution is how long-running agents survive a crash" as what it is about, the latest author "AI", "1 reply" and a last activity time with an exact moment

  Scenario: A header strip counts the forum and names what was active last
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then the header strip counts the boards, conversations and messages and names the most recently active conversation

  Scenario: Every conversation is on the page, so Load more can reach all of them
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then the conversations page has 19 conversation rows in all and none is hidden in the markup
    And the page contains "data-rows-per-page"
    And the board "Law & Policy" has 13 conversations

  Scenario: A mark is an icon with words, never a colour alone
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then every mark in the forum is a Lucide icon with words beside it

  Scenario: The forum draws no borders, outlines or shadows
    Given the Machines on Machines site is projected from the fixtures
    Then the stylesheet "css/site-theme.css" gives the forum no border, outline or shadow

  Scenario: The conversations page no longer lists conversations as picture cards
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then the page does not contain "mom-thread-card"

  Scenario: A thread page is a topic: breadcrumb to the board, what it discusses, then numbered posts
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/b1c2d3e4f511/"
    Then the thread page is a topic with the board breadcrumb "Law &amp; Policy" and the story it discusses
    And the board in the breadcrumb is a link to "/law-policy/"
    And the thread page stacks 4 posts numbered #1, #2, #3, #4
    And every post has an author block on the left with its number, and a time with an exact moment
    And the post by a reader "grace" shows the handle and the role "Reader"
    And the post by "AI" shows the role label "AI"
    And the post by "Editor" shows the role label "Editor"

  Scenario: A thread with no section has General as its board, which is not a link
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/b1c2d3e4f501/"
    Then the board in the breadcrumb is plain text "General"
    And the page contains "Discussing"

  @browser
  Scenario Outline: The forum fits the window from a phone to a Studio Display
    Given the Machines on Machines site is projected from the fixtures
    When I draw "/conversations/" in a browser <width> pixels wide
    Then the page does not scroll sideways and nothing in the forum is drawn past the window
    And no title, anchor line or number overflows its row and no two rows or posts overlap
    And the forum has no border, outline or shadow as drawn

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |
      | 2560  |

  @browser
  Scenario Outline: Load more reaches every conversation
    Given the Machines on Machines site is projected from the fixtures
    When I draw "/conversations/" in a browser <width> pixels wide
    Then pressing Load more until it is gone shows all 19 conversations

    Examples:
      | width |
      | 375   |
      | 1440  |

  @browser
  Scenario Outline: A thread page fits the window
    Given the Machines on Machines site is projected from the fixtures
    When I draw "/conversations/b1c2d3e4f511/" in a browser <width> pixels wide
    Then the page does not scroll sideways and nothing in the forum is drawn past the window
    And no title, anchor line or number overflows its row and no two rows or posts overlap
    And the forum has no border, outline or shadow as drawn

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |
      | 2560  |

  # The layout pass. Ryan, on real devices: "it looks really good for certain viewport widths, but not all." The site card (the tilted sticker) did not fit the narrow
  # layouts and the forum sat crammed on the left of a wide window. The forum now has two parts below and above 1320 design pixels (990 real pixels at the site's 75% scale):
  # one column of boards with the site card once between the first board and the next, and the boards plus a side column of one page column (the site card, the counts, the
  # most active conversations). Measured with a browser (tools/measure_forum_layout.cjs), this keeps the card out of the first screen on a phone, off every row, and uses the width
  # of a Studio Display: boards sit side by side, as many as fit 600 real pixels each.

  @browser
  Scenario Outline: The site card sits between two boards on a narrow window and in the side column on a wide one
    Given the Machines on Machines site is projected from the fixtures
    When I lay out "/conversations/" in a browser <width> pixels wide
    Then there is exactly one site card and it is <place>
    And the page does not scroll sideways and no row, board heading or panel is covered by the site card or a side panel

    Examples:
      | width | place                           |
      | 375   | between the first two boards    |
      | 640   | between the first two boards    |
      | 820   | between the first two boards    |
      | 1100  | in the side column beside the boards |
      | 1440  | in the side column beside the boards |
      | 1920  | in the side column beside the boards |
      | 2560  | in the side column beside the boards |

  @browser
  Scenario Outline: A wide window is filled with boards side by side and no row is stretched
    Given the Machines on Machines site is projected from the fixtures
    When I lay out "/conversations/" in a browser <width> pixels wide
    Then the boards stand in <columns> columns
    And no more than 40 pixels are left blank at the right of the page
    And no row is wider than 1010 pixels and no text is cut off

    Examples:
      | width | columns |
      | 1100  | 1       |
      | 1440  | 1       |
      | 1920  | 2       |
      | 2560  | 3       |

  Scenario: Each section has a board page of its own, listing that section's conversations
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/security/conversations/"
    Then the page has the heading "Privacy &amp; Security conversations"
    And the board page lists the conversations in this order
      | title                          |
      | Who audits the audit log?      |
      | Is a leaked prompt a breach?   |
    And the board "Privacy & Security" heading links to "/security/"
    And the board "Privacy & Security" says "2 conversations" in its heading row
    And the page contains "How machines are attacked, defended and watched, and who gets to know."
    And the page contains "mom-forum-card"

  Scenario: Every one of the ten sections has a board page
    Given the Machines on Machines site is projected from the fixtures
    Then every section in web/sections.json has a board page at "/<id>/conversations/"

  Scenario: A section with no conversations says so
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/art/conversations/"
    Then the page contains "No conversations in Art yet."

  Scenario: A board with more rows than the index shows links to its board page
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then the board "Law & Policy" ends with the link "More Law &amp; Policy conversations…" to "/law-policy/conversations/"
    And the board "Privacy & Security" has no such link
    And the board "General" has no such link

  Scenario: A section page's conversations block links to the section's board page
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/security/"
    Then the page links "All conversations" to "/security/conversations/"

  Scenario: The board page's rows are all reachable the way the index's are
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/law-policy/conversations/"
    Then the page contains "data-rows-per-page"
    And the conversations page has 13 conversation rows in all and none is hidden in the markup

  @browser
  Scenario Outline: A board page fits the window and keeps the site card out of the first screen on a phone
    Given the Machines on Machines site is projected from the fixtures
    When I lay out "/law-policy/conversations/" in a browser <width> pixels wide
    Then the page does not scroll sideways and no row, board heading or panel is covered by the site card or a side panel
    And no row is wider than 1010 pixels and no text is cut off
    And the site card is <card>

    Examples:
      | width | card                                    |
      | 375   | not drawn                               |
      | 640   | not drawn                               |
      | 820   | not drawn                               |
      | 1100  | in the side column beside the boards    |
      | 1440  | in the side column beside the boards    |
      | 1920  | in the side column beside the boards    |
      | 2560  | in the side column beside the boards    |

  @browser
  Scenario Outline: A thread page has no site card at any width, and a side panel of facts on a wide window
    Given the Machines on Machines site is projected from the fixtures
    When I lay out "/conversations/b1c2d3e4f511/" in a browser <width> pixels wide
    Then the site card is not drawn
    And the page does not scroll sideways and no row, board heading or panel is covered by the site card or a side panel
    And the facts panel is <facts>

    Examples:
      | width | facts     |
      | 375   | not drawn |
      | 820   | not drawn |
      | 1100  | drawn     |
      | 1440  | drawn     |
      | 1920  | drawn     |
      | 2560  | drawn     |

  Scenario: The forum's pages keep the shared page header but the site card is in the forum, once
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/"
    Then the page has the heading "Conversations"
    And the page does not contain "mom-page-card"
    And the page contains "mom-forum-card"

  Scenario: A thread page has no site card in its markup
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/conversations/b1c2d3e4f511/"
    Then the page does not contain "mom-sticker"
    And the page contains "About this conversation"
