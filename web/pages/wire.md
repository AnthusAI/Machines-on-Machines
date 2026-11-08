::band{size="bare"}

::raw
<div class="mom-page mom-wire mom-refs-page">
::endraw

::include{kind="block" name="page-top" title="Findings" lead="Every source our editors and Cyclotron have accepted, by section. Each card says who accepted it."}

::raw
<div class="mom-by-section">
::endraw

::include{kind="references" select="recent" bucket="week" count="500"}

::raw
</div>
::endraw

::raw
<section class="mom-section mom-untagged" data-noun="findings" aria-label="Findings">
<!--sf:untagged-heading-->
::endraw

::include{kind="references" select="recent" bucket="week" count="24" paged="true" id="untagged" empty="Nothing has been accepted yet."}

::raw
<!--/sf:untagged-->
</section>
::endraw

::raw
<section class="mom-panel mom-panel-machine" aria-labelledby="mom-wire-recommended">
<div class="mom-section-head"><div><h2 id="mom-wire-recommended" class="mom-section-title">Found by machines</h2><p class="mom-section-note">Cyclotron expects an editor to accept these. Highest confidence first.</p></div></div>
::endraw

::include{kind="references" select="recommended" count="24" paged="true" id="recommended" empty="Nothing is waiting for an editor."}

::raw
</section>
::endraw

::raw
</div>
::endraw
