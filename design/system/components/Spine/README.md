The full-height navy `brand` column on the right edge of article and wiki pages: home link at the top, section name down the middle, reading progress rising in `brand-progress`, a lighter navy the section name stays readable over.

- **Provide**: `subject` (the article's section, or `Meaning` on wiki pages), `progress` from 0 to 1 computed from the reader's scroll position, and `homeHref` / `sectionHref`.
- **Container**: a flex row with the scrolling content first and the spine last; the spine stays fixed while the content scrolls and needs the full viewport height.
- The fill is `brand-progress`, a lighter navy, so the section name stays readable over it. Update it without animation under reduced motion.
- Keep the spine on the right. Content leads from the left edge; the brand comes second.
- At phone width, collapse it to a band across the top of the page with the inline wordmark and the section name.
