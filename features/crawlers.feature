Feature: Search and AI crawlers are told plainly that they may read the site
  Some tools only read a site when its crawler rules say so in words, not by saying nothing.
  The published site therefore names Google's search crawler and Google's AI crawler, and allows both.

  Scenario: Google's crawlers are allowed by name
    Given the Machines on Machines site is projected from the fixtures
    When I read the file "/robots.txt"
    Then the file allows everyone with "User-agent: *"
    And the file allows "Googlebot" to read everything
    And the file allows "Google-Extended" to read everything
    And the file blocks nobody
    And the file points to the sitemap
