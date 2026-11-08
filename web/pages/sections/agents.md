::band{size="bare"}

::raw
<div class="mom-page mom-home rh-home mom-section-front" data-section="agents">
::endraw

::include{kind="block" name="section-top" section="agents" depends="agents"}

::raw
<div class="mom-home-top rh-top">
<div class="mom-home-lead">
::endraw

::include{kind="listing" type="article" section="agents" count="1" card="lead" layout="bare"}

::raw
</div>
<div class="mom-home-side">
::endraw

::include{kind="block" name="section-sticker" section="agents" depends="agents"}

::raw
<section class="mom-home-rail" aria-labelledby="mom-conversations-rail">
<div class="mom-section-head"><h2 id="mom-conversations-rail" class="mom-section-title">Conversations</h2><a class="mom-section-link" href="/agents/conversations/">All conversations</a></div>
<!--sf:conversations-->
::endraw

::include{kind="threads" select="recent" section="Agents" count="500" layout="list"}

::raw
<!--/sf:conversations-->
</section>
</div>
</div>
<div class="mom-story-grid mom-sf-cards">
::endraw

::include{kind="listing" type="article" section="agents" skip="1" count="12" layout="bare"}

::raw
</div>
::endraw

::include{kind="block" name="section-more" part="articles" shown="13" section="agents" depends="agents"}

::raw
<div class="rh-mosaic mom-sf-videos">
<!--sf:videos:6-->
::endraw

::include{kind="references" select="confident" bucket="week" medium="video" section="Agents" count="7" heading="Worth Watching" counts="true"}

::raw
<!--/sf:videos-->
</div>
<div class="mom-sf-findings">
<!--sf:findings:3-->
::endraw

::include{kind="references" select="recent" bucket="week" section="Agents" count="24"}

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

::include{kind="block" name="section-heading" part="posts" section="agents" depends="agents"}

::raw
<div class="rh-mosaic mom-sf-post-grid">
::endraw

::include{kind="listing" type="post" section="agents" count="12" card="post" layout="bare"}

::raw
</div>
::endraw

::include{kind="block" name="section-more" part="posts" shown="12" section="agents" depends="agents"}

::raw
</section>
</div>
</div>
::endraw
