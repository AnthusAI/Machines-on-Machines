Feature: An article page fits its content
  A reading page puts the story first. The spine down the left edge always reads "Machines on Machines",
  because on an article it is the only place the site's name shows, and a story with no picture gets a slim band of brand art rather than a giant block.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The spine's name fits its column
    When I open the page "/field-notes/steer-a-story/"
    Then the spine tells the stylesheet its name is 20 characters long
    And the stylesheet "/css/site-theme.css" sizes the spine's section name to fit the room it has

  Scenario Outline: The spine's name links to the home page from every page
    When I open the page "<page>"
    Then the spine's name links to "/"

    Examples:
      | page                                  |
      | /                                     |
      | /articles/                            |

  Scenario Outline: The spine is on every page
    When I open the page "<page>"
    Then the page has a spine after its masthead that reads "<subject>"

    Examples:
      | page                                  | subject  |
      | /                                     | Machines |
      | /articles/                            | Machines |
      | /conversations/                       | Machines |
      | /about/                               | Machines |
      | /wiki/                                | Machines |
      | /wiki/benchmarks/                     | Machines |
      | /field-notes/                         | Machines |
      | /field-notes/a-team-byline-and-no-picture/ | Machines |

  Scenario: In a narrow or short window the spine goes away and the name and home icon lead the top bar
    When I open the page "/articles/"
    Then the page contains "mom-brand-pill"
    And the stylesheet "/css/site-theme.css" shows the spine only when the window has room for it

  Scenario: An article with no image gets a slim band of art
    When I open the page "/field-notes/a-team-byline-and-no-picture/"
    Then the article's picture is a slim band of placeholder art

  Scenario: An article whose body opens with a figure gets no band
    Then a body that opens with a figure has no separate picture above it
    And a body with no figure at the top still gets the band

  Scenario: An article that sets a card image and opens with a figure shows the picture once
    Then a body that opens with a figure has no separate picture above it, even with a card image

  Scenario: A picture the markup wraps in a paragraph still counts as the body's opening picture
    The body renderer sometimes puts the opening figure inside a paragraph. The article then shows that picture once, with no second cover picture above it.
    Then a body whose opening figure sits inside a paragraph has no separate picture above it, even with a stored card image

  Scenario: An article is one centered column
    Then the stylesheet "/css/site-theme.css" centers everything in an article in one reading column

  Scenario: A story's concepts are hashtag-styled links above the References, the most used first
    The concepts a story is tagged with, and that have a public page, are links written as hashtags. There is no other list of hashtags: a tag with no concept page is not shown.
    Then the concepts of a story are hashtag links, the most used first, and a tag with no concept page is not shown

  Scenario: A story with no concepts has no concepts row and no unlinked hashtags
    When I open the page "/field-notes/a-subtitle-and-a-separate-blurb/"
    Then the page does not contain "mom-concepts"
    And the page does not contain "<span class="mom-hashtag">"

  Scenario: See also holds only articles and Posts only posts, each only when there is something to show
    Then the article rail has See also with article cards and Posts with compact rows, never mixed, and no rail when empty

  Scenario: The rail sits beside the text on a wide window and under it on a narrow one
    Then the stylesheet "/css/site-theme.css" puts the article rail beside the text from 825pt and keeps the footer under the text column

  Scenario: The References heading appears only over references
    Then a body with citations gets a References heading after the concepts
    And a body with no citations gets no References heading

  Scenario: An article offers its Markdown and a way to share either version
    When I open the page "/field-notes/a-subtitle-and-a-separate-blurb/"
    Then the page contains "aria-label="View as Markdown""
    And the page contains "href="/field-notes/a-subtitle-and-a-separate-blurb/index.md""
    And the page contains "Share the web page"
    And the page contains "Share the Markdown"
    And the page contains "https://x.com/intent/post?"
    And the page contains "https://www.reddit.com/submit?"

  Scenario: A callout in an article reads as a contained block
    Then the stylesheet "/css/site-theme.css" draws a callout as a filled, rounded panel

  Scenario: A pull quote carries no caption
    When I open the page "/field-notes/the-agents-are-writing-the-benchmarks-now/"
    Then the page contains "mom-pull-quote-text"
    And the page does not contain "chosen by the editor"

  Scenario: Tables show a header and alternating row tones with no lines
    Then the stylesheet "/css/site-theme.css" styles article tables with a header row and alternating row tones and no borders

  Scenario: Long URLs in the references list wrap instead of overflowing
    Then the stylesheet "/css/site-theme.css" wraps long URLs in the references list

  Scenario: Only the short lead headline is set in capitals
    Then the stylesheet "/css/site-theme.css" sets card headlines, article headlines and subheads in sentence case

  Scenario: A wide display gains columns and the spine
    Then the stylesheet "/css/site-theme.css" adds a column for each step up in window width

  Scenario: The home icon sits at the top of the spine, or leads the navigation when there is no spine
    When I open the page "/posts/"
    Then the navigation starts with the site name, then a labelled home link with the Lucide house icon
    And the spine's home link is the Lucide house icon
    And the stylesheet "/css/site-theme.css" hides the name and home pills exactly when the spine shows

  Scenario: A tablet in portrait sets the home card beside the latest posts
    Then the stylesheet "/css/site-theme.css" sets the home card and latest posts side by side on a tablet

  Scenario: Listing and index pages share one header with the site title card
    Then "/posts/" has the shared page header titled "Posts"
    And "/findings/" has the shared page header titled "Findings"
    And "/wiki/" has the shared page header titled "Concepts"
    And "/videos/" has the shared page header titled "Videos"
    And "/wiki/" has the same site title card as the home page
    And the home page places the card with the same slot as every other page
    And "/posts/" leads with "Quick pointers to the latest in information systems."

  Scenario: The site title card busts out of its place
    Then the stylesheet "/css/site-theme.css" lets the card bust out, up and right to the spine, with three columns
    And the stylesheet "/css/site-theme.css" keeps the first grid's last cell free for the card in the page header
    And the stylesheet "/css/site-theme.css" hides the header's card on a phone

  Scenario: A site title card in a page header keeps its width
    Then the stylesheet "/css/site-theme.css" gives a header's site title card a width

  Scenario: On a short page the footer reaches the bottom of the window
    Then the stylesheet "/css/site-theme.css" stretches the main content to fill the window

  Scenario Outline: Every page offers its Markdown and sharing with the same icons
    When I open the page "<page>"
    Then the page contains "aria-label="View as Markdown""
    And the page contains "aria-label="Post on X""
    And the page contains "aria-label="Post on Reddit""
    And the page contains "aria-label="Share""
    And the page contains "href="<markdown>""
    And the page does not contain "markus-page-actions"

    Examples:
      | page                                      | markdown                                      |
      | /                                         | /index.md                                     |
      | /conversations/                           | /conversations/index.md                       |
      | /findings/                                    | /findings/index.md                                |
      | /articles/                                | /articles/index.md                            |
      | /about/                                   | /about/index.md                               |
      | /field-notes/                             | /field-notes/index.md                         |
      | /wiki/                                    | /wiki/index.md                                |
      | /wiki/benchmarks/                         | /wiki/benchmarks/index.md                     |
      | /field-notes/a-subtitle-and-a-separate-blurb/ | /field-notes/a-subtitle-and-a-separate-blurb/index.md |

  Scenario: The spine is the brand and nothing else
    When I open the page "/field-notes/a-team-byline-and-no-picture/"
    Then the spine shows no reading progress
    And the stylesheet "/css/site-theme.css" fills the window with the spine and keeps the masthead and footer beside it

  Scenario: The page behind the content is the brand color
    Then the stylesheet "/css/site-theme.css" paints the canvas in the brand color
    And the browser chrome is told to use the brand color in Day and Night

  Scenario Outline: The spine and the label over the headline name the Story's topic, not the heading its address sits under
    Given an article published under "/articles/" with the section "<section>"
    Then its topic reads "<topic>"

    Examples:
      | section       | topic              |
      | security      | Privacy & Security |
      | law-policy    | Law & Policy       |
      | formal-proofs | Formal Proofs      |

  Scenario: An article with no section is about machines and has no topic label
    Given an article published under "/articles/" with no section
    Then it has no topic label

  Scenario: The list of a Story type is not a topic
    Then the list of articles is titled "Machines on Machines"

  Scenario: The subtitle goes under the headline and the blurb goes on index pages
    When I open the page "/field-notes/a-subtitle-and-a-separate-blurb/"
    Then the line under the headline is "The line a reader sees under this headline."
    And the page does not contain "The paragraph that leads a reader in from an index page." in its article
    When I open the page "/field-notes/"
    Then the page contains "The paragraph that leads a reader in from an index page."

  Scenario: An article with an image keeps its wide picture
    When I open the page "/field-notes/the-agents-are-writing-the-benchmarks-now/"
    Then the article's picture is the wide image

  Scenario: The retired seed sections are not in the navigation and their addresses are not served
    When I open the page "/"
    Then the page does not contain "Newsroom How-To"
    And the page does not contain "href=\"/papyrus/\""
    And the page does not contain "href=\"/how-to/\""
    And the site does not serve "/papyrus/"
    And the site does not serve "/how-to/"

  Scenario: The spine stands on the left and its name reads from the bottom up
    Then the stylesheet "/css/site-theme.css" fills the window with the spine and keeps the masthead and footer beside it
    And the stylesheet "/css/site-theme.css" turns the spine's name to read from the bottom up

  Scenario: A link preview's picture is an address the site serves
    A story's stored picture can be written as media/assets/<slug>/<file>, and a relative picture can carry ../ segments. The page's og:image and twitter:image would then point at an address that serves nothing (404 or 400), and the shared link showed no picture. The site corrects its own addresses to /assets/ and leaves a picture hosted elsewhere alone.
    Then the link preview picture "https://machines-on-machines.anth.us/media/assets/a-story/cover.png" is served from "https://machines-on-machines.anth.us/assets/a-story/cover.png"
    And the link preview picture "https://machines-on-machines.anth.us/../../assets/responsive/assets/a-post/cover-1024.png" is served from "https://machines-on-machines.anth.us/assets/responsive/assets/a-post/cover-1024.png"
    And the link preview picture "https://machines-on-machines.anth.us/assets/a-story/cover.png" is served from "https://machines-on-machines.anth.us/assets/a-story/cover.png"
    And the link preview picture "https://upload.wikimedia.org/wikipedia/commons/b/ba/Norbert_Wiener.webp" is served from "https://upload.wikimedia.org/wikipedia/commons/b/ba/Norbert_Wiener.webp"

  Scenario: The picture's dark-mode style inside the opening paragraph does not bring the cover picture back
    Papyrus places the style that swaps a picture's light and dark versions inside the paragraph before the first figure. That body still opens with its picture, so the article shows it once.
    Then a body whose style and figure both sit inside the opening paragraph has no separate picture above it, even with a stored card image

  Scenario: The footer of an article lines up with the article's text
    An article is a narrow centred column. Its footer is held to the same column so the footer's first letter sits under the article's first letter instead of at the edge of the wider page footer.
    Then the stylesheet "css/site-theme.css" holds an article page's footer to the article's text column

  Scenario: A citation number is a superscript right against the claim
    A citation number is small, lifted above the line and pulled back over the space before it, so it reads as a footnote mark and not a full-size underlined digit.
    Then the stylesheet "css/site-theme.css" draws a citation number as a superscript pulled against the text

  Scenario: Outside links in the References carry the external-link icon and open in a new tab, ours do not
    The site opts in to the icon (citations externalIcon). A cited source we have a post for links to our own page with no icon; every other source is an outside link marked with the icon.
    Then the site settings turn on the external-link icon for citations and keep outside links opening in a new tab

  Scenario: Related findings are quiet text tiles that open in a new tab, and only appear when there are some
    A related Reference is somebody else's page, so it is a quiet tile with the site, the headline and a short summary when there is one, the external-link icon, and a new tab. It is the third kind of related content beside the article cards and the post rows.
    Then the article rail shows Related findings as text tiles with the external-link icon, and none when there are none

  Scenario: Citation numbers that run together keep a space between them
    A claim cited by several sources ends in a run of small raised numbers, such as 3 4 5 1. Each number used to be pulled back over the space before it, so a run read as one number, "3451". Numbers that follow another number keep the space between them, at the size of the superscript. A single number, and the first of a run, are still pulled against the claim.
    Then the stylesheet "css/site-theme.css" keeps the space between citation numbers that follow each other

  @browser
  Scenario Outline: A run of citation numbers has a gap and a single number does not change
    When I measure highlights at <width> pixels in "<theme>" mode
    Then every citation number in a run is separated from the last by a gap of a few pixels
    And a single citation number, and the first of a run, are still pulled against the text

    Examples:
      | width | theme |
      | 1440  | light |
      | 375   | dark  |
