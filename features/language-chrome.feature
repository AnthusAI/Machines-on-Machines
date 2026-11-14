Feature: The site's chrome is in the reader's language only, and a language with missing words is not served
  The navigation, the menu and its subtitles, the footer, the labels the engine writes (skip link, breadcrumb, share and Markdown labels, the cookie banner), bylines, dates
  and section names are words of the language, kept as data per language in `web/strings/<tag>.json` (one flat object of `key: text` per language; the primary language's
  file is the reference and holds every key). Papyrus reads them as `page.strings` and refuses to serve a language whose file lacks a key the engine or the site needs. The
  Spanish (`es-419`) and Chinese (`zh-Hans`) wording was drafted by a machine and has not been reviewed by a speaker of the language. A language edition has the destinations
  that exist in the language: the home, the listings of articles, posts and Concepts (at `/<prefix>/concepts/`), and the language's own section lists. The pages that exist only
  in the primary language (Findings, Videos, Conversations, About, Corrections, `llms.txt`) are not in an edition, so its navigation and footer leave them out: nothing links
  to an English page as if it were the language's own, and no label carries parentheses to mark it as lesser.

  Background:
    Given the language case is projected

  Scenario Outline: The navigation is in the page's language only and every item stays under the language prefix
    When I open the language page "<page>"
    Then the navigation reads "<labels>" and nothing else
    And the navigation links go to "<prefix>articles/", "<prefix>posts/" and "<prefix>concepts/"
    And no navigation label holds parentheses

    Examples:
      | page                                              | prefix | labels                                  |
      | /es/field-notes/dirigir-una-historia/             | /es/   | Artículos, Publicaciones, Conceptos      |
      | /zh/field-notes/如何引导一篇报道/                 | /zh/   | 文章, 动态, 概念                         |

  Scenario: The menu and the footer are in the language and stay under its prefix
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the menu names "Inicio, Artículos, Publicaciones, Conceptos" with lines in the language
    And the footer reads "RSS, Privacidad, Configuración de cookies" with the feed of the language
    And the engine's chrome is in the language: "Saltar al contenido principal", "Compartir", "Cookies y análisis", "Aceptar todo"

  Scenario: The pages that exist only in the primary language are not offered in a language edition
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then no link in the navigation, the menu or the footer leads to Findings, Videos, Conversations, About, Corrections or llms.txt

  Scenario Outline: A translated page says it was translated by AI, under the byline, with a link to the original
    When I open the language page "<page>"
    Then under the byline the page says "<sentence>" and links "<words>" to "<original>" with hreflang "en"

    Examples:
      | page                                  | sentence                           | words              | original                    |
      | /es/field-notes/dirigir-una-historia/ | Traducido por IA del original en inglés | original en inglés | /field-notes/steer-a-story/ |
      | /zh/field-notes/如何引导一篇报道/     | 由 AI 翻译自英文原文                | 英文原文           | /field-notes/steer-a-story/ |
      | /es/concepts/evaluaciones-de-agentes/ | Traducido por IA del original en inglés | original en inglés | /wiki/agent-evals/          |

  Scenario: The original and a page that is not a translation carry no such line
    When I open the language page "/field-notes/steer-a-story/"
    Then the page has no translation line

  Scenario: A byline and a date use the language's own words and month names
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the byline reads "Por varios bots y Ada Reader · 27 de octubre de 2026"
    When I open the language page "/zh/field-notes/如何引导一篇报道/"
    Then the byline reads "作者：多个机器人 和 Ada Reader · 2026年10月27日"

  Scenario: The Concepts page of a language is at its prefix plus concepts, and the nav marks it as current
    When I open the language page "/es/concepts/"
    Then the navigation marks "Conceptos" as the current page
    And the list links to the concept "/es/concepts/evaluaciones-de-agentes/"
    When I open the language page "/zh/concepts/"
    Then the navigation marks "概念" as the current page

  Scenario: The primary language's Concept and the Spanish one are each other's alternates
    When I open the language page "/wiki/agent-evals/"
    Then the switcher lists "English, Español" in that order
    When I open the language page "/es/concepts/evaluaciones-de-agentes/"
    Then the switcher lists "English, Español" in that order

  Scenario: The home link and the wordmark are the language's own home
    When I open the language page "/zh/field-notes/"
    Then every link to the home page goes to "/zh/"

  Scenario Outline: Every destination of the navigation exists in the language and keeps the navigation
    When I open the language page "<page>"
    Then the page exists in the language "<tag>" and its navigation is intact
    And the page says "<sentence>"

    Examples:
      | page              | tag     | sentence                                          |
      | /es/posts/        | es-419  | Todavía no se ha publicado nada aquí.              |
      | /es/concepts/     | es-419  | Cada concepto que sigue nuestra base de conocimiento |
      | /es/field-notes/  | es-419  | Cómo ejecutar un monitor                           |
      | /zh/posts/        | zh-Hans | 这里还没有发布任何内容。                           |
      | /zh/concepts/     | zh-Hans | 我们知识库跟踪的每个概念在这里都有一页               |

  Scenario: A language's section lists only its own stories
    When I open the language page "/es/field-notes/"
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
    And the footer reads "Findings, Conversations, About, Corrections, RSS, For agents, Privacy, Cookie settings" with the feed of the language

  Scenario: The interface strings of every language hold every key of the primary language
    Then every language file is a flat object holding every key of English, none empty, with twelve month names

  Scenario: Papyrus refuses to serve a language whose words are missing, and names the key
    Then serving Spanish without the key "nav./posts/.label" is refused naming "es-419: nav./posts/.label"

  @browser
  Scenario Outline: The navigation is in the language, has no parentheses and fits beside the switcher
    When I check the translated chrome in a browser <width> pixels wide
    Then the navigation in "es-419" and in "zh-Hans" shows only the language's own words with no parentheses and nothing is cut off
    And the menu shows the translated labels

    Examples:
      | width |
      | 375   |
      | 1440  |
