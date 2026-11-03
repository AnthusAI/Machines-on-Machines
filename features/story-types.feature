Feature: Post is the default Story type
  Editors write posts. A new Story is a post and is published under /posts/. Articles stay
  offered because earlier ideas are typed article, but they get no address of their own.

  Scenario: The newsroom offers post and article with post as the default
    Given the publication's projection settings
    Then new Stories default to the type "post"
    And the newsroom offers the types "post" and "article"

  Scenario: Posts have a public address and articles do not
    Given the publication's projection settings
    Then the type "post" is published under "/posts/"
    And the type "article" has no address of its own
