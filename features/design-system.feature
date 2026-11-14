Feature: Each release publishes the site's design system to Papyrus
  Papyrus keeps a site's design system as backend data: the figure colours, fonts and worked examples that `papyrus figures render` draws with,
  and the site settings the newsroom enforces, such as requiring an editor's star rating before a Story publishes.
  This repository is where the design system is edited. Each release builds it into the one folder Papyrus reads and pushes it as the next version.

  Scenario: The folder built for Papyrus is one Papyrus can store and draw with
    When the design system folder is built
    Then Papyrus loads it as a design system with the Anton and Archivo fonts embedded
    And Papyrus would store it, with every gallery figure as a worked example

  Scenario: A Story needs an editor's star rating before it publishes
    When the design system folder is built
    Then its settings turn on "publishRequiresRating" and nothing else

  Scenario: The release pushes it after the site deploys
    Then the deploy workflow pushes the built folder after the deploy job, with the site's GitHub CI role on the operator lane
