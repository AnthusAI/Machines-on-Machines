Feature: A page in a language whose slug is made of characters is written the same way everywhere
  A localization drafts its slug once, at first publish (the slug lock then fixes it): Papyrus's `localized_slug`, by the language's policy in the editorial settings'
  `languages.slugs` (`translated` for Spanish, `characters` for Chinese, `primary` to reuse the primary's slug). Drafting and its limits (no cap of ours, 255 bytes of UTF-8
  for a directory name, a title that yields no slug is refused) are Papyrus's, with its own specifications. This feature covers what the site shows of such a page: it lives
  at a directory named with the characters, and every place that names its address (`canonical`, `hreflang`, the switcher, links, the sitemap) writes it percent-encoded, the form
  the browser copies; both forms are the same page.

  Scenario: The Chinese page is a directory named with its characters, served at the percent-encoded address
    Given the language case is projected
    Then the directory "zh/field-notes/如何引导一篇报道" holds the Chinese page
    And the server returns that page at "/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/"

  Scenario: The address, the hreflang links, the switcher and the links write the Chinese page percent-encoded and the same
    Given the language case is projected
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the Chinese page's address is written percent-encoded in the hreflang links, the switcher and the menu, and nowhere as raw characters

  Scenario: The sitemap names the Chinese page percent-encoded
    Given the language case is projected
    Then the sitemap lists "https://machines-on-machines.anth.us/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/" once
    And no address in the sitemap holds characters outside ASCII

  Scenario: A copied address is the percent-encoded form, and decoding it gives the characters
    Given the language case is projected
    When I open the language page "/zh/field-notes/如何引导一篇报道/"
    Then the page's canonical address, once decoded, is "https://machines-on-machines.anth.us/zh/field-notes/如何引导一篇报道/"
    And the page's canonical address is the percent-encoded form of those characters

  Scenario: The Chinese section list links to the page percent-encoded
    Given the language case is projected
    When I open the language page "/zh/field-notes/"
    Then the list links to "/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/" and to no page that is not Chinese
