Feature: A video rated two stars or lower stays out of every public video index
  An editor can rate a video two stars or lower to keep it out of every public video index while an article or post that links to it keeps its link. The
  indexes are the home page's Worth Watching panel and Videos section, the Videos page with every page of its list, each section's Worth Watching panel and
  each section's own list of videos (`/<section>/videos/`). A rating of three or higher, and no rating at all, leave a video eligible under the existing
  ordering rules. The rating is applied to the candidates before any slot or page is counted, so a low-rated video takes no slot and no page, the lists
  reach every eligible video once without a gap or a duplicate, and a list with fewer eligible videos than its capacity stays shorter. Only video indexes
  are filtered: the video stays accepted in the snapshot, and the direct links of articles and posts to it are unchanged. The "rated" case has 80 videos
  filed under Privacy & Security and unfiled alternately, the newest 12 rated one or two stars, then one rated three and one rated four.

  Background:
    Given the "rated" Reference case is projected

  Scenario: A rating of two or lower excludes a video from every public video index
    Then the videos rated two stars or lower are absent from the home page, "/videos/", every page of its list, "/security/", "/security/videos/" and every page of its list
    And the videos rated two stars or lower are still accepted in the snapshot

  Scenario: A rating of three or higher leaves a video eligible
    When I open the case page "/videos/"
    Then the videos rated three and four stars are on the page in the shared order

  Scenario: Filtering does not starve the Videos page: every eligible video is reachable once
    When I open the case page "/videos/"
    Then the lead and the list reach all 34 videos exactly once
    And the lists contain no video rated two stars or lower

  Scenario: Filtering does not starve a section's list: every eligible video filed under it is reachable once, in order
    When I open the case page "/security/videos/"
    Then the lead and the list reach all 34 videos filed under "Privacy & Security" exactly once
    And the lists contain no video rated two stars or lower

  Scenario: A section's Worth Watching panel shows eligible videos only and stays shorter when too few remain
    When I open the case page "/security/"
    Then the Worth Watching panel has videos and none of them is rated two stars or lower

  Scenario: A direct editorial link to a video rated two stars or lower is preserved
    Then the article "an-article-that-links-a-video-rated-two-stars" links directly to a video rated two stars or lower
    And that video is absent from "/videos/"
