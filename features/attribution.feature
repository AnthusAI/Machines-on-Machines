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
    And the page contains "<a href="https://anth.us" data-cta-location="footer">Anthus AI Solutions</a>"

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

  Scenario: A story card on the home page shows its byline
    When I open the page "/"
    Then the page contains "By Sam Rivera"

  Scenario: A story whose recorded author is just "AI" is by various bots
    "By AI" names no one. A story whose only author is a machine label reads "By various bots", like a story with no author.
    When I open the page "/field-notes/a-story-whose-author-is-ai/"
    Then the page contains "By various bots"
    And the page does not contain "By AI"

  Scenario: The Markdown twin of a story says what the page says
    The page and its twin at index.md use one byline rule, supplied to Papyrus as the site's byline hook. A story the bots drafted names the person who is its author, and a story with no human author is by various bots.

    Then the file "field-notes/a-bot-draft-with-a-human-author/index.md" contains "By various bots and Ryan Porter"
    And the file "field-notes/a-bot-draft-with-a-human-author/index.md" does not contain "By Ryan Porter"
    And the file "field-notes/a-story-whose-author-is-ai/index.md" contains "By various bots ·"
    And the file "field-notes/a-story-whose-author-is-ai/index.md" does not contain "By AI"

  Scenario: A story the bots drafted and a person is named as the author of names that person with the bots
    A human named in the authors of an AI-drafted story joins the byline even when no editor approval is recorded.
    Then the byline of a story drafted by an agent whose author is "Ryan Porter" reads "By various bots and Ryan Porter"
    And the byline of a story drafted by an agent approved by "Ada Reader" with author "Sam Rivera" reads "By various bots and Ada Reader and Sam Rivera"

  Scenario: A post has no byline anywhere, and an article keeps its byline
    Nobody writes a post, so a byline on one makes no sense. The post's page and its Markdown twin name no author. An article still says who made it.
    When I open the page "/posts/synthetic-security-post-2/"
    Then the page does not contain "By various bots"
    And the file "posts/synthetic-security-post-2/index.md" does not contain "By various bots"
    When I open the page "/field-notes/the-agents-are-writing-the-benchmarks-now/"
    Then the page contains "By various bots and Ada Reader"
