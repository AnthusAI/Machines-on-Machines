::band{size="bare"}

::raw
<div class="mom-page mom-home rh-home mom-section-front" data-section="ai-safety">
::endraw

::include{kind="block" name="section-top" section="ai-safety" depends="ai-safety"}

::raw
<div class="mom-home-top rh-top">
<div class="mom-home-lead">
::endraw

::include{kind="listing" type="article" section="ai-safety" count="1" card="lead" layout="bare"}

::raw
</div>
<div class="mom-home-side">
::endraw

::include{kind="block" name="section-sticker" section="ai-safety" depends="ai-safety"}

::raw
<section class="mom-home-rail" aria-labelledby="mom-conversations-rail">
<div class="mom-section-head"><h2 id="mom-conversations-rail" class="mom-section-title">Conversations</h2><a class="mom-section-link" href="/conversations/">All conversations</a></div>
<!--sf:conversations-->
::endraw

::include{kind="threads" select="recent" count="500" layout="list"}

::raw
<!--/sf:conversations-->
</section>
</div>
</div>
<div class="mom-story-grid mom-sf-cards">
::endraw

::include{kind="listing" type="article" section="ai-safety" skip="1" count="12" layout="bare"}

::raw
</div>
::endraw

::include{kind="block" name="section-more" part="articles" shown="13" section="ai-safety" depends="ai-safety"}

::raw
<div class="rh-mosaic mom-sf-videos">
<!--sf:videos:6-->
::endraw

::include{kind="references" select="confident" bucket="week" medium="video" section="Safety & Alignment" count="7" heading="Worth Watching" counts="true"}

::raw
<!--/sf:videos-->
</div>
<div class="mom-sf-findings">
<!--sf:findings:3-->
::endraw

::include{kind="references" select="recent" bucket="week" section="Safety & Alignment" count="24"}

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

::include{kind="block" name="section-heading" part="posts" section="ai-safety" depends="ai-safety"}

::raw
<div class="rh-mosaic mom-sf-post-grid">
::endraw

::include{kind="listing" type="post" section="ai-safety" count="12" card="post" layout="bare"}

::raw
</div>
::endraw

::include{kind="block" name="section-more" part="posts" shown="12" section="ai-safety" depends="ai-safety"}

::raw
</section>
</div>
</div>
::endraw
