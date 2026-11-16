::band{size="bare"}

::raw
<div class="mom-page mom-wire mom-videos mom-refs-page" data-list-kind="videos">
::endraw

::include{kind="block" name="page-top" halftone="true" title="Videos" lead="Videos que creemos que vale la pena ver."}

::raw
<p class="mom-original-notice">Los elementos de esta página están en su idioma original, el inglés.</p>
::endraw

::raw
<!--sf:refs-lead:4-->
<div class="mom-by-section" data-source-count="500">
::endraw

::include{kind="references" select="recent" bucket="week" medium="video" minStars="3" count="500"}

::raw
</div>
::endraw

::raw
<section class="mom-section mom-refs-stream" data-noun="videos" aria-label="Más videos">
<!--sf:refs-stream-->
::endraw

::include{kind="references" select="recent" bucket="week" medium="video" minStars="3" count="64" paged="true" id="untagged" empty="Todavía no se ha aceptado ningún video."}

::raw
<!--/sf:refs-stream-->
</section>
</div>
::endraw
