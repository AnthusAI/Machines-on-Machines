Feature: Every language's navigation, menu and footer have the same destinations as the English site
  The bar, the full-page menu and the footer of a language edition list every destination the English site lists, in the same order, with the language's own labels and
  lines (`nav.<href>.label`, `nav.<href>.description`, `footer*` in `web/strings/<tag>.json`). A destination that has a page in the language goes to it; one that exists only in
  English (Findings, Videos, Conversations, About, Corrections, For agents) goes to the English page, marked as leaving the language (`lang`, `hreflang`, the Languages icon, and
  the language's name for a screen reader). Concepts go to the language's own index once a concept page exists in it, and to the English Concepts until then, never to an empty
  shell. A page that gains a localization (it appears in the page's link map) is linked there with no change to this list.

  Background:
    Given the language case is projected

  Scenario Outline: The bar has the English destinations in the same order and targets modulo the language prefix
    When I open the language page "<page>"
    Then the navigation has the same number of destinations as the English home and in the same order
    And each navigation target is the English target or the same address under "<prefix>"
    And the English-only navigation entries "/findings/, /videos/, /conversations/" go to the English page marked lang "en" and hreflang "en"
    And the Concepts entry goes to "<concepts>"

    Examples:
      | page | prefix | concepts |
      | /es/ | /es/ | /es/concepts/ |
      | /zh/ | /zh/ | /wiki/ |

  Scenario Outline: The menu mirrors the bar, with a line under each destination in the language
    When I open the language page "<page>"
    Then the menu lists the same targets as the bar and every destination has a line

    Examples:
      | page |
      | /es/ |
      | /zh/ |

  Scenario Outline: The footer has the English footer's links in the language
    When I open the language page "<page>"
    Then the footer has the same number of links as the English footer and "<labels>" first
    And the footer's English-only links are marked lang "en"

    Examples:
      | page | labels |
      | /es/ | Hallazgos, Conversaciones, Acerca de, Correcciones |
      | /zh/ | 发现, 对话, 关于, 更正 |
