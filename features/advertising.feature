Feature: Advertisements sit between things, never on top of them
  The site carries standard advertising units: a Band, a Rectangle, a Half page, a Card and a Story panel.
  Ads come from `web/ads.json`, always say "Advertisement" in words, never appear on the first screen or in the
  navigation, spine or margin notes, and no page carries more than two. Papyrus's own house ad is the first ad.

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
    When I open the page "/"
    Then the page contains "Advertisement"
    And the page contains "Have your own automated newsroom."
    And the page contains "Start your newsroom"
    And every advertisement link is marked sponsored

  Scenario: The Papyrus ad wears Papyrus's name and colors, not the site's shapes
    When I open the page "/"
    Then the page contains "mom-ad-branded"
    And the page contains "mom-ad-brand-name"
    And the page contains "mom-ad-mark"
    And the page does not contain "mom-ad-disc"

  Scenario: The stylesheet reserves the standard sizes and never animates an ad
    Then the stylesheet "/assets/mom-components.css" reserves the standard ad sizes

  Scenario: The home page band sits in the page container like the blocks around it
    When I open the page "/"
    Then the page contains "mom-home-ad"
