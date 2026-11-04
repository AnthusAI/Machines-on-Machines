Feature: Post is the default Story type
  Editors write posts. A new Story is a post and is published under /posts/. An editor can make
  a Story an article, which is published under /articles/.

  Scenario: The newsroom offers post and article with post as the default
    Given the publication's projection settings
    Then new Stories default to the type "post"
    And the newsroom offers the types "post" and "article"

  Scenario: Posts and articles each have a public address
    Given the publication's projection settings
    Then the type "post" is published under "/posts/"
    And the type "article" is published under "/articles/"

  Scenario: Articles can carry pictures and citations
    Then the site turns on images and citations
