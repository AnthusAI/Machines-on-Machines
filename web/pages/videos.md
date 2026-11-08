::band{size="bare"}

::raw
<div class="mom-page mom-wire mom-videos mom-refs-page">
::endraw

::include{kind="block" name="page-top" title="Videos" lead="Videos we think are worth watching."}

::raw
<div class="mom-by-section">
::endraw

::include{kind="references" select="recent" bucket="week" medium="video" count="500"}

::raw
</div>
::endraw

::raw
<section class="mom-section mom-untagged" data-noun="videos" aria-label="Videos">
<!--sf:untagged-heading-->
::endraw

::include{kind="references" select="recent" bucket="week" medium="video" count="24" paged="true" id="untagged" empty="No videos have been accepted yet."}

::raw
<!--/sf:untagged-->
</section>
::endraw

::raw
<section class="mom-panel mom-panel-machine" aria-labelledby="mom-videos-recommended">
<div class="mom-section-head"><div><h2 id="mom-videos-recommended" class="mom-section-title">Not accepted yet</h2><p class="mom-section-note">Cyclotron expects an editor to accept these. Highest confidence first.</p></div></div>
::endraw

::include{kind="references" select="recommended" medium="video" count="24" paged="true" id="recommended" empty="No videos are waiting for an editor."}

::raw
</section>
::endraw

::raw
</div>
::endraw
