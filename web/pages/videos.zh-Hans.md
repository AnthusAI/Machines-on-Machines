::band{size="bare"}

::raw
<div class="mom-page mom-wire mom-videos mom-refs-page" data-list-kind="videos">
::endraw

::include{kind="block" name="page-top" halftone="true" title="视频" lead="我们认为值得一看的视频。"}

::raw
<p class="mom-original-notice">本页的内容保持原文语言：英文。</p>
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
<section class="mom-section mom-refs-stream" data-noun="视频" aria-label="更多视频">
<!--sf:refs-stream-->
::endraw

::include{kind="references" select="recent" bucket="week" medium="video" minStars="3" count="64" paged="true" id="untagged" empty="目前还没有接受任何视频。"}

::raw
<!--/sf:refs-stream-->
</section>
</div>
::endraw
