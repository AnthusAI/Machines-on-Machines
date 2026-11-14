Feature: Translations are invisible until the site makes a language public
  A language is written, translated and checked as soon as the site enables it (the editorial settings' `languages.enabled`), but the public site serves it only when it is in
  `languages.public`. With `public` unset the site serves its primary language alone: a published translation has no page, and no page lists a language switcher, a banner,
  `hreflang` or a language address. Flipping a language public is a separate, deliberate step of the newsroom's settings, not part of this repository.

  Scenario: With every language enabled and none public, nothing of a translation is served
    Given the language case is projected with translations published but no language public
    Then no page of the site is under "es/" or "zh/"
    And no page of the site has a language switcher, a welcoming banner, a language script or an hreflang link
    And the sitemap lists no address under "/es/" or "/zh/"
    And the English article "/field-notes/steer-a-story/" is where it always was and says its language is "en"
