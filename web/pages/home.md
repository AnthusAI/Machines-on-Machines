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

::raw
<section class="mom-home-rail" aria-labelledby="mom-conversations-rail">
<div class="mom-section-head"><h2 id="mom-conversations-rail" class="mom-section-title">Conversations</h2><a class="mom-section-link" href="/conversations/">All conversations</a></div>
::endraw

::include{kind="threads" select="recent" count="8" layout="list"}

::raw
</section>
</div>
</div>
<div class="rh-features">
::endraw

::include{kind="listing" type="article" fallback="post" sections="3" per="2,1" card="large" heading="true" class="rh-group" unique="true"}

::include{kind="references" select="confident" medium="video" count="3" heading="Worth Watching" more="/videos/" counts="true"}

::raw
</div>
</div>
::endraw

::include{kind="block" name="loop-band" role="machine"}

::raw
<div class="mom-page mom-home rh-home">
<section class="mom-section rh-latest" aria-labelledby="mom-latest-posts">
<div class="mom-section-head"><h2 id="mom-latest-posts" class="mom-section-title">Latest Posts</h2></div>
<div class="rh-mosaic">
::endraw

::include{kind="listing" type="post" count="1" card="tile" layout="bare" unique="true"}
::include{kind="references" select="confident" medium="video" count="1" counts="true"}
::include{kind="listing" type="post" sections="3" per="2,1,1" card="large" heading="true" class="rh-panel" unique="true"}
::include{kind="references" select="confident" medium="video" count="2" heading="Worth Watching" more="/videos/" counts="true"}
::include{kind="references" select="confident" medium="video" count="1" counts="true"}
::include{kind="listing" type="post" count="1" card="tile" layout="bare" unique="true"}

::raw
</div>
</section>
</div>
::endraw

::include{kind="block" name="loop-band" role="machine"}

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
<div class="mom-page mom-home rh-home mom-home-ad">
::endraw

::include{kind="block" name="ad" unit="band" placement="home-band"}

::raw
</div>
::endraw
