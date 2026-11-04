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

  Scenario: Invented scenes say so
    Then the "search-nobody-sees" figure carries the stamp "INVENTED EXAMPLE"
    And the "parked-car" figure carries the stamp "INVENTED SCENE"

  Scenario: A figure is not marked approved until a person confirms it
    Then no gallery figure names an approver

  Scenario: The diagram-design guide is built from the rules
    Then the figure style guide is current

  Scenario: A figure fills the article column on a phone
    Then the site theme removes the browser's figure margin and fits the picture to the column
