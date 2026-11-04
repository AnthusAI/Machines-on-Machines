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
<section class="mom-home-rail" aria-labelledby="mom-recent-findings">
<div class="mom-section-head">
<div><h2 id="mom-recent-findings" class="mom-section-title">Recent findings</h2></div>
<a class="mom-section-link" href="/wire/">See the whole reading list</a>
</div>
::endraw

::include{kind="references" select="recent" count="6" empty="Nothing has been accepted yet."}

::raw
</section>
</div>
</div>

<section class="mom-section" aria-label="More stories">
<div class="mom-story-grid">
::endraw

::include{kind="listing" types="article" skip="1" count="6" card="story" layout="bare"}

::raw
</div>
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
<section class="mom-panel mom-panel-machine mom-section" aria-labelledby="mom-up-for-consideration">
<div class="mom-section-head"><div><h2 id="mom-up-for-consideration" class="mom-section-title">Up for consideration</h2><p class="mom-section-note">Not accepted yet. Our AI thinks an editor will say yes.</p></div></div>
::endraw

::include{kind="references" select="recommended" count="6" empty="Nothing is waiting for an editor."}

::raw
</section>
</div>
::endraw

::include{kind="block" name="loop-band" role="brand"}
