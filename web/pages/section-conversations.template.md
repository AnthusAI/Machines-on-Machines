::band{size="bare"}

::raw
<div class="mom-page mom-conversations mom-board-page" data-section="@ID@">
::endraw

::include{kind="block" name="page-top" title="@LABEL@ conversations" lead="Editors and AI discussing @LABEL@ stories and sources." card="none"}

::raw
<!--sf:forum-->
::endraw

::include{kind="threads" select="recent" section="@LABEL@" count="100000" layout="list" empty="No conversations in @LABEL@ yet."}

::raw
<!--/sf:forum-->
</div>
::endraw
