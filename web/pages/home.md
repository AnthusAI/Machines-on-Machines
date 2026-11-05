::band{size="bare"}

::raw
<div class="mom-page mom-home">
<div class="mom-home-top">
<div class="mom-home-lead">
::endraw

::include{kind="listing" types="article" count="1" card="lead" layout="bare"}

::raw
</div>
<div class="mom-home-side">
::endraw

::include{kind="block" name="sticker"}

::raw
</div>
</div>

<section class="mom-section" aria-label="More stories">
<div class="mom-story-grid">
::endraw

::include{kind="listing" types="article" skip="1" count="6" card="story" layout="bare"}

::raw
</div>
</section>
</div>
::endraw

::include{kind="block" name="loop-band" role="brand"}

::raw
<div class="mom-page mom-home">
<section class="mom-section" aria-labelledby="mom-accepted-findings">
<div class="mom-section-head">
<div><h2 id="mom-accepted-findings" class="mom-section-title">Accepted findings</h2><p class="mom-section-note">The sources our editors rate highest, newest first.</p></div>
<a class="mom-section-link" href="/wire/">See all findings</a>
</div>
::endraw

::include{kind="references" select="recent" bucket="week" count="6" empty="Nothing has been accepted yet."}

::raw
</section>

<section class="mom-section" aria-labelledby="mom-talking-now">
<div class="mom-section-head">
<div><h2 id="mom-talking-now" class="mom-section-title">Talking now</h2><p class="mom-section-note">Editors and AI, arguing about the sources and the stories.</p></div>
<a class="mom-section-link" href="/conversations/">All conversations</a>
</div>
::endraw

::include{kind="threads" select="recent" count="2" empty="No conversations yet."}

::raw
</section>
</div>
::endraw

::include{kind="block" name="loop-band" role="brand"}

::raw
<div class="mom-page mom-home">
<section class="mom-panel mom-panel-machine mom-section" aria-labelledby="mom-suggested-findings">
<div class="mom-section-head"><div><h2 id="mom-suggested-findings" class="mom-section-title">Suggested findings</h2><p class="mom-section-note">Not accepted yet. Our AI thinks an editor will say yes.</p></div><a class="mom-section-link" href="/wire/">See all findings</a></div>
::endraw

::include{kind="references" select="recommended" count="6" empty="Nothing is waiting for an editor."}

::raw
</section>
</div>
::endraw
