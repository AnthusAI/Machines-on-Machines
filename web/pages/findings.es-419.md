::band{size="bare"}

::raw
<div class="mom-page mom-wire mom-refs-page" data-list-kind="findings">
::endraw

::include{kind="block" name="page-top" halftone="true" title="Hallazgos" lead="Cada fuente que nuestros editores y Cyclotron han aceptado. Cada tarjeta dice quién la aceptó."}

::raw
<p class="mom-original-notice">Los elementos de esta página están en su idioma original, el inglés.</p>
::endraw

::raw
<!--sf:refs-lead:4-->
<div class="mom-by-section" data-source-count="500">
::endraw

::include{kind="references" select="recent" bucket="week" count="500"}

::raw
</div>
::endraw

::raw
<section class="mom-section mom-refs-stream" data-noun="hallazgos" aria-label="Más hallazgos">
<!--sf:refs-stream-->
::endraw

::include{kind="references" select="recent" bucket="week" count="64" paged="true" id="untagged" empty="Todavía no se ha aceptado nada."}

::raw
<!--/sf:refs-stream-->
</section>
</div>
::endraw
