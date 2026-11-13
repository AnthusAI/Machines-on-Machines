Feature: Each language drafts the slug of its pages by its own policy, and a slug of characters is written the same way everywhere
  A localization drafts its slug once, at first publish (the slug lock then fixes it). How is a setting per language in `web/language-groups.json` (`slugPolicies`), not code:
  `translated` (Spanish: ASCII words from the Spanish title), `characters` (Chinese: the title's own characters) or `primary` (the primary language's slug). A slug of
  characters strips punctuation and full-width marks, turns spaces into hyphens, keeps Han characters, and is cut at a whole character so that it is no longer than 120
  characters once percent-encoded, which is what a copied address, an email or a chat message carries. A title that yields no slug is an error that says so: no slug is guessed.
  Such a page lives at a directory named with the characters, and every place that names its address (`canonical`, `hreflang`, the switcher, links, `llms.txt`, the sitemap)
  writes it percent-encoded, the form the browser copies; both forms are the same page. Until Papyrus keeps non-ASCII slugs, the tests project the page under a stand-in slug
  and move it (`tools/preview_local.py`); the engine's own proof is Papyrus's.

  Scenario Outline: The policy drafts the slug
    Then the "<policy>" policy drafts the slug "<slug>" from the title "<title>"

    Examples:
      | policy     | title                                                                | slug                                  |
      | characters | 如何引导一篇报道                                                     | 如何引导一篇报道                      |
      | characters | 近一半的新歌由 AI 制作。几乎没人听。                                 | 近一半的新歌由-ai-制作几乎没          |
      | characters | “你可以”：私密、有用（二选一）！                                     | 你可以私密有用二选一                  |
      | translated | Cómo ejecutar un monitor                                             | como-ejecutar-un-monitor              |
      | translated | Una prueba de seguridad de IA traspasó sus límites y                 | una-prueba-de-seguridad-de-ia-traspaso-sus-limites |

  Scenario: A Chinese slug is cut at a whole character within the encoded limit
    Then a Chinese title of 40 characters drafts a slug of 13 characters whose encoded form is at most 120 characters

  Scenario: A title that yields no slug is an error, never a guess
    Then the "characters" policy refuses the title "！？。，" saying that no slug can be drafted

  Scenario: Each language's policy is in the setting file
    Then the slug policy of "zh-Hans" is "characters" and of "es" is "translated"

  Scenario: The primary policy reuses the primary language's slug
    Then the primary policy reuses the slug "steer-a-story" for the title "如何引导一篇报道"

  Scenario: The Chinese page is a directory named with its characters, served at the percent-encoded address
    Given the language case is projected
    Then the directory "zh/field-notes/如何引导一篇报道" holds the Chinese page
    And the server returns that page at "/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/"

  Scenario: The address, the hreflang links, the switcher and the links write the Chinese page percent-encoded and the same
    Given the language case is projected
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the Chinese page's address is written percent-encoded in the hreflang links, the switcher and the menu, and nowhere as raw characters

  Scenario: The sitemap and llms.txt name the Chinese page percent-encoded
    Given the language case is projected
    Then the sitemap lists "https://machines-on-machines.anth.us/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/" once
    And no address in the sitemap holds characters outside ASCII

  Scenario: A copied address is the percent-encoded form, and decoding it gives the characters
    Given the language case is projected
    When I open the language page "/zh/field-notes/如何引导一篇报道/"
    Then the page's canonical address, once decoded, is "https://machines-on-machines.anth.us/zh/field-notes/如何引导一篇报道/"
    And the page's canonical address is the percent-encoded form of those characters

  Scenario: The Chinese section list and home link to the page percent-encoded
    Given the language case is projected
    When I open the language page "/zh/field-notes/"
    Then the list links to "/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/" and to no page that is not Chinese

  Scenario: A link to the page written with raw characters or percent-encoding goes to the same localization
    Then a Spanish page's link to "/zh/field-notes/如何引导一篇报道/" and to the same address percent-encoded are both left at that page
