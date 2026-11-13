Feature: The home page is made of whole sections, and videos, conversations and concepts each have their own
  The home page leads with the lead story and the site title card, and nothing else: conversations used to sit under the site title card in that top
  row, where they did not work, so they are a section of their own near the bottom. After the topic sections and the Top Posts, the home page ends with
  these sections, each with the standard section heading (the title, and a link to all of it): Videos, then Findings, then Conversations, then, last of
  all, Concepts. Videos are a section of their own, no longer a floating card of videos in general. A "Worth Watching" card, which Ryan likes, is tied to
  a few topic sections that a short list in `web/hooks.py` names (HOME_WORTH_WATCHING_SECTIONS); it holds the best one or two videos by the ranking the
  Videos page uses (this week's first, then an editor's stars), and a video appears once on the page. The other topic sections show stories only, and an
  advertisement is one more card in the few topic sections that a second list names (HOME_AD_CARD_SECTIONS). A part with nothing to show is left out.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The top row holds the lead and the site title card, and no conversations
    When I open the page "/"
    Then the home page's top row has the lead and the site title card and no conversations
    And the page does not contain "mom-home-rail"
    And the page does not contain "mom-conversations-rail"

  Scenario: After the topic sections the home page has Videos, Top Posts, Findings, Conversations and, last of all, Concepts
    When I open the page "/"
    Then these home page sections come in this order: "mom-home-videos, mom-top-posts, rh-findings, mom-home-conversations, mom-home-concepts"
    And the Concepts section is the last section of the home page

  Scenario: The home page's own sections have the standard section heading
    When I open the page "/"
    Then the home page section "Videos" has the heading with the link "All videos" to "/videos/"
    And the home page section "Conversations" has the heading with the link "All conversations" to "/conversations/"
    And the home page section "Concepts" has the heading with the link "All concepts" to "/wiki/"

  Scenario: The Videos section shows the best videos of the week as cards, up to the number the page shows
    When I open the page "/"
    Then the Videos section shows at most 6 video cards, each once on the page

  Scenario: Conversations are the site's thread cards, most recent first, no more than six
    When I open the page "/"
    Then the Conversations section shows between 1 and 6 thread cards

  Scenario: Concepts are the index's cards, the most associated first, and end with a link to all of them
    The cards are the ones the concept index draws (the `mom-wiki-grid` of `mom-wiki-card`), ordered the way the index orders them: associations, highest first.
    A concept with no definition is still a card, and the stylesheet gives it its own height.
    When I open the page "/"
    Then the Concepts section is a concept grid with at most 12 cards, the most associated first
    And the page contains "<a class="mom-section-link" href="/wiki/">All concepts</a>"

  Scenario: Twenty concepts show the twelve with the most associations, and a concept with no definition is still a card
    Every third concept has no definition, and stories tag the concepts in different numbers.
    Given a site with 20 concepts
    When the home page's Concepts section is made
    Then it holds 12 concept cards, the most associated first, and the link "All concepts" to "/wiki/"
    And the cards without a definition have no definition text

  Scenario: Without concepts, the Concepts section is left out
    Given a site with 0 concepts
    When the home page's Concepts section is made
    Then the section is not drawn

  Scenario: Worth Watching is not a floating card, and only the named topic sections have one
    When I open the page "/"
    Then no "Worth Watching" card is outside a topic section
    And every "Worth Watching" card is in a topic section that the home page's list names

  Scenario Outline: Worth Watching holds one or two videos, in the sections the list names, in the list's order
    Given a home page with the topic sections "security, agents, science, music, history, art"
    And the engine offers <offered> videos, best first
    When the home page's videos are placed
    Then the "Worth Watching" cards are in "<cards in>" with videos "<card videos>"
    And the Videos section shows videos "<section videos>"
    And every video is on the page once

    Examples:
      | offered | cards in             | card videos          | section videos            |
      | 14      | agents, music, history | 1 2, 3 4, 5 6      | 7 8 9 10 11 12            |
      | 7       | agents, music, history | 1 2, 3 4, 5 6      | 7                         |
      | 5       | agents, music, history | 1 2, 3 4, 5        | none                      |
      | 1       | agents                 | 1                  | none                      |

  Scenario: A listed section that the page does not have gives its videos to the next one
    Given a home page with the topic sections "security, music, art"
    And the engine offers 8 videos, best first
    When the home page's videos are placed
    Then the "Worth Watching" cards are in "music" with videos "1 2"
    And the Videos section shows videos "3 4 5 6 7 8"

  Scenario: With no videos, the page has no Worth Watching card and no Videos section
    Given a home page with the topic sections "security, agents, music"
    And the engine offers 0 videos, best first
    When the home page's videos are placed
    Then the page has no "Worth Watching" card and no Videos section

  Scenario: An advertisement is one more card only in the listed sections that have two cards
    Given a home page with the topic sections "security:2, science:2, agents:3, art:2"
    When the home page's advertisement cards are placed
    Then an advertisement card is in "science, art" and nowhere else, and each of those sections has 3 columns

  Scenario: A listed section that has three cards gets no advertisement
    Given a home page with the topic sections "science:3"
    When the home page's advertisement cards are placed
    Then no advertisement card is on the page

  Scenario: Without a card advertisement, no section gets one
    Given a home page with the topic sections "science:2, art:2"
    And the site has no advertisements
    When the home page's advertisement cards are placed
    Then no advertisement card is on the page

  Scenario: Conversations with nothing to show leave the section out
    Given a home page with the topic sections "security"
    When the home page's conversations are made from a page with no conversations
    Then the section is not drawn

  Scenario: The stylesheet draws the Worth Watching card flat across its section's columns, with no borders
    Then the stylesheet "/css/site-theme.css" draws the Worth Watching card as a flat panel across the columns of its section

  # On a wide display the topic sections sit in two columns. Sections differ in height (a Worth Watching panel, a solo story, an ad card), so rows of two would
  # leave a blank hole under the shorter one. The columns are filled by the browser and balanced, a section never splits, and the next section follows at once.
  Scenario: On wide displays the topic sections fill two balanced columns instead of rows that leave blank holes
    Then the stylesheet "/css/site-theme.css" flows the topic sections into two balanced columns and never splits a section

  Scenario Outline: The footer has two variants, chosen by the kind of page
    An index page is wide, so its footer has the page margins and width of the index pages' content and fills the page where the content fills it. A single-column content page has the footer centred under its column, as before. Every page that is not a single-column content page, including a special page nobody named, has the index footer. The masthead is the same everywhere.
    When I open the page "<route>"
    Then the page has the <variant> footer and only that one

    Examples:
      | route                          | variant |
      | /                              | index   |
      | /security/                     | index   |
      | /articles/                     | index   |
      | /posts/                        | index   |
      | /wiki/                         | index   |
      | /findings/                     | index   |
      | /videos/                       | index   |
      | /conversations/                | index   |
      | /about/                        | index   |
      | /corrections/                  | index   |
      | /articles/synthetic-law-policy-article-1/ | content |
      | /posts/synthetic-gaming-post-1/ | content |
      | /wiki/durable-execution/       | content |

  Scenario: Footer variants by page kind: an article, a post and a wiki term get the content footer, and an unlisted kind gets the index footer
    Then the footer variant of a page of kind "item" is "content"
    And the footer variant of a page of kind "listing" is "index"
    And the footer variant of a page of kind "tag" is "index"
    And the footer variant of a page of kind "custom" is "index"
    And the footer variant of a page of kind "some-new-special-page" is "index"

  Scenario: The stylesheet gives the index footer the index pages' width and the content footer the content column, with no borders
    Then the stylesheet "/css/site-theme.css" gives the index footer the width of the index pages and the content footer the article column

  # The sections of the wide home page are put into two columns by their height in rows of cards, in rank order, each into the shorter column. A column that is still
  # a whole row short takes one more row of its best-ranked section's own next-ranked stories (the page asks the engine for more than a section shows, and the rest wait
  # in a reserve). A section with an advertisement card, or with no whole row in reserve, does not grow. Nothing of the reserve is left on the page.
  Scenario: Each section goes to the shorter column in rank order, and the page is written column after column
    Given the featured sections "a:3:0, b:3:0, c:3:0, d:2:1"
    When the featured sections are put into columns
    Then the sections are written in the order "a, c, b, d" and "b" is where the second column starts
    And every section still carries its rank so a narrow window shows them in rank order

  Scenario: A column a whole row short takes a row of the next-ranked stories of its best section
    Given the featured sections "a:3:3, b:3:0, c:3:0, d:2:1"
    When the featured sections are put into columns
    Then the section "a" shows 6 stories, the ones after its first 3 in ranked order
    And no section holds a reserve of stories on the page

  Scenario: A section with no whole row in reserve does not grow
    Given the featured sections "a:3:2, b:3:0, c:3:0, d:2:1"
    When the featured sections are put into columns
    Then every section shows the stories it started with
    And no section holds a reserve of stories on the page
