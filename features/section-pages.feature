Feature: Every newsroom section has a page
  Each section the newsroom files stories under (Privacy & Security, AI Safety, Agents, Science, History, Gaming, Art, Law & Policy, Full Self
  Driving and Music) has a page at its own address, such as /security/. All ten come from one template and one list, so a change to the
  layout is made once. A section page leads with the section's articles, then shows its videos; beside them, in a narrow side column, are the
  section's conversations and, above them, its posts, drawn small as one line each so a post is never a large card. A block with nothing in it
  is not drawn at all. Articles are ordered the way the whole site orders them: this week's first, then an editor's stars, newest within a tie.
  The page says how many articles, posts and conversations the section has.

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

  Scenario: The page says what the section is and how much it holds
    When I open the page "/security/"
    Then "/security/" has the shared page header titled "Privacy &amp; Security"
    And the page contains "How machines are attacked, defended and watched, and who gets to know."
    And the section page counts "4 articles · 4 posts · 2 conversations"

  Scenario: The articles lead, best first, with the lead article drawn large
    When I open the page "/security/"
    Then the section page's lead article is "Synthetic Security article 1"
    And "Synthetic Security article 1" comes before "Synthetic Security article 3"
    And "Synthetic Security article 3" comes before "Synthetic Security article 5"
    And the section page shows only articles of its own section

  Scenario: The posts are one line each, with no picture, in the side column
    When I open the page "/security/"
    Then the side column lists the posts "Synthetic Security post 2, Synthetic Security post 4, Synthetic Security post 6, Synthetic Security post 8" as lines
    And no post on the page is drawn as a card

  Scenario: The side column lists the section's conversations as lines
    When I open the page "/security/"
    Then the side column lists the conversations "Who audits the audit log?, Is a leaked prompt a breach?" as lines
    And the page does not contain "What would count as a replication?"
    And the page does not contain "Is a judge that shares training data still a judge?"

  Scenario: The videos of the section follow the articles and a longer list says More videos
    When I open the page "/security/"
    Then the section page shows 4 videos, all from its own section
    And "Videos</h2>" comes before "Posts</h2>"
    And the section page ends its videos with the link "More videos…" to "/videos/"

  Scenario: A section with one video shows it and has no More videos link
    When I open the page "/science/"
    Then the section page shows 1 videos, all from its own section
    And the section page has no "More videos…" link

  Scenario: A section with more articles than fit on the page links to the rest
    Then the page "/security/articles/" was projected
    And the page "/security/posts/" was projected

  Scenario: The More links of a section page lead to its full lists only when there are more
    When I open the page "/science/"
    Then the page does not contain "More articles…"
    And the page does not contain "More posts…"

  Scenario: A block with nothing in it is not drawn, and says nothing about being empty
    When I open the page "/gaming/"
    Then the section page has no videos block and no conversations block
    And the page does not contain "none yet"
    And the page does not contain "No videos"

  Scenario: A section nobody has written for yet still has a page, with no blocks
    When I open the page "/music/"
    Then the section page has no articles block, no posts block, no videos block and no conversations block

  Scenario: On a narrow window the blocks stack as articles, videos, conversations, then posts
    When I open the page "/security/"
    Then the section page's blocks come in this order in the markup
      | block         |
      | articles      |
      | videos        |
      | conversations |
      | posts         |

  Scenario: On a wide window the posts come first in the side column, which has a fixed width
    Then the stylesheet "/css/site-theme.css" puts the section page's posts above its conversations in the side column
    And the stylesheet "/css/site-theme.css" gives the section page's side column one page column, which stays one column as the page gains columns

  Scenario: The section pages have Markdown twins and are in the sitemap
    Then the file "sitemap.xml" contains "/security/"
    And the file "security/index.md" contains "Synthetic Security article 1"

  Scenario: An article's section label leads to the section's page
    When I open the page "/articles/synthetic-security-article-1/"
    Then the page contains "<a class="mom-kicker" href="/security/">Privacy &amp; Security</a>"
