::band{size="bare"}

::raw
<div class="mom-page mom-wire">
<header class="mom-page-head">
<h1 class="mom-page-title">Findings</h1>
<p class="mom-dek">Every source our editors and Cyclotron have accepted, newest first. Each card says who accepted it.</p>
</header>
<section class="mom-section" aria-labelledby="mom-wire-accepted">
<h2 id="mom-wire-accepted" class="mom-section-title">Accepted</h2>
::endraw

::include{kind="references" select="recent" count="500" empty="Nothing has been accepted yet."}

::raw
</section>
<section class="mom-panel mom-panel-machine" aria-labelledby="mom-wire-recommended">
<div class="mom-section-head"><div><h2 id="mom-wire-recommended" class="mom-section-title">Not accepted yet</h2><p class="mom-section-note">Cyclotron expects an editor to accept these. Highest confidence first.</p></div></div>
::endraw

::include{kind="references" select="recommended" count="500" empty="Nothing is waiting for an editor."}

::raw
</section>
</div>
::endraw
