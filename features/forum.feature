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
    And the forum is no wider than <widest> pixels

    Examples:
      | width | widest |
      | 375   | 375    |
      | 820   | 748    |
      | 1440  | 825    |
      | 2560  | 825    |

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
