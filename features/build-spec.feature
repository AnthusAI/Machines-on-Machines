Feature: The Amplify build runs the same steps as every Papyrus site
  A Papyrus site's Amplify build does more than deploy the backend and build the pages. Right after the backend deploys it registers the
  procedures (`papyrus procedures seed-required`), applies the agent definitions (`papyrus agents apply`) and reconciles the schedule group
  (`papyrus agents schedules --site <brand id>`). Papyrus generates that build spec from `infra/site.json`, so this repository keeps no
  hand-written copy: `amplify.yml` is exactly what `papyrus-infra print-buildspec` prints for the production app.

  Scenario: The build spec is the one Papyrus generates from the site's configuration
    When Papyrus prints the production build spec for "infra/site.json"
    Then "amplify.yml" is exactly that build spec

  Scenario: The build registers procedures, applies agents and reconciles schedules, in that order, after the backend deploys
    Then "amplify.yml" runs these commands in order
      | command                                              |
      | npx papyrus-infra backend-deploy                     |
      | papyrus procedures seed-required                     |
      | papyrus agents apply                                 |
      | papyrus agents schedules --site machines-on-machines |

  Scenario: The build names the site that the steps act on
    Then "infra/site.json" sets "PAPYRUS_TENANT_ID" and "PAPYRUS_SITE_ID" to "machines-on-machines"
    And the schedule step names the site's brand "machines-on-machines"
