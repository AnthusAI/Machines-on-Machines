Feature: The app-shell stack deploys from Git

  The Amplify app (build timeout, branch variables) is defined by infra/site.json and applied by a pipeline on merge to main,
  never by hand. A deploy rewrites the branch's whole variable list, so every variable the live branch needs must be in site.json.

  Scenario: The caller workflow deploys the stack named in site.json
    Given the app-shell caller workflow
    Then it calls the Papyrus reusable app-shell workflow at the pinned Papyrus version
    And its stack name is the stack name in infra/site.json
    And it does not start the Amplify build itself

  Scenario: The tenant and site ids survive a stack deploy
    Given the site configuration infra/site.json
    Then the branch environment carries PAPYRUS_SITE_ID and PAPYRUS_TENANT_ID equal to the site id
