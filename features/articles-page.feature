Feature: The Articles page shows the articles, grouped by section
  Articles is where the articles are. Posts are a different kind of story with their own page, so no post is ever listed here, and
  neither are findings, videos, conversations or wiki pages. Articles are grouped by section, and the section that was updated
  most recently comes first. The sections near the top make more of their first article, the way the home page does, and the
  sections further down thin out into plain grids. No section is left off, and every row is full at any width. The Posts page
  works the same way (see posts-page.feature).

  Background:
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/articles/"

  Scenario: Articles are on the page and posts are not
    Then the page contains "Synthetic Security article 1"
    And the page contains "Synthetic Law Policy article 3"
    And the page does not contain "Synthetic Security post 2"
    And the page does not contain "Synthetic Law Policy post 2"
    And the page does not contain "Synthetic Gaming post 1"
    And the page does not contain "/posts/synthetic"

  Scenario: Findings, videos, conversations and concepts never appear
    Then the page does not contain "mom-reference-card"
    And the page does not contain "Fixture video number 1: talks on machines"
    And the page does not contain "mom-thread-card"
    And the page does not contain "mom-wiki-card"

  Scenario: The section updated most recently comes first
    Then the page lists its sections in this order
      | section            |
      | Privacy & Security |
      | Law & Policy       |
      | Math & Science            |
      | Field Notes        |
      | Robotics           |

  Scenario: A section with only posts has no place on the Articles page
    Then the page has no section named "Gaming"

  Scenario: Articles within a section are newest first
    Then in the section "Privacy & Security" "Synthetic Security article 1" comes before "Synthetic Security article 3"
    And in the section "Privacy & Security" "Synthetic Security article 3" comes before "Synthetic Security article 5"

  Scenario: Only the first three sections have a featured story
    Then the section "Privacy & Security" has the "feature" layout
    And the section "Law & Policy" has the "wide" layout
    And the section "Math & Science" has the "wide" layout
    And the section "Field Notes" has the "plain" layout
    And the section "Robotics" has the "plain" layout

  Scenario: The first section features its newest article beside its picture
    Then the section "Privacy & Security" has one feature card drawn beside its picture
    And the section "Law & Policy" has one card across two columns

  Scenario: Later sections are plain grids with no featured card
    Then the section "Field Notes" has no featured card and no card across two columns

  Scenario: No section is hidden, and a section with more articles than shown says how many it has
    Then the page has 5 sections
    And the section "Field Notes" says it has "13 stories"
    And the section "Math & Science" does not say how many stories it has

  Scenario: A section's name links to its page, and a section with more than one article ends with a More link
    Then the section "Privacy & Security" links to "/security/" and ends with "More Privacy & Security…"
    And the section "Law & Policy" links to "/law-policy/" and ends with "More Law & Policy…"
    And the section "Field Notes" links to "/field-notes/" and ends with "More Field Notes…"

  Scenario: A section with one article links its name but has no More link
    Then the section "Math & Science" links to "/science/" and has no More link

  Scenario: A section that has no page gets no link of any kind
    Then the section "Robotics" has no link to a section page

  Scenario: Every row of a section is full
    Then every row on the page is a whole row of one, two or three cards

  Scenario: The page header says it is the articles
    Then the page contains "Every article from Machines on Machines, by section."
    And the page contains "Articles</h1>"

  Scenario: The navigation has Articles and Posts and no Stories
    Then the navigation links Articles to "/articles/"
    And the navigation lists "Articles, Posts, Findings, Videos, Conversations, Concepts" in that order
    And the page does not contain ">Stories</a>"

  Scenario: The Articles page has one address for the whole list, in the sitemap, the feeds and as Markdown
    Then the page "/articles/page/2/" was not projected
    And the file "sitemap.xml" contains "/articles/"
    And the file "articles/index.md" contains "Synthetic Security article 1"

  Scenario: The old Stories address sends readers to Articles and stays out of the sitemap
    When I open the page "/stories/"
    Then the page redirects to "/articles/"
    And the page names "/articles/" as its canonical address
    And the page contains "Go to Articles"
    And the file "sitemap.xml" does not contain "/stories/"

  Scenario: On a very wide window a section's rows sit two across so cards stay the size they are on a laptop
    Articles and Posts share this layout. From 1840px a section's rows of two and three cards sit side by side, as the home page's featured sections do, while a row of one stays full width.
    Then the stylesheet "css/site-theme.css" lays a section's rows two across on a very wide window
