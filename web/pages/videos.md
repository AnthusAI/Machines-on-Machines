::band{size="bare"}

::raw
<div class="mom-page mom-wire mom-videos mom-refs-page">
::endraw

::include{kind="block" name="page-top" title="Videos" lead="Videos we think are worth watching."}

::raw
<div class="mom-by-section">
::endraw

::include{kind="references" select="recent" bucket="week" medium="video" count="500" empty="No videos have been accepted yet."}

::raw
</div>
<section class="mom-panel mom-panel-machine" aria-labelledby="mom-videos-recommended">
<div class="mom-section-head"><div><h2 id="mom-videos-recommended" class="mom-section-title">Not accepted yet</h2><p class="mom-section-note">Cyclotron expects an editor to accept these. Highest confidence first.</p></div></div>
<div class="mom-by-rows">
::endraw

::include{kind="references" select="recommended" medium="video" count="500" empty="No videos are waiting for an editor."}

::raw
</div>
</section>
</div>
::endraw
