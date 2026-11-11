::band{size="bare"}

::raw
<div class="mom-page mom-home rh-home">
<div class="mom-section-head rh-label"><h2 class="mom-section-title">Top Articles</h2></div>
<div class="mom-home-top rh-top">
<div class="mom-home-lead">
::endraw

::include{kind="listing" type="article" fallback="post" count="1" card="lead" layout="bare" unique="true"}

::raw
</div>
<div class="mom-home-side">
::endraw

::include{kind="block" name="sticker"}

::include{kind="block" name="halftone"}

::raw
</div>
</div>
<div class="rh-features">
::endraw

::include{kind="listing" type="article" sections="10" per="3,3,3,2" card="large" heading="true" class="rh-group" unique="true"}

::raw
</div>
</div>
::endraw

::include{kind="block" name="loop-band" role="machine"}

::include{kind="block" name="loop-band" role="machine"}

::raw
<div class="mom-page mom-home rh-home">
<section class="mom-section rh-posts" aria-labelledby="mom-latest-posts">
<div class="mom-section-head"><div><h2 id="mom-latest-posts" class="mom-section-title">Latest Posts</h2><p class="mom-section-note">Shorter pieces, quick to read.</p></div><a class="mom-section-link" href="/posts/">All posts</a></div>
::endraw

::include{kind="listing" type="post" count="12" card="brief" layout="bare" tag="div" class="rh-brief-list" unique="true"}

::raw
</section>
</div>
::endraw


::raw
<div class="mom-page mom-home rh-home mom-home-ad">
::endraw

::include{kind="block" name="ad" unit="band" placement="home-band"}

::raw
</div>
::endraw

::raw
<!--home:videos-->
::endraw

::include{kind="references" select="confident" bucket="week" medium="video" count="12"}

::raw
<!--/home:videos-->
::endraw

::raw
<div class="mom-page mom-home rh-home">
<section class="mom-section rh-findings" aria-label="Findings">
::endraw

::include{kind="references" select="confident" bucket="week" count="40" heading="Findings" more="/findings/" counts="true"}

::raw
</section>
</div>
::endraw

::raw
<!--home:conversations-->
::endraw

::include{kind="threads" select="recent" count="6" layout="list"}

::raw
<!--/home:conversations-->
::endraw

::include{kind="block" name="home-concepts"}
