::band{size="bare"}

::raw
<div class="mom-page mom-section-page mom-section-front" data-section="full-self-driving">
::endraw

::include{kind="block" name="section-top" section="full-self-driving" depends="full-self-driving"}

::raw
<div class="mom-sf-grid">
<div class="mom-sf-main">
<section class="mom-sf-block mom-sf-articles" aria-label="Articles">
::endraw

::include{kind="block" name="section-heading" part="articles" section="full-self-driving" depends="full-self-driving"}
::raw
<div class="mom-story-grid mom-sf-cards">
::endraw
::include{kind="listing" type="article" section="full-self-driving" count="1" card="lead" layout="bare"}
::include{kind="listing" type="article" section="full-self-driving" skip="1" count="12" layout="bare"}
::raw
</div>
::endraw
::include{kind="block" name="section-more" part="articles" shown="13" section="full-self-driving" depends="full-self-driving"}

::raw
</section>
<div class="mom-sf-block mom-sf-videos" role="region" aria-label="Videos">
<!--sf:videos:6-->
::endraw

::include{kind="references" select="confident" bucket="week" medium="video" section="Full Self Driving" count="7"}

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

::include{kind="block" name="section-heading" part="posts" section="full-self-driving" depends="full-self-driving"}
::include{kind="listing" type="post" section="full-self-driving" count="8" card="line" layout="bare" tag="div" class="mom-sf-lines"}
::include{kind="block" name="section-more" part="posts" shown="8" section="full-self-driving" depends="full-self-driving"}

::raw
</aside>
</div>
</div>
</div>
::endraw
