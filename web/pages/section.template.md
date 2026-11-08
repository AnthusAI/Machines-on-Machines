::band{size="bare"}

::raw
<div class="mom-page mom-home rh-home mom-section-front" data-section="@ID@">
::endraw

::include{kind="block" name="section-top" section="@ID@" depends="@ID@"}

::raw
<div class="mom-home-top rh-top">
<div class="mom-home-lead">
::endraw

::include{kind="listing" type="article" section="@ID@" count="1" card="lead" layout="bare"}

::raw
</div>
<div class="mom-home-side">
::endraw

::include{kind="block" name="section-sticker" section="@ID@" depends="@ID@"}

::raw
<section class="mom-home-rail" aria-labelledby="mom-conversations-rail">
<div class="mom-section-head"><h2 id="mom-conversations-rail" class="mom-section-title">Conversations</h2><a class="mom-section-link" href="/@ID@/conversations/">All conversations</a></div>
<!--sf:conversations-->
::endraw

::include{kind="threads" select="recent" section="@LABEL@" count="500" layout="list"}

::raw
<!--/sf:conversations-->
</section>
</div>
</div>
<div class="mom-story-grid mom-sf-cards">
::endraw

::include{kind="listing" type="article" section="@ID@" skip="1" count="@ARTICLE_CARDS@" layout="bare"}

::raw
</div>
::endraw

::include{kind="block" name="section-more" part="articles" shown="@ARTICLES_SHOWN@" section="@ID@" depends="@ID@"}

::raw
<div class="rh-mosaic mom-sf-videos">
<!--sf:videos:@VIDEO_CARDS@-->
::endraw

::include{kind="references" select="confident" bucket="week" medium="video" section="@LABEL@" count="@VIDEO_FETCH@" heading="Worth Watching" counts="true"}

::raw
<!--/sf:videos-->
</div>
<div class="mom-sf-findings">
<!--sf:findings:@FINDING_CARDS@-->
::endraw

::include{kind="references" select="recent" bucket="week" section="@LABEL@" count="@FINDING_FETCH@"}

::raw
<!--/sf:findings-->
</div>
</div>
<div class="mom-sf-posts-block">
::endraw

::include{kind="block" name="loop-band" role="machine"}

::raw
<div class="mom-page mom-home rh-home">
<section class="mom-section rh-latest mom-sf-posts" aria-label="Posts">
::endraw

::include{kind="block" name="section-heading" part="posts" section="@ID@" depends="@ID@"}

::raw
<div class="rh-mosaic mom-sf-post-grid">
::endraw

::include{kind="listing" type="post" section="@ID@" count="@POST_CARDS@" card="post" layout="bare"}

::raw
</div>
::endraw

::include{kind="block" name="section-more" part="posts" shown="@POST_CARDS@" section="@ID@" depends="@ID@"}

::raw
</section>
</div>
</div>
::endraw
