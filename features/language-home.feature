Feature: The home of a language edition is the site's home design built from that language's Stories
  The home of `/es/` and `/zh/` is not the engine's plain list. It has the English home's shape: the site card with its purpose beside the lead article, the latest posts,
  then each section that has a translated article as a group of its newest, then the top posts. It lists only Stories of its own language. Every word of it comes from the
  language's strings (`web/strings/<tag>.json`), and a section the site has no name for in the language shows its English name, marked as English, never blank. A section
  has its English page one link away, marked as leaving the language. A language with no Story yet says so and links to the English home. The lead picture loads at once
  and a picture that has not arrived yet shows a flat tone, so the page is never blank below the heading. Chinese text uses Chinese faces, no italics, no capitals and no
  letter-spacing. The publication's name is localized with the rest of the words: Máquinas Sobre Máquinas, 机器论机器.

  Background:
    Given the language case is projected

  Scenario Outline: The edition home has the home design, in the language, with the language's own Stories only
    When I open the language page "<page>"
    Then the home heading reads "<heading>"
    And the home lead article is "<lead>"
    And the site card tagline reads "<tagline>"
    And the home purpose reads "<purpose>"
    And every story link on the home is under "<prefix>"

    Examples:
      | page | prefix | heading | lead | tagline | purpose |
      | /es/ | /es/ | Artículos destacados | Cómo ejecutar un monitor | Información sobre los sistemas de información | ¿Qué pasa cuando las máquinas dan forma al mundo y a otras máquinas? Las máquinas lo informan, las personas las guían y tú puedes verlo todo suceder. |
      | /zh/ | /zh/ | 精选文章 | 如何引导一篇报道 | 关于信息系统的信息 | 当机器塑造世界，也塑造彼此，会发生什么？机器负责报道，人负责掌舵，而你可以亲眼看着这一切发生。 |

  Scenario: The home says where the rest of the site is and links to it in English
    When I open the language page "/es/"
    Then the home links "Más artículos…" to "/es/articulos/"
    And the home links "Leer todo el sitio en inglés" to "/" marked as English

  Scenario: The lead picture loads at once and every picture frame has a flat tone
    When I open the language page "/es/"
    Then the lead picture is eager with high priority and no other card picture is
    And the picture frames have a flat panel tone

  Scenario: A language with no Story yet says so and links to the English home
    Given a language home with no translated Story
    Then the home says nothing is translated yet and links to the English index
    And the home has no article group

  Scenario: A section the language has no name for shows its English name as English
    Given a language home with a section the language does not name
    Then that section's heading is its English name marked lang "en"
    And a section the language names uses the language's name
    And each section group links "Leer en inglés" to its English page marked as English

  Scenario: Chinese text has Chinese faces and no italics, capitals or letter-spacing
    Then the Chinese stylesheet names Chinese faces, normal style and no letter-spacing

  Scenario: The Articles and Posts pages of a language name their sections and counts in the language
    Given a language sectioned page with a section the language names and one it does not
    Then the named section's heading is the language's name and the other is its English name marked lang "en"
    And the count reads "30 historias" and the link at the end reads "Más de Agentes…"

  Scenario: The latest posts are the newest, and the top posts follow the Story ranking
    Given a language home with fourteen posts, newest first, that the ranking puts in the opposite order
    Then the latest posts are the twelve newest, newest first
    And the top posts are the other two, in the ranking's order

  Scenario: The lead is the best ranked translated article, not the newest
    Given a language home with two articles, the older one ranked first
    Then the home lead article of the stub home is "Viejo mejor valorado"

  Scenario Outline: The home has the English home's loop bands, with the brand phrase and the other words in the language
    When I open the language page "<page>"
    Then the home has loop bands and the first reads "<lead>" and "<on>" in the language
    And a band reads "<information>" and "<about>"
    And the bands move only when motion is allowed and never carry meaning by colour alone

    Examples:
      | page | lead | on | information | about |
      | /es/ | Máquinas | sobre | Información | sobre |
      | /zh/ | 机器 | 论 | 信息 | 关于 |

  Scenario Outline: The name of the publication is localized in every language edition
    When I open the language page "<page>"
    Then the title ends with "<name>" and og:site_name is "<name>"

    Examples:
      | page | name |
      | /es/ | Máquinas Sobre Máquinas |
      | /zh/ | 机器论机器 |
      | /es/articulos/ | Máquinas Sobre Máquinas |
      | /zh/%E6%96%87%E7%AB%A0/ | 机器论机器 |

  Scenario Outline: The wordmark is the language's name in every place it is drawn
    When I open the language page "<page>"
    Then the masthead, the site card, the spine and the footer draw the wordmark "<lead>" "<on>" "<lead>"
    And the wordmark seal is "<seal>"
    And the footer names the English name "Machines on Machines" marked as English

    Examples:
      | page | lead | on | seal |
      | /es/ | Máquinas | sobre | a pill |
      | /zh/ | 机器 | 论 | round |

  Scenario: The English home keeps the English wordmark and a round seal
    When I open the page "/"
    Then the masthead, the site card, the spine and the footer draw the wordmark "Machines" "on" "Machines"
    And the wordmark seal is "round"

  Scenario: The Chinese wordmark is Chinese display type
    Then the Chinese stylesheet gives the wordmark heavy strokes, normal style and no letter-spacing

  Scenario: The share picture of each edition carries its name, with alt text in the language
    When I open the language page "/es/"
    Then og:image is "https://machines-on-machines.anth.us/assets/share/mom-share-default-es.png" and its alt text starts "Máquinas Sobre Máquinas"
    When I open the language page "/zh/"
    Then og:image is "https://machines-on-machines.anth.us/assets/share/mom-share-default-zh.png" and its alt text starts "机器论机器"

  Scenario Outline: Search engines connect the editions through the structured data
    When I open the language page "<page>"
    Then the WebSite structured data names "<name>" with alternate names "<first>" and "<second>"

    Examples:
      | page | name | first | second |
      | /es/ | Máquinas Sobre Máquinas | Machines on Machines | 机器论机器 |
      | /zh/ | 机器论机器 | Machines on Machines | Máquinas Sobre Máquinas |

  Scenario Outline: The feeds are titled in the language
    Then the feed "<feed>" of the language case is titled "<title>"

    Examples:
      | feed | title |
      | es/feed.xml | Máquinas Sobre Máquinas |
      | zh/feed.xml | 机器论机器 |

  Scenario: Posts of one date are ordered by their English pages, as the English home orders them
    Given a language home with three posts of one date whose English pages order them the opposite way
    Then the latest posts are in the English pages' order: Post 1, Post 2, Post 3

  Scenario: A section shows as many Stories as its rank allows on the English home
    Given a language home with five sections of one article each, ranked in order
    Then the sections show 3, 3, 3 and then 2 Stories, as the English home's ranks do

  Scenario Outline: Each section has a page in the language, with the language's name for it and the section in English one link away
    When I open the language page "<page>"
    Then the page title is "<title>" and its heading is "<title>"
    And the page links "<english>" to "/security/" marked as English
    And the page names the section's English page in hreflang "en" and its own in "<tag>"

    Examples:
      | page | title | english | tag |
      | /es/security/ | Privacidad y seguridad | Leer en inglés | es |
      | /zh/security/ | 隐私与安全 | 阅读英文版 | zh-Hans |
