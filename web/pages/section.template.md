::band{size="bare"}

::raw
<div class="mom-page mom-section-page mom-section-front" data-section="@ID@">
::endraw

::include{kind="block" name="section-top" section="@ID@" depends="@ID@"}

::raw
<div class="mom-sf-grid">
<div class="mom-sf-main">
<section class="mom-sf-block mom-sf-articles" aria-label="Articles">
::endraw

::include{kind="block" name="section-heading" part="articles" section="@ID@" depends="@ID@"}
::raw
<div class="mom-story-grid mom-sf-cards">
::endraw
::include{kind="listing" type="article" section="@ID@" count="1" card="lead" layout="bare"}
::include{kind="listing" type="article" section="@ID@" skip="1" count="@ARTICLE_CARDS@" layout="bare"}
::raw
</div>
::endraw
::include{kind="block" name="section-more" part="articles" shown="@ARTICLES_SHOWN@" section="@ID@" depends="@ID@"}

::raw
</section>
<div class="mom-sf-block mom-sf-videos" role="region" aria-label="Videos">
<!--sf:videos:@VIDEO_CARDS@-->
::endraw

::include{kind="references" select="confident" bucket="week" medium="video" section="@LABEL@" count="@VIDEO_FETCH@"}

::raw
<!--/sf:videos-->
</div>
</div>
<div class="mom-sf-side">
<div class="mom-sf-block mom-sf-conversations" role="region" aria-label="Conversations">
<!--sf:conversations-->
::endraw

::include{kind="threads" select="recent" count="500" layout="list"}

::raw
<!--/sf:conversations-->
</div>
<aside class="mom-sf-block mom-sf-posts" aria-label="Posts">
::endraw

::include{kind="block" name="section-heading" part="posts" section="@ID@" depends="@ID@"}
::include{kind="listing" type="post" section="@ID@" count="@POST_LINES@" card="line" layout="bare" tag="div" class="mom-sf-lines"}
::include{kind="block" name="section-more" part="posts" shown="@POST_LINES@" section="@ID@" depends="@ID@"}

::raw
</aside>
</div>
</div>
</div>
::endraw
