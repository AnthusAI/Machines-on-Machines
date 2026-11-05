::band{size="bare"}

::raw
<div class="mom-page mom-wire mom-videos">
::endraw

::include{kind="block" name="page-top" title="Videos" lead="Videos we think are worth watching."}

::raw
<section class="mom-section" aria-labelledby="mom-videos-accepted">
<h2 id="mom-videos-accepted" class="mom-section-title">Accepted</h2>
::endraw

::include{kind="references" select="recent" bucket="week" medium="video" count="500" empty="No videos have been accepted yet."}

::raw
</section>
<section class="mom-panel mom-panel-machine" aria-labelledby="mom-videos-recommended">
<div class="mom-section-head"><div><h2 id="mom-videos-recommended" class="mom-section-title">Not accepted yet</h2><p class="mom-section-note">Cyclotron expects an editor to accept these. Highest confidence first.</p></div></div>
::endraw

::include{kind="references" select="recommended" medium="video" count="500" empty="No videos are waiting for an editor."}

::raw
</section>
</div>
::endraw
