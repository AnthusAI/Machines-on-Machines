::band{size="bare"}

::raw
<div class="mom-page mom-wire @CLASSES@mom-refs-page">
::endraw

::include{kind="block" name="page-top" title="@TITLE@" lead="@LEAD@"}

@@if groups
::raw
<div class="mom-by-section">
::endraw

::include{kind="references" select="recent" bucket="week"@MEDIUM@ count="500"}

::raw
</div>
::endraw

@@end
::raw
@@if groups
<section class="mom-section mom-untagged" data-noun="@NOUN@" aria-label="@TITLE@">
<!--sf:untagged-heading-->
@@end
@@if plain
<section class="mom-section mom-all-refs" aria-label="@TITLE@">
@@end
::endraw

::include{kind="references" select="recent" bucket="week"@MEDIUM@@SECTION@ count="24" paged="true" id="@LIST_ID@" empty="@EMPTY@"}

::raw
@@if groups
<!--/sf:untagged-->
@@end
</section>
::endraw

@@if recommended
::raw
<section class="mom-panel mom-panel-machine" aria-labelledby="mom-@SLUG@-recommended">
<div class="mom-section-head"><div><h2 id="mom-@SLUG@-recommended" class="mom-section-title">@RECOMMENDED_TITLE@</h2><p class="mom-section-note">Cyclotron expects an editor to accept these. Highest confidence first.</p></div></div>
::endraw

::include{kind="references" select="recommended"@MEDIUM@ count="24" paged="true" id="recommended" empty="@RECOMMENDED_EMPTY@"}

::raw
</section>
::endraw

@@end
::raw
</div>
::endraw
