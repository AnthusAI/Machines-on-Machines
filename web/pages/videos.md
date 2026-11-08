::band{size="bare"}

::raw
<div class="mom-page mom-wire mom-videos mom-refs-page" data-list-kind="videos">
::endraw

::include{kind="block" name="page-top" title="Videos" lead="Videos we think are worth watching."}

::raw
<!--sf:refs-lead:4-->
<div class="mom-by-section" data-source-count="500">
::endraw

::include{kind="references" select="recent" bucket="week" medium="video" count="500"}

::raw
</div>
::endraw

::raw
<section class="mom-section mom-refs-stream" data-noun="videos" aria-label="More videos">
<!--sf:refs-stream-->
::endraw

::include{kind="references" select="recent" bucket="week" medium="video" count="64" paged="true" id="untagged" empty="No videos have been accepted yet."}

::raw
<!--/sf:refs-stream-->
</section>
</div>
::endraw
