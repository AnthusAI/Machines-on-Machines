Feature: The published site expires on its own and is not purged on every change
  CloudFront bills each purged path after the first thousand a month, and curation changes the home page and its lists dozens of times a day.
  The site therefore does not purge on publish. Its pages are eventually consistent: the edge keeps a page for an hour, then fetches it again.

  Scenario: Publishing does not purge the edge
    Given the site's backend configuration
    Then it turns edge invalidation off
    And it lets the edge keep a page for 3600 seconds
