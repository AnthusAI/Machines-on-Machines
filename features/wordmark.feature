Feature: "On" is the biggest word in the wordmark
  The wordmark is MACHINES ON MACHINES in Anton. "On" is the biggest word, stamped in a tilted
  seal that sits behind the words: it may overlap MACHINES, but it never covers a letter. The
  proportion is the same in every layout, from the nav pill to the sticker.

  Background:
    Given the Machines on Machines site is projected from the fixtures

  Scenario: "On" is set larger than MACHINES
    Then the stylesheet "assets/mom-tokens.css" sets "wordmark-on-scale" above 1em

  Scenario: The seal never covers the words
    Then in the stylesheet "assets/mom-components.css" the wordmark seal is drawn behind the words

  Scenario: Every page carries the wordmark
    When I open the page "/"
    Then the page contains "mom-wordmark-on"
