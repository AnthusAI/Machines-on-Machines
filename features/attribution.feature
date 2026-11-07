Feature: Say who made what, in Papyrus's words
  Readers must always be able to tell what a machine did and what a person chose. The byline says it: a story is
  "By various bots", or "By various bots and" a name when an editor approved it, and a story a person wrote names that
  person. No chip repeats the byline. The site never says "desk".

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: An AI-drafted story names its approver in the byline and nowhere else
    When I open the page "/field-notes/the-agents-are-writing-the-benchmarks-now/"
    Then the page contains "By various bots and Ada Reader"
    And the page does not contain "Drafted by AI"
    And the page does not contain "Approved by"

  Scenario: A story a person wrote is not labelled as AI work
    When I open the page "/field-notes/who-owns-an-agents-mistakes/"
    Then the page contains "By Sam Rivera"
    And the page contains "Editor’s pick"
    And the page does not contain "various bots"

  Scenario: No content page carries an AI-drafted disclaimer, because the whole site says it is drafted by AI
    When I open the page "/wiki/durable-execution/"
    Then the page does not contain "Edited by AI"
    And the page does not contain "Draft, not yet reviewed"
    And the page does not contain "Drafted by AI"
    And the page contains "Updated"

  Scenario: An article and a post end with the normal page footer and no disclaimer
    When I open the page "/field-notes/the-agents-are-writing-the-benchmarks-now/"
    Then the page does not contain "Edited by AI"
    And the page does not contain "Drafted by AI"
    And the page contains "Published by"

  Scenario: A reviewed wiki term names the reviewer
    When I open the page "/wiki/agent-evals/"
    Then the page contains "Reviewed by Ada Reader on 29 Oct 2026"

  Scenario: Conversation authors are a handle or a role label
    When I open the page "/conversations/b1c2d3e4f501/"
    Then the page contains "ada"
    And the page contains "AI"

  Scenario: An article does not explain the colors
    When I open the page "/field-notes/the-agents-are-writing-the-benchmarks-now/"
    Then the page does not contain "What the colors mean"

  Scenario: The word desk appears nowhere
    Then no projected page contains the word "desk"

  Scenario: A story with no named author and no approval is by various bots
    When I open the page "/field-notes/a-subtitle-and-a-separate-blurb/"
    Then the page contains "By various bots"
    And the page does not contain "By various bots and"

  Scenario: An editor who approves a story joins the byline
    When I open the page "/field-notes/the-agents-are-writing-the-benchmarks-now/"
    Then the page contains "By various bots and Ada Reader"

  Scenario: A team byline carried over from an older site is not presented as a named person
    When I open the page "/field-notes/a-team-byline-and-no-picture/"
    Then the page contains "By the editors"
    And the page does not contain "By Papyrus Editorial Team"

  Scenario: Cards show the same byline as the article
    When I open the page "/field-notes/"
    Then the page contains "By various bots and Ada Reader"
    And the page does not contain "Approved by"

  Scenario: The latest posts rail shows each post's byline
    When I open the page "/"
    Then the page contains "By various bots"
