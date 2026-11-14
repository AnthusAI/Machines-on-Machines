Feature: Links in a translated page keep the reader in their language, and a link that must leave it says so
  Other languages live under their own prefix with the same structure as the primary language: English keeps its existing addresses, Spanish is under `/es/` and
  Chinese under `/zh/` (Papyrus's `languages.prefixes` setting; by default the tag's first subtag). The page's canonical address is itself, and its `hreflang` links and
  language switcher use the prefixed addresses (Papyrus writes them). A reader who is reading Spanish stays in Spanish: a link in the article or in the page's navigation,
  menu, footer, section label or home link that leads to a page that has a Spanish version goes to that version. A link to a page that has no version in the reader's language
  is never turned into a different page and never switches the language silently: in the page's own words it goes to the page that exists (English), carries `lang` and
  `hreflang` of its destination and a small Languages icon after its text, with the language's name for a screen reader ("en inglés", "英文"); no parentheses and no words in
  the text. Which page a link goes to is decided by Papyrus: `page.link_in_language(path)` answers from the published language groups, and the site only marks the links that
  leave the language (`languages.localize_links`); the translator never chooses a link target. A language's section list and home list only what exists in that language.
  The primary language's pages and addresses do not change. The projected pages come from tests/language_cases.py.

  Background:
    Given the language case is projected

  Scenario: A translated page lives under its language's prefix, with its own address as canonical
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the page is canonical to "https://machines-on-machines.anth.us/es/field-notes/dirigir-una-historia/" and its language is "es-419"

  Scenario: A Chinese page lives under its prefix at an address made of the title's own characters
    When I open the language page "/zh/field-notes/如何引导一篇报道/"
    Then the page is canonical to "https://machines-on-machines.anth.us/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/" and its language is "zh-Hans"

  Scenario: hreflang names every language at its prefixed address, and x-default is the primary page
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the hreflang links are
      | hreflang  | href                                                                    |
      | en        | https://machines-on-machines.anth.us/field-notes/steer-a-story/          |
      | es-419    | https://machines-on-machines.anth.us/es/field-notes/dirigir-una-historia/ |
      | zh-Hans   | https://machines-on-machines.anth.us/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/       |
      | x-default | https://machines-on-machines.anth.us/field-notes/steer-a-story/          |

  Scenario: A link in a Spanish article to a page that has a Spanish version stays in Spanish
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the link "cómo ejecutar un monitor" goes to "/es/field-notes/ejecutar-un-monitor/" and is not marked

  Scenario: A link in a Chinese article to a page with no Chinese version leaves the language visibly
    When I open the language page "/zh/field-notes/如何引导一篇报道/"
    Then the link "如何运行监控" goes to "/field-notes/run-a-monitor/" and is marked for "英文" with lang and hreflang "en"

  Scenario: A link in a Spanish article to a page with no Spanish version carries an icon and names the language for a screen reader
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the link "la crónica sin traducir" goes to "/field-notes/read-the-wire/" and is marked for "en inglés" with lang and hreflang "en"
    And no link text holds parentheses added by the site

  Scenario: Links out of the site and to a spot in the page are left as they are
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the link "una fuente" goes to "https://example.org/fuente" and is not marked
    And the link "el principio" goes to "#top" and is not marked

  Scenario: The home link, the wordmark, the section label and the breadcrumb keep the prefix
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then every link to the home page goes to "/es/"
    And the section label links to "/es/field-notes/"

  Scenario: The navigation, the menu and the footer stay under the language prefix
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then every navigation, menu and footer link to a page goes to a page under "/es/"
    And no link in the page leads to a page in another language without saying so

  Scenario: The language switcher still links each option to its own language
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the switcher links "English" to "/field-notes/steer-a-story/", "Español" to "/es/field-notes/dirigir-una-historia/" and "中文" to "/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/"

  Scenario: A language's section list holds only what is translated into it
    When I open the language page "/es/field-notes/"
    Then the list links to "/es/field-notes/dirigir-una-historia/" and "/es/field-notes/ejecutar-un-monitor/" and to no English page
    When I open the language page "/zh/field-notes/"
    Then the list links to "/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/" and to no page that is not Chinese

  Scenario: A language's home lists only that language and offers the other languages in the switcher
    When I open the language page "/zh/"
    Then the page is canonical to "https://machines-on-machines.anth.us/zh/" and its language is "zh-Hans"
    And the switcher lists "English, Español, 中文" in that order

  Scenario: The primary language's pages and addresses do not change
    When I open the language page "/field-notes/steer-a-story/"
    Then the page is canonical to "https://machines-on-machines.anth.us/field-notes/steer-a-story/" and its language is "en"
    And the page has no marked link and no link into "/es/" or "/zh/" outside the switcher

  Scenario: The English section list does not list the translations
    When I open the language page "/field-notes/"
    Then the list links to no page under "/es/" or "/zh/"
