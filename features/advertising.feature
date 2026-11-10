Feature: Advertisements sit between things, never on top of them
  The site carries standard advertising units: a Band, a Rectangle, a Half page, a Card and a Story panel.
  Ads come from `web/ads.json`, always say "Advertisement" in words, never appear on the first screen or in the
  navigation, spine or margin notes, and no page carries more than two. Two house advertisers take turns: Papyrus, the
  publishing system behind the site, and Anthus AI Solutions, the company that makes it. Each wears its own brand. An advertiser
  can run several variants of its ad; the advertisers take turns, and a page picks one of the chosen advertiser's variants.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: The home page has one band, at the end after the findings
    When I open the page "/"
    Then the page has the ad placements "home-band"
    And "rh-findings" comes before "home-band"

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

  Scenario: A wiki term has a half page in the rail on wide screens and a rectangle in the flow below that
    When I open the page "/wiki/durable-execution/"
    Then the page has the ad placements "wiki-rail"
    And the page contains "mom-ad-half-page"
    And the page contains "mom-ad-rectangle"

  Scenario: The newsroom's own pages carry no ads
    When I open the page "/findings/"
    Then the page has no ad placements

  Scenario: The Papyrus house ad says who it is from and where it leads
    When I open the page "/design/"
    Then the page contains "Advertisement"
    And the page contains "This publication <em>literally</em> writes itself."
    And the page contains "Almost. Agents find, rank and draft every story here"
    And the page contains "See how Papyrus works"
    And every advertisement link is marked sponsored

  Scenario: The Papyrus ad wears Papyrus's plant, type and colors, not the site's shapes
    When I open the page "/design/"
    Then the page contains "mom-ad-art-papyrus-sun"
    And the page contains "mom-ad-brand-name"
    And the page contains "mom-ad-mark-papyrus-plant"
    And the page contains "mom-ad-face-serif"
    And the page does not contain "mom-ad-disc"

  Scenario: Anthus AI Solutions is the second advertiser, with three variants in its own pixel lockup and type
    When I open the page "/design/"
    Then the page contains "Advertisement</b> · Anthus AI Solutions"
    And the page contains "This site is brought to you by Anthus AI Solutions."
    And the page contains "Got a job AI could do? We’ll build it."
    And the page contains "Like how this site works? We build things like it."
    And the page contains "mom-ad-art-anthus-pixels"
    And the page contains "mom-ad-wordmark-anthus-lockup"
    And the page contains "mom-ad-face-pixel"

  Scenario: Two slots on one page show two different advertisers
    When I open the page "/field-notes/"
    Then the ads in the placements "listing-card" and "listing-end" are from different advertisers

  Scenario: Both advertisers appear across the site's pages
    Then the projected pages carry ads from the advertisers "Papyrus" and "Anthus AI Solutions"

  Scenario: An advertiser with more variants does not get more turns
    Then over many pages each advertiser fills about the same share of a slot, however many variants it has
    And over many pages every variant of an advertiser appears

  Scenario: The stylesheet reserves the standard sizes and never animates an ad
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

  Scenario: The build refuses an advertiser's brand it cannot draw readably
    Then an ad whose brand accent has contrast below 4.5 on its ground is refused
    And an ad whose brand names an unknown type face is refused
    And an ad whose brand names an unknown wordmark or art is refused
    And a headline's length counts the words a reader sees, not its emphasis marks
