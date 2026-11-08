Feature: Every newsroom section has a page
  Each section the newsroom files stories under (Privacy & Security, AI Safety, Agents, Science, History, Gaming, Art, Law & Policy, Full Self
  Driving and Music) has a page at its own address, such as /security/. All ten come from one template and one list, so a change to the
  layout is made once. A section page is the home page for one section: the same top row (the lead article large on the left, the site title card on the
  right with the section's conversations beside it), then the rest of the section's articles as the site's story cards in whole rows, then the
  section's videos in the Worth Watching panel, then a band and the section's posts as a mosaic of small picture cards. A post is always smaller
  than an article and is never a lead. A block with nothing in it is not drawn at all. Articles are ordered the way the whole site orders them:
  this week's first, then an editor's stars, newest within a tie. The page says how many articles, posts and conversations the section has.
  On wide windows the page gains columns of the same width, so no card grows with the window and no row leaves a gap.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario Outline: Each section has a page at its own address
    Then the page "<route>" was projected

    Examples:
      | route              |
      | /security/         |
      | /ai-safety/        |
      | /agents/           |
      | /science/          |
      | /history/          |
      | /gaming/           |
      | /art/              |
      | /law-policy/       |
      | /full-self-driving/ |
      | /music/            |

  Scenario: The section pages are all made from one template and one list
    Then the generated section pages are up to date with web/sections.json and the template

  Scenario: The page is titled like a home page block, and counts what the section holds
    When I open the page "/security/"
    Then the section page is titled "Privacy &amp; Security" with a small label heading like the home page's
    And the section page counts "14 articles · 13 posts · 2 conversations"
    And the section page says "How machines are attacked, defended and watched, and who gets to know." under the site title card

  Scenario: The top row is the home page's: the lead, then the site title card with the conversations rail
    When I open the page "/security/"
    Then the section page has the home page's top row: the lead article, then the site title card with the conversations rail beside it
    And the section page's lead article is "Synthetic Security article 1"

  Scenario: The rest of the articles are the site's story cards, best first, all from this section
    When I open the page "/security/"
    Then "Synthetic Security article 3" comes before "Synthetic Security article 5"
    And "Synthetic Security article 5" comes before "Synthetic Security article 7"
    And the section page shows only articles of its own section

  Scenario: The rail lists the section's conversations as the home page's rail does
    When I open the page "/security/"
    Then the rail lists the conversations "Who audits the audit log?, Is a leaked prompt a breach?" as lines
    And the page does not contain "What would count as a replication?"
    And the page does not contain "Is a judge that shares training data still a judge?"

  Scenario: The videos are the home page's Worth Watching panel, and a longer list says More videos
    When I open the page "/security/"
    Then the section page shows 6 videos in the Worth Watching panel, all from its own section
    And the section page ends its videos with the link "More videos…" to "/security/videos/"

  Scenario: A section with one video shows it and has no More videos link
    When I open the page "/science/"
    Then the section page shows 1 videos in the Worth Watching panel, all from its own section
    And the section page has no "More videos…" link

  Scenario: The posts are small picture cards in a mosaic under the videos, never large cards or lines
    When I open the page "/security/"
    Then the section page shows 12 posts as picture cards in the mosaic, each a small card with no blurb
    And no post on the page is drawn as a large card or as a line
    And the page contains ">More posts…</a>"
    And "Worth Watching" comes before ">Posts</h2>"

  Scenario: A section with more articles or posts than fit links to the rest
    Then the page "/security/articles/" was projected
    And the page "/security/posts/" was projected
    When I open the page "/security/"
    Then the page contains ">More articles…</a>"

  Scenario: A section with few articles and posts has no More links to the full lists
    When I open the page "/science/"
    Then the page does not contain "More articles…"
    And the page does not contain "More posts…"

  Scenario: A block with nothing in it is not drawn, and says nothing about being empty
    When I open the page "/gaming/"
    Then the section page has no videos panel and no conversations
    And the page does not contain "none yet"
    And the page does not contain "No videos"

  Scenario: A section nobody has written for yet still has a page, with nothing in it
    When I open the page "/music/"
    Then the section page has no articles, no videos, no posts and no conversations

  Scenario: The blocks come in the home page's order, which is also the order they stack in on a narrow window
    When I open the page "/security/"
    Then the section page's blocks come in this order in the markup
      | block         |
      | lead          |
      | card          |
      | conversations |
      | articles      |
      | videos        |
      | posts         |

  @browser
  Scenario Outline: The conversations rail and the sentence under it never touch the site title card
    When I measure the page "/security/" in a browser <width> pixels wide
    Then no element of the conversations rail or the sentence under it touches the site title card

    Examples:
      | width |
      | 1024  |
      | 1440  |
      | 1920  |
      | 2200  |
      | 2560  |

  @browser
  Scenario Outline: On wide windows the page gains columns and the cards keep their size, in whole rows
    When I measure the page "/security/" in a browser <width> pixels wide
    Then every article, video and post card is a laptop-sized card and the lead's picture is not enlarged with the window
    And every row of article, video and post cards is a whole row and nothing leaves a blank gap to the right

    Examples:
      | width |
      | 1024  |
      | 1440  |
      | 1920  |
      | 2200  |
      | 2560  |

  Scenario: Wide windows show only whole rows of cards, and a block with nothing in it is hidden
    Then the stylesheet "/css/site-theme.css" shows only whole rows of cards on wide windows, and hides a block with nothing in it

  Scenario: The section pages have Markdown twins and are in the sitemap
    Then the file "sitemap.xml" contains "/security/"
    And the file "security/index.md" contains "Synthetic Security article 1"

  Scenario: An article's section label leads to the section's page
    When I open the page "/articles/synthetic-security-article-1/"
    Then the page contains "<a class="mom-kicker" href="/security/">Privacy &amp; Security</a>"
