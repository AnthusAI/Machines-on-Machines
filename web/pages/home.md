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
<div class="mom-side-stories">
::endraw

::include{kind="listing" types="article" skip="1" count="2" card="small" layout="bare"}

::raw
</div>
</div>
</div>

<section class="mom-section" aria-labelledby="mom-just-accepted">
<div class="mom-section-head">
<div><h2 id="mom-just-accepted" class="mom-section-title">Just accepted</h2><p class="mom-section-note">The newest sources our editors and Cyclotron said belong here.</p></div>
<a class="mom-section-link" href="/wire/">The whole wire</a>
</div>
::endraw

::include{kind="references" select="recent" count="3" empty="Nothing has been accepted yet."}

::raw
</section>

<section class="mom-section" aria-label="More stories">
<div class="mom-story-grid">
::endraw

::include{kind="listing" types="article" skip="3" count="3" card="story" layout="bare"}

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
</div>
::endraw

::include{kind="block" name="loop-band" role="brand"}

::raw
<div class="mom-page mom-home">
<div class="mom-home-pair">
<section class="mom-panel mom-panel-machine" aria-labelledby="mom-recommends">
<div class="mom-section-head"><div><h2 id="mom-recommends" class="mom-section-title">Cyclotron recommends</h2><p class="mom-section-note">Not accepted yet. Cyclotron expects an editor to say yes.</p></div></div>
::endraw

::include{kind="references" select="recommended" count="3" empty="Nothing is waiting for an editor."}

::raw
</section>
<section class="mom-panel mom-panel-plain" aria-labelledby="mom-proposals">
<div class="mom-section-head"><div><h2 id="mom-proposals" class="mom-section-title">Proposals</h2><p class="mom-section-note">What the AI wants to publish or change, waiting for editors.</p></div><a class="mom-section-link" href="/proposals/">All proposals</a></div>
<p class="mom-placeholder-note"><span class="mom-chip mom-chip-quiet">Placeholder</span> These rows show the design. Real proposals appear when the proposals feed is switched on.</p>
::endraw

::include{kind="block" name="proposal-rows"}

::raw
</section>
</div>
</div>
::endraw
