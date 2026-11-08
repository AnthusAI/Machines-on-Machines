Feature: The Posts page shows the posts, grouped by section
  Posts is where the posts are, laid out exactly like the Articles page: grouped by section, the section updated most recently
  first, the newest post first within a section, a featured post only in the first section and a wide post in the next two, and
  plain grids below. No article is ever listed here, and neither are findings, videos, conversations or wiki pages. Every post
  keeps its own address, and the page keeps its place in the navigation, the feeds and the sitemap.

  Background:
    Given the Machines on Machines site is projected from the fixtures
    When I open the page "/posts/"

  Scenario: Posts are on the page and articles are not
    Then the page contains "Synthetic Security post 2"
    And the page contains "Synthetic Gaming post 1"
    And the page does not contain "Synthetic Security article 1"
    And the page does not contain "Synthetic Law Policy article 1"
    And the page does not contain "/articles/synthetic"

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
      | Science            |
      | Gaming             |
      | Robotics           |

  Scenario: Posts within a section are newest first
    Then in the section "Privacy & Security" "Synthetic Security post 2" comes before "Synthetic Security post 4"
    And in the section "Privacy & Security" "Synthetic Security post 4" comes before "Synthetic Security post 6"

  Scenario: Only the first three sections have a featured post
    Then the section "Privacy & Security" has the "feature" layout
    And the section "Law & Policy" has the "wide" layout
    And the section "Science" has the "wide" layout
    And the section "Gaming" has the "plain" layout
    And the section "Robotics" has the "plain" layout

  Scenario: Later sections are plain grids with no featured card
    Then the section "Gaming" has no featured card and no card across two columns

  Scenario: No section is hidden, and a section with more posts than shown says how many it has
    Then the page has 5 sections
    And the section "Gaming" says it has "7 stories"
    And the section "Science" does not say how many stories it has

  Scenario: A section's name links to its page, and a section with more than one post ends with a More link
    Then the section "Gaming" links to "/gaming/" and ends with "More Gaming…"
    And the section "Privacy & Security" links to "/security/" and ends with "More Privacy & Security…"

  Scenario: A section that has no page gets no link of any kind
    Then the section "Robotics" has no link to a section page

  Scenario: Every row of a section is full
    Then every row on the page is a whole row of one, two or three cards

  Scenario: The page keeps its lead, its place in the navigation and one address for the whole list
    Then the page contains "Quick pointers to the latest in information systems."
    And the navigation links Posts to "/posts/"
    And the page "/posts/page/2/" was not projected

  Scenario: Posts keep their own pages, feed entries and sitemap entries
    Then the file "sitemap.xml" contains "/posts/synthetic-security-post-2/"
    And the file "sitemap.xml" contains "/posts/"
    And the file "feed.xml" contains "/posts/synthetic-security-post-2/"
    And the file "atom.xml" contains "/posts/synthetic-security-post-2/"
    And the file "posts/index.md" contains "Synthetic Security post 2"
    When I open the page "/posts/synthetic-security-post-2/"
    Then the page contains "Synthetic Security post 2"
