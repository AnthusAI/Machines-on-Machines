Feature: Figures follow one written system
  Agents draw the figures, so the system has to catch mistakes without a designer in the room.
  Readers include people in their 80s on phones, in both themes, and people who can't tell colors apart.

  Scenario: Every gallery figure has a matching Day and Night picture
    Then every gallery figure has a Day picture and a Night picture with the same proportions
    And every gallery figure passes the source checks

  Scenario Outline: The checks refuse a figure that breaks a rule
    When the "<figure>" source has <change>
    Then the source checks report "<problem>"

    Examples:
      | figure         | change                    | problem    |
      | wiped-board    | a raw color               | raw color  |
      | wiped-board    | navy in it                | brand navy |
      | wiped-board    | a second focal mark       | focal      |
      | wall-and-climb | its stamp removed         | stamp      |

  Scenario: A forecast never looks like data
    Then the "wall-and-climb" figure carries the stamp "FORECAST, NOT DATA"
    And the "wall-and-climb" figure shows no numbers

  Scenario: A scenario that could pass for fact says so
    Then the "search-nobody-sees" figure carries the stamp "SCENARIO"

  Scenario: A scene-setting illustration carries no stamp
    Then the "parked-car" figure carries no stamp

  Scenario: A figure credits its sources, not who drew or approved it
    Then the credit of the "wiped-board" figure reads "Source: METR; OpenAI."
    And the "parked-car" figure has no credit line

  Scenario: A data chart has a plain title, an axis line, ticks, units and direct labels
    Then the figure rules give a data chart a plain title, an axis line, ticks, units and direct labels

  Scenario: Our own drawn images carry no visible credit and approval lives in metadata only
    Then the figure rules prescribe no visible credit for who drew or approved a figure

  Scenario: A caption says something about the article or is left out
    Then the figure rules make the caption optional and forbid a caption that only names the kind of picture
    And the "parked-car" figure has no imagined-scene caption

  Scenario: The diagram-design guide is built from the rules
    Then the figure style guide is current

  Scenario: A figure fills the article column on a phone
    Then the site theme removes the browser's figure margin and fits the picture to the column
