Feature: A reader can switch a page to another language, and is welcomed in the language their browser prefers
  Every page that exists in more than one language carries a language switcher in the top bar, and the same list inside the full-page menu, so a phone has it
  too. It lists only the languages that page exists in, each written in its own language and script ("English", "Español", "中文"), never as a flag, and each is
  a real link to the matching translation of the same page, with `lang` and `hreflang`. The current language is marked by its name in the control, a check mark and
  `aria-current`, never by colour alone. A page with no translation in a language does not list it: nothing is offered in place of a missing translation, and a
  page with no translation at all has no switcher. The list of languages of a page (its language group) comes from one place, `web/languages.py`, which Papyrus
  will replace; the component only draws what it is handed. The site itself sets `<html lang>` and the `hreflang` links, including `x-default`, for each page.

  A visitor whose browser prefers another language that the page they are on exists in sees a small banner in that language: Switch now, Stay here, Pause, and
  a 15 second countdown. The countdown never goes toward the site's primary language (English): there the visitor is offered a quiet "Read in English" link, so
  a crawler that runs scripts and prefers English cannot be sent away from a translated page. The visitor's choice (switching, letting the clock run out,
  staying, or picking a language in the switcher) is remembered in this browser only, in localStorage, never in a cookie; a remembered language switches a
  page that exists in it at once, with a note and Undo, and leaves a page that does not exist in it alone. Nothing moves when the banner appears.

  The static scenarios read the projected pages. The browser scenarios run when Playwright is installed:
  `PLAYWRIGHT_MODULE=<path to playwright> behave features/language-switcher.feature --tags=@browser`

  Background:
    Given the language case is projected

  Scenario: A page with translations has a switcher listing its languages in their own names
    When I open the language page "/field-notes/steer-a-story/"
    Then the switcher lists "English, Español, 中文" in that order
    And the switcher's control is named "Language: English" and shows the Lucide "languages" icon
    And no language is drawn as a flag or a picture

  Scenario: Every option is a link with lang and hreflang to the same article in that language
    When I open the language page "/field-notes/steer-a-story/"
    Then the switcher links "English" to "/field-notes/steer-a-story/", "Español" to "/es/field-notes/dirigir-una-historia/" and "中文" to "/zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/"
    And every switcher option has lang and hreflang equal to its language tag "en, es-419, zh-Hans"

  Scenario Outline: The current language is marked by text, a check mark and aria-current
    When I open the language page "<page>"
    Then the control shows "<name>" as the current language
    And only the "<name>" option has aria-current and a check mark
    And the page's html lang is "<tag>"

    Examples:
      | page                          | name    | tag     |
      | /field-notes/steer-a-story/    | English | en      |
      | /es/field-notes/dirigir-una-historia/ | Español | es-419  |
      | /zh/field-notes/%E5%A6%82%E4%BD%95%E5%BC%95%E5%AF%BC%E4%B8%80%E7%AF%87%E6%8A%A5%E9%81%93/ | 中文    | zh-Hans |

  Scenario: A page with no translation in a language does not offer that language
    When I open the language page "/field-notes/run-a-monitor/"
    Then the switcher lists "English, Español" in that order
    And the page has no hreflang for "zh-Hans"

  Scenario: A page with no translation at all has no switcher, no banner and no language script
    When I open the language page "/field-notes/read-the-wire/"
    Then the page has no language switcher, no welcoming banner, no language script and no hreflang
    And the page's html lang is "en"

  Scenario: A page with no translation is unchanged
    When I open the language page "/field-notes/read-the-wire/"
    Then the page has no language switcher, no welcoming banner, no language script and no hreflang

  Scenario: Every page of a group lists every language of the group, itself included, and x-default
    When I open the language page "/es/field-notes/dirigir-una-historia/"
    Then the page has hreflang links for "en, es-419, zh-Hans" with absolute addresses of the matching pages
    And the page has an x-default hreflang that is the English page
    And the page is canonical to itself

  Scenario: The same languages are in the full-page menu for a phone
    When I open the language page "/field-notes/steer-a-story/"
    Then the menu lists the languages "English, Español, 中文" under a heading named in the page's language

  Scenario: The switcher's words are in the page's own language
    When I open the language page "/zh/field-notes/如何引导一篇报道/"
    Then the switcher's control is named "语言: 中文" and shows the Lucide "languages" icon

  Scenario: The banner is empty and hidden in the page and drawn before the page's content
    When I open the language page "/field-notes/steer-a-story/"
    Then the welcoming banner is hidden, empty and comes right after the skip link
    And the banner's words for every language of the group are in the page as JSON

  Scenario: The language script is loaded in the head before the page is drawn and uses no cookie
    When I open the language page "/field-notes/steer-a-story/"
    Then the language script is in the head without defer
    And the language script never reads or writes a cookie and keeps the choice only in localStorage under "papyrus.readingLanguage"

  Scenario: The countdown never switches toward the primary language
    Then the language script gives the primary language a link and never a countdown
    And Traditional Chinese preferences match no page and Simplified ones match "zh-Hans"

  Scenario: The stylesheet uses no borders for the switcher and the banner, and respects reduced motion
    Then the switcher and banner rules draw no border, and the focus outline is the only outline
    And with reduced motion the countdown bar is not drawn and nothing fades

  @browser
  Scenario Outline: The switcher is in the bar, links to the translations and never scrolls the page sideways
    When I check the language switcher in a browser <width> pixels wide
    Then the control is in the bar and named "Language: English"
    And the language list holds the three languages as links, the current one marked
    And the language page does not scroll sideways
    And the control and the list are reachable by keyboard with a visible focus, and Escape closes the list

    Examples:
      | width |
      | 375   |
      | 820   |
      | 1440  |
      | 2560  |

  @browser
  Scenario: On a phone the bar shows only the icon and the full list is in the menu
    When I check the language switcher in a browser 375 pixels wide
    Then the bar's control shows the icon alone at 48 pixels and the menu holds the three languages in 72 pixel blocks

  @browser
  Scenario: Without JavaScript the switcher still works as a list of links
    When I check the language switcher in a browser 375 pixels wide
    Then without JavaScript the control and its links are still there

  @browser
  Scenario Outline: A visitor who prefers Chinese is offered the Chinese page with a countdown that can be paused
    When a browser <width> pixels wide that prefers Chinese opens the English page
    Then the banner is shown in Chinese before the masthead with Switch now, Stay here and Pause
    And the countdown reads 15 seconds, counts down and is announced once in a polite live region
    And Pause stops the clock and Resume starts it again
    And when the clock runs out the page is replaced by the Chinese page and the choice is remembered

    Examples:
      | width |
      | 375   |
      | 1440  |

  @browser
  Scenario: No banner when the page does not exist in the preferred language
    When a browser 1440 pixels wide that prefers Chinese opens the page with no Chinese page
    Then there is no banner, the page stays and Chinese is not in the switcher
    And a Traditional Chinese browser is offered nothing on the Chinese page
    And a Spanish browser from Mexico is offered the Spanish page

  @browser
  Scenario: An English-preferring visitor on a translated page is offered a link and never a countdown
    When an English-preferring browser 1440 pixels wide opens the Spanish page
    Then the banner is a quiet "Read in English" link to the English page with no countdown
    And two minutes later the page has not moved
    And a Chinese-preferring browser on the Chinese page sees no banner

  @browser
  Scenario: Staying is remembered across a reload and across pages
    When a browser 1440 pixels wide that prefers Chinese stays on the English page
    Then after a reload and on another English page there is no banner and the page stays

  @browser
  Scenario: A language picked in the switcher is remembered, switches later pages with a note, and Undo goes back
    When an English-preferring browser 375 pixels wide picks 中文 in the switcher
    Then the Chinese page opens and Chinese is remembered
    And opening the English page again opens the Chinese page with a note "已切换到中文" and Undo, without adding to the history
    And Undo returns to the English page and remembers English
    And a remembered language leaves a page that does not exist in it alone

  @browser
  Scenario: Without storage the page still works and the banner still offers
    When a browser 1440 pixels wide that prefers Chinese opens the English page with storage blocked
    Then the banner is shown and the page raised no error

  @browser
  Scenario Outline: Nothing moves when the banner appears
    When a browser <width> pixels wide that prefers Chinese measures the English page as it loads
    Then the navigation bar never changes its position while the page loads and no layout shift is reported

    Examples:
      | width |
      | 375   |
      | 1440  |
