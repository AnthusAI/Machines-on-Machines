Feature: The site's chrome is in the reader's language only, every destination exists in it, and a language with missing words is not offered
  The navigation, the menu and its subtitles, the footer, the labels the engine writes (skip link, breadcrumb, share and Markdown labels, the cookie banner), bylines, dates
  and section names are words of the language, kept as data per language in `web/interface-strings.json` (the primary language's entry is the reference and holds every
  key). The Spanish (`es-419`) and Chinese (`zh-Hans`) wording was drafted by a machine and has not been reviewed by a speaker of the language. A language is public, and
  so offered by the switcher, named in `hreflang` and linked, only when every key exists and none is empty. Every destination of the navigation and the footer exists in each
  public language, under its prefix: an article list holds the translated articles, or says in the language that there are none; Findings, Videos, Conversations, Concepts,
  About and Corrections are not translated in the MVP, so each page says so in the language, with the navigation intact, and offers the original through a link that names
  its language. Nothing redirects to English, nothing English is shown as if it were translated, and no label carries parentheses to mark it as lesser.

  Background:
    Given the language case is projected

  Scenario Outline: The navigation is in the page's language only and every item stays under the language prefix
    When I open the language page "<page>"
    Then the navigation reads "<labels>" and nothing else
    And the navigation links go to "<prefix>articles/", "<prefix>posts/", "<prefix>findings/", "<prefix>videos/", "<prefix>conversations/" and "<prefix>wiki/"
    And no navigation label holds parentheses

    Examples:
      | page                                              | prefix | labels                                                                |
      | /es/field-notes/dirigir-una-historia/             | /es/   | Artículos, Publicaciones, Hallazgos, Videos, Conversaciones, Conceptos |
      | /zh/field-notes/如何引导一篇报道/                 | /zh/   | 文章, 动态, 发现, 视频, 讨论, 概念                                      |

  Scenario: The menu and the footer are in the language and stay under its prefix
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the menu names "Inicio, Artículos, Publicaciones, Hallazgos, Videos, Conversaciones, Conceptos" with lines in the language
    And the footer reads "Hallazgos, Conversaciones, Acerca de, Correcciones" before the feed, privacy and cookie links
    And the engine's chrome is in the language: "Saltar al contenido principal", "Compartir", "Cookies y análisis", "Aceptar todo"

  Scenario: A byline and a date use the language's own words and month names
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the byline reads "Por varios bots y Ada Reader · 27 de octubre de 2026"
    When I open the language page "/zh/field-notes/如何引导一篇报道/"
    Then the byline reads "作者：多个机器人 和 Ada Reader · 2026年10月27日"

  Scenario: The home link and the wordmark are the language's own home
    When I open the language page "/zh/findings/"
    Then every link to the home page goes to "/zh/"

  Scenario Outline: Every destination of the navigation exists in the language and keeps the navigation
    When I open the language page "<page>"
    Then the page exists in the language "<tag>" and its navigation is intact
    And the page says "<sentence>"

    Examples:
      | page                  | tag     | sentence                                                                          |
      | /es/articles/         | es-419  | Artículos traducidos                                                               |
      | /es/posts/            | es-419  | Todavía no hay publicaciones traducidas.                                           |
      | /es/findings/         | es-419  | Los hallazgos todavía no se traducen                                               |
      | /es/videos/           | es-419  | Los videos todavía no se traducen                                                  |
      | /es/conversations/    | es-419  | Las conversaciones todavía no se traducen                                          |
      | /es/wiki/             | es-419  | Las páginas de conceptos todavía no se traducen.                                   |
      | /es/about/            | es-419  | Esta página todavía no está traducida.                                             |
      | /es/corrections/      | es-419  | Esta página todavía no está traducida.                                             |
      | /zh/articles/         | zh-Hans | 已翻译的文章                                                                       |
      | /zh/posts/            | zh-Hans | 尚无已翻译的动态。                                                                 |
      | /zh/findings/         | zh-Hans | “发现”尚未翻译                                                                     |

  Scenario: A page that is not translated offers the original through a link that names its language, and shows no English cards
    When I open the language page "/es/findings/"
    Then the link "Leer el original en inglés" goes to "/findings/" and is marked for "en inglés" with lang and hreflang "en"
    And the page's own words hold no link to an English page other than that one

  Scenario: The articles list holds the translated articles and the posts list says there are none
    When I open the language page "/es/articles/"
    Then the list links to "/es/field-notes/dirigir-una-historia/" and "/es/field-notes/ejecutar-un-monitor/" and to no English page
    When I open the language page "/es/posts/"
    Then the page lists no story

  Scenario: The section's title is the section's title in the language
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the section label reads "Notas de campo"
    When I open the language page "/zh/field-notes/"
    Then the section label reads "现场笔记"

  Scenario: The primary language's chrome and addresses do not change
    When I open the language page "/field-notes/steer-a-story/"
    Then the navigation reads "Articles, Posts, Findings, Videos, Conversations, Concepts" and nothing else
    And the navigation links go to "/articles/", "/posts/", "/findings/", "/videos/", "/conversations/" and "/wiki/"

  Scenario: The interface strings of every public language hold every key of the primary language
    Then every public language has every interface string of English, none empty, with twelve month names and a title for every section

  Scenario: A language with a missing key is not offered by the switcher
    Then a language missing a key is in no language group and so is not offered

  @browser
  Scenario Outline: The navigation is in the language, has no parentheses and fits beside the switcher
    When I check the translated chrome in a browser <width> pixels wide
    Then the navigation in "es-419" and in "zh-Hans" shows only the language's own words with no parentheses and nothing is cut off
    And the menu shows the translated labels

    Examples:
      | width |
      | 375   |
      | 1440  |
