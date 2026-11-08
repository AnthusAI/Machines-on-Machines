::band{size="bare"}

::raw
<div class="mom-page mom-wire mom-refs-page" data-list-kind="findings">
::endraw

::include{kind="block" name="page-top" title="Findings" lead="Every source our editors and Cyclotron have accepted. Each card says who accepted it."}

::raw
<!--sf:refs-lead:4-->
<div class="mom-by-section" data-source-count="500">
::endraw

::include{kind="references" select="recent" bucket="week" count="500"}

::raw
</div>
::endraw

::raw
<section class="mom-section mom-refs-stream" data-noun="findings" aria-label="More findings">
<!--sf:refs-stream-->
::endraw

::include{kind="references" select="recent" bucket="week" count="64" paged="true" id="untagged" empty="Nothing has been accepted yet."}

::raw
<!--/sf:refs-stream-->
</section>
</div>
::endraw
