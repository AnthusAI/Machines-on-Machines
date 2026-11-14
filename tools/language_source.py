"""A synthetic multilingual site for the preview and the tests: Papyrus's own projection over a directory of Markdown files that carry their language.

Papyrus reads published Stories with their `language` and `languageGroupId` from the CMS. A content directory has neither, so this source adds them from the front matter
(`language: es-419`, and `languageGroup: <slug of the original>` on a translation) and says which languages the site serves, in the shape of the editorial settings'
`languages` (`primary`, `enabled`, `prefixes`, `public`; see docs/multilingual-serving.md in the Papyrus repository). Everything else is the engine's: the editions, the
language groups, `page.alternates`, `page.link_map`, `hreflang`, the sitemaps and the listings of each language. No language data is written by hand.

    python3 tools/language_source.py CONTENT_DIR STATIC_DIR KNOWLEDGE_DIR OUT_DIR LANGUAGES_JSON
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yaml
from papyrus_content.language_serving import serving_languages
from papyrus_content.projection.directory_source import DirectoryContentSource, _split
from papyrus_content.projection.engine import ProjectionContext, project_all
from papyrus_content.projection.runtime import SITE_STATIC_DIRECTORY_ENV, load_projector
from papyrus_content.projection.writers import LocalDirectoryWriter
from papyrus_content.renditions import (
    DirectoryRenditionStore,
    PrefixedRenditionStore,
    base_path_from_static_directory,
    make_directory_renditions,
    media_originals_enabled,
    settings_from_static_directory,
)


class LanguageDirectorySource(DirectoryContentSource):
    """The directory source with each Story's language and language group, and the site's languages as the engine reads them from the CMS settings."""

    def __init__(self, content_directory: Path, languages: dict) -> None:
        super().__init__(content_directory)
        self._languages = languages

    def _load(self) -> dict[str, dict]:
        if self._rows is None:
            rows = super()._load()
            primary = self._languages["primary"]
            for row in rows.values():
                data = yaml.safe_load(row["metadata"]["frontMatterYaml"] or "") or {}
                row["language"] = str(data.get("language") or primary)
                group = data.get("languageGroup") or (row["slug"] if row["language"] == primary else None)
                row["languageGroupId"] = str(group) if group else None
        return self._rows

    def serving_languages(self):
        return serving_languages({"languages": self._languages})


def project_language_site(content: Path, static: Path, knowledge: Path, out: Path, languages: dict) -> None:
    """Project the directory as a multilingual site into `out`, as `papyrus ops content project --all --from-dir` does for a one-language site."""
    environment = {**os.environ, SITE_STATIC_DIRECTORY_ENV: str(static)}
    renditions = None
    settings = settings_from_static_directory(static)
    if settings is not None:
        renditions = DirectoryRenditionStore(out)
        make_directory_renditions(settings, PrefixedRenditionStore(renditions, base_path_from_static_directory(static)), content, originals=media_originals_enabled(static))
    projector = load_projector(environment, renditions=renditions)
    projector.use_knowledge_directory(knowledge)
    context = ProjectionContext(source=LanguageDirectorySource(content, languages), projector=projector, writer=LocalDirectoryWriter(out, ""), keep_state=False)
    report = project_all(context)
    for error in report.errors:
        print(f"error: {error}")
    if not report.ok:
        raise SystemExit(1)


if __name__ == "__main__":
    if len(sys.argv) != 6:
        raise SystemExit(__doc__)
    content, static, knowledge, out = (Path(argument) for argument in sys.argv[1:5])
    project_language_site(content, static, knowledge, out, json.loads(sys.argv[5]))
