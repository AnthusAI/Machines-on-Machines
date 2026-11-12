Feature: Advertisements are assets the advertiser controls; the site draws only the slot
  An ad is a picture the advertiser supplies, with its own words, type, colors and art drawn inside it. The site never styles what is inside a
  creative. It draws the slot: an "Advertisement" label with the advertiser's name outside the picture, a link marked sponsored, the alt text,
  the unit's size and place, and the containment that keeps a picture inside its column. The site carries standard units (a Band, a
  Half page, a Card, a Story panel, a Pull-quote and an Aside) and no text-only unit, because a bare sentence set in the site's own type is not
  something the advertiser controls and would pass for the article's words. Ads come from `web/ads.json`, never appear on the first screen or in
  the navigation, spine or margin notes, and no page carries more than two. Two house advertisers take turns, Papyrus and Anthus AI Solutions,
  and each ships pictures for every unit, with a Night picture beside each Day one. An advertiser can run several variants; the advertisers
  take turns, and a page picks one of the chosen advertiser's variants.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The home page has one band, after the topic sections and before the Videos
    The Concepts section is the last section of the home page, so the band comes before the sections that end it. (The home page's topic sections may also carry an advertisement card; see home-sections.feature.)
    When I open the page "/"
    Then the page has the ad placements "home-band"
    And "rh-features" comes before "home-band"
    And "home-band" comes before "mom-home-videos"

  Scenario: A section page has a card in the grid and a band at the end
    When I open the page "/field-notes/"
    Then the page has the ad placements "listing-card, listing-end"
    And the advertisement card is the fifth card in the grid

  Scenario: A long article has exactly one ad, inside its words or at the end
    When I open the page "/field-notes/durable-execution-for-agents/"
    Then the page has exactly one article ad placement

  Scenario: A short article has the closing band, because nothing would follow an in-content ad
    When I open the page "/field-notes/a-team-byline-and-no-picture/"
    Then the page has the ad placements "article-end"

  Scenario: A wiki term has a half page in the rail on wide screens and a story panel as wide as the text in the flow below that
    When I open the page "/wiki/durable-execution/"
    Then the page has the ad placements "wiki-rail"
    And the page contains "mom-ad-half-page"
    And the page contains "mom-ad-story"

  Scenario: The newsroom's own pages carry no ads
    When I open the page "/findings/"
    Then the page has no ad placements

  Scenario: An ad is the site's label and slot around the advertiser's picture and nothing the site styled
    When I open the page "/design/"
    Then every advertisement on the page is the site's label and slot around the advertiser's picture, and nothing the site styled
    And every advertisement picture on the page is a file under "/assets/ads/"
    And every advertisement link is marked sponsored

  Scenario: The label names the advertiser outside the picture, so nobody mistakes an ad for the publication's words
    When I open the page "/design/"
    Then the advertisement says it is from "Papyrus" outside its picture
    And the advertisement says it is from "Anthus AI Solutions" outside its picture

  Scenario: The picture's alt text carries the creative's words
    When I open the page "/design/"
    Then the page contains "Papyrus: This publication literally writes itself."
    And the page contains "Anthus AI Solutions: Got a job AI could do? We’ll build it."
    And the page contains "Anthus AI Solutions: Like how this site works? We build things like it."

  Scenario: Each ad has a Night picture beside its Day picture, and the theme shows one
    When I open the page "/design/"
    Then the page contains "mom-ad-day"
    And the page contains "mom-ad-night"
    And the page does not contain "mom-ad-branded"

  Scenario: The text-only inline unit is gone
    When I open the page "/design/"
    Then the page does not contain "mom-ad-inline"
    And the page does not contain "mom-ad-tag"

  Scenario: Every house ad ships its own picture for every unit
    Then every ad in the repository is an advertiser's picture for every unit, in Day and Night, with its own alt text

  Scenario: Two slots on one page show two different advertisers
    When I open the page "/field-notes/"
    Then the ads in the placements "listing-card" and "listing-end" are from different advertisers

  Scenario: Both advertisers appear across the site's pages
    Then the projected pages carry ads from the advertisers "Papyrus" and "Anthus AI Solutions"

  Scenario: An advertiser with more variants does not get more turns
    Then over many pages each advertiser fills about the same share of a slot, however many variants it has
    And over many pages every variant of an advertiser appears

  Scenario: The stylesheet reserves the standard sizes, styles only the slot and never animates an ad
    Then the stylesheet "/assets/mom-components.css" reserves the standard ad sizes

  Scenario: The home page band sits in the page container like the blocks around it
    When I open the page "/"
    Then the page contains "mom-home-ad"

  @browser
  Scenario Outline: The words of an article keep a gutter beside and below the aside ad
    Given the sample of article words with the aside ad on the component gallery
    When I measure the aside ad in a browser <width> pixels wide
    Then no line of the article's words comes within <gutter> pixels of the aside's side or <below> pixels of its foot

    Examples:
      | width | gutter | below |
      | 1440  | 20     | 16    |
      | 820   | 20     | 16    |

  @browser
  Scenario: On a phone the aside ad takes the column's full width, with the words above and below it
    Given the sample of article words with the aside ad on the component gallery
    When I measure the aside ad in a browser 390 pixels wide
    Then the aside is not floated and spans the article's text column

  # A block that sits in the text column on its own fills the whole column: the label's left edge, the picture's left edge and the column's left edge
  # are one line, the picture is exactly as wide as the column, and the label sits directly on top of the picture. Each picture is drawn for the
  # width of its slot (a band for the page-wide slot at three window widths, a column-wide one for an article, a narrow one for a phone), so it
  # is scaled by a few percent at most and never given gutters or centered.
  @browser
  Scenario Outline: An ad in the text column fills the column, with its label directly on top and on its left edge
    Given the fixture article with the <unit> ad in its words
    When I measure its advertisement in a browser <width> pixels wide
    Then the label's left edge, the picture's left edge and the slot's left edge are the same line
    And every advertisement that is not floated starts and ends where its column does and its picture fills it
    And the picture of a card or a floated ad fills its own slot
    And the label sits no more than 12 pixels above its picture

    Examples:
      | unit      | width |
      | band      | 375   |
      | band      | 820   |
      | band      | 1440  |
      | story     | 375   |
      | story     | 820   |
      | story     | 1440  |
      | pullquote | 375   |
      | pullquote | 820   |
      | pullquote | 1440  |
      | aside     | 375   |
      | aside     | 820   |
      | aside     | 1440  |

  @browser
  Scenario Outline: Every ad on a page fills its slot in light and dark, with its label directly on top and on its left edge
    When I measure the advertisements on the page "<route>" in a browser <width> pixels wide in the <theme> theme
    Then the label's left edge, the picture's left edge and the slot's left edge are the same line
    And every advertisement that is not floated starts and ends where its column does and its picture fills it
    And the picture of a card or a floated ad fills its own slot
    And the label sits no more than 12 pixels above its picture

    Examples:
      | route                      | width | theme |
      | /                          | 375   | light |
      | /                          | 1440  | dark  |
      | /field-notes/              | 375   | dark  |
      | /field-notes/              | 820   | light |
      | /field-notes/              | 1440  | light |
      | /wiki/durable-execution/   | 375   | light |
      | /wiki/durable-execution/   | 820   | dark  |
      | /wiki/durable-execution/   | 1440  | dark  |

  Scenario: The build refuses an ad without alt text that says what the creative says
    Then an ad with no alt text, or alt text that is only the advertiser's name, is refused

  Scenario: The build refuses a picture that is not a real file in the ads folder
    Then an ad whose picture is missing, outside the ads folder, or not a picture file is refused

  Scenario: The build refuses an ad with no advertiser or an unsafe link
    Then an ad with no advertiser, or a link that is not https or a path on the site, is refused

  Scenario: The build refuses the inline unit and any unit it does not know
    Then an ad offering the text-only inline unit or any unit the site does not know is refused

  Scenario: The build refuses a stretchy unit that cannot show on a phone
    Then a stretchy unit without its narrow picture is refused
