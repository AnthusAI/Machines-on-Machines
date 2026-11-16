::band{size="bare"}

::raw
<div class="mom-page mom-wire @CLASSES@mom-refs-page" data-list-kind="@KIND@">
::endraw

::include{kind="block" name="page-top"@HALFTONE@ title="@TITLE@" lead="@LEAD@"}

@@if notice
::raw
<p class="mom-original-notice">@NOTICE@</p>
::endraw

@@end
::raw
<!--sf:refs-lead:@LEAD_CARDS@-->
@@if groups
<div class="mom-by-section" data-source-count="@SOURCE_COUNT@">
@@end
::endraw

@@if groups
::include{kind="references" select="recent" bucket="week"@MEDIUM@ count="@SOURCE_COUNT@"}

::raw
</div>
::endraw

@@end
::raw
<section class="mom-section mom-refs-stream" data-noun="@NOUN@" aria-label="@MORE_LABEL@">
<!--sf:refs-stream-->
::endraw

::include{kind="references" select="recent" bucket="week"@MEDIUM@@SECTION@ count="@PAGE_COUNT@" paged="true" id="@LIST_ID@" empty="@EMPTY@"}

::raw
<!--/sf:refs-stream-->
</section>
</div>
::endraw
