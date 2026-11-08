Feature: The edge can answer where the cookie notice is needed, and only when it is switched on
  The pages stay cached and identical for every visitor. The page script asks the site's own address /_papyrus/consent
  which country the visitor is in, and the edge answers that one request itself from the country header CloudFront adds.
  The edge template has a switch for this. It is off by default, so the edge is exactly what it was.

  Scenario: Off by default leaves the edge unchanged
    Given the edge template
    When it is rendered with the lookup switch at its default
    Then it creates the same resources as the template before the consent change
    And it has no behavior for the consent path

  Scenario: On adds only the consent path
    Given the edge template
    When it is rendered with the lookup switched on
    Then it has exactly one more behavior than before, for the path "/_papyrus/consent" only
    And the new behavior answers from a function on the viewer request and allows only GET and HEAD
    And the page behavior and every other path behavior are exactly as they were

  Scenario: The country header reaches the function by a policy that can be swapped
    Given the edge template
    When it is rendered with the lookup switched on and the header policy "origin-request-policy"
    Then the consent path has an origin request policy that forwards "CloudFront-Viewer-Country"
    When it is rendered with the lookup switched on and the header policy "cache-policy"
    Then the consent path has a cache policy that includes "CloudFront-Viewer-Country"

  Scenario: The answer is never cached
    Given the edge template
    When it is rendered with the lookup switched on
    Then the consent function answers with "private, no-store"
    And an unknown country gets the notice
