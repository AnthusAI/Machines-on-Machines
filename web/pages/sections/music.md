::band{size="bare"}

::raw
<div class="mom-page mom-section-page mom-section-front" data-section="music">
::endraw

::include{kind="block" name="section-top" section="music" depends="music"}

::raw
<div class="mom-sf-grid">
<div class="mom-sf-main">
<section class="mom-sf-block mom-sf-articles" aria-label="Articles">
::endraw

::include{kind="block" name="section-heading" part="articles" section="music" depends="music"}
::include{kind="listing" type="article" section="music" count="1" card="lead" layout="bare"}
::include{kind="listing" type="article" section="music" skip="1" count="12" layout="bare" tag="div" class="mom-story-grid mom-sf-cards"}
::include{kind="block" name="section-more" part="articles" shown="13" section="music" depends="music"}

::raw
</section>
<div class="mom-sf-block mom-sf-videos" role="region" aria-label="Videos">
<!--sf:videos:4-->
::endraw

::include{kind="references" select="confident" bucket="week" medium="video" section="Music" count="5"}

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

::include{kind="block" name="section-heading" part="posts" section="music" depends="music"}
::include{kind="listing" type="post" section="music" count="8" card="line" layout="bare" tag="div" class="mom-sf-lines"}
::include{kind="block" name="section-more" part="posts" shown="8" section="music" depends="music"}

::raw
</aside>
</div>
</div>
</div>
::endraw
