Feature: The home of a language edition is the site's home design built from that language's Stories
  The home of `/es/` and `/zh/` is not the engine's plain list. It has the English home's shape: the site card with its purpose beside the lead article, the latest posts,
  then each section that has a translated article as a group of its newest, then the top posts. It lists only Stories of its own language. Every word of it comes from the
  language's strings (`web/strings/<tag>.json`), and a section the site has no name for in the language shows its English name, marked as English, never blank. A section
  has its English page one link away, marked as leaving the language. A language with no Story yet says so and links to the English home. The lead picture loads at once
  and a picture that has not arrived yet shows a flat tone, so the page is never blank below the heading. Chinese text uses Chinese faces, no italics, no capitals and no
  letter-spacing; the wordmark stays Latin.

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
    Then the home links "Más artículos…" to "/es/articles/"
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
