Feature: Findings, Videos and Conversations exist in each language, listing the same items as in English
  A language edition has a page for each of the site's lists (Findings, Videos, Conversations) with its own title, line, notice and chrome in the language, the same items in the
  same order as the English page (the same ranking, and the Videos rule that keeps videos rated two stars or lower out), and the page and its English page name each other
  (`hreflang`, the switcher). What is written by a source or a person stays in its own language and is marked `lang`; a line at the top says so. The navigation, the menu and
  the footer link to these pages, not to the English ones.

  Background:
    Given the language case is projected

  Scenario Outline: Each list has a page in each language, with the language's title, line and the original-language notice
    When I open the language page "<page>"
    Then the list page title is "<title>"
    And the list page says "<notice>" above the items
    And the page names its English page in hreflang "en" and its own in "<tag>"

    Examples:
      | page | title | notice | tag |
      | /es/findings/ | Hallazgos | Los elementos de esta página están en su idioma original, el inglés. | es |
      | /es/videos/ | Videos | Los elementos de esta página están en su idioma original, el inglés. | es |
      | /es/conversations/ | Conversaciones | Los elementos de esta página están en su idioma original, el inglés. | es |
      | /zh/findings/ | 发现 | 本页的内容保持原文语言：英文。 | zh-Hans |
      | /zh/videos/ | 视频 | 本页的内容保持原文语言：英文。 | zh-Hans |
      | /zh/conversations/ | 对话 | 本页的内容保持原文语言：英文。 | zh-Hans |

  Scenario Outline: A list shows the same items as the English page, in the same order
    When I open the language page "<english>"
    And I read its first items as "english"
    And I open the language page "<page>"
    Then its first items are the same as "english"

    Examples:
      | english | page |
      | /findings/ | /es/findings/ |
      | /videos/ | /es/videos/ |
      | /videos/ | /zh/videos/ |

  Scenario: The cards say their words in the language and mark the source's words
    When I open the language page "/es/findings/"
    Then the cards' status reads "Aceptado automáticamente" and not "Accepted automatically"
    And the cards' titles carry lang "en"

  Scenario: The forum's words are in the language
    When I open the language page "/es/conversations/"
    Then the page says "tablero", "conversaciones", "mensajes", "Más activas" and "Actividad reciente:" and none of "messages", "Most active", "Recently active"

  Scenario Outline: The navigation, the menu and the footer link to the pages in the language
    When I open the language page "<page>"
    Then the navigation links "<findings>", "<videos>" and "<conversations>" with no marker that leaves the language
    And the footer links "<findings>" and "<conversations>"

    Examples:
      | page | findings | videos | conversations |
      | /es/ | /es/findings/ | /es/videos/ | /es/conversations/ |
      | /zh/ | /zh/findings/ | /zh/videos/ | /zh/conversations/ |
