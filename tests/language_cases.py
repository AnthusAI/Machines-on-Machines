"""A fixture site that has translations, for the language features' tests.

The ordinary fixture site is English only. This case copies its content and adds Spanish and Chinese pages for one article ("How to steer a story": all three languages),
a Spanish page for another ("How to run a monitor": English and Spanish, no Chinese) and a Spanish Concept ("Agent evals"), and projects the site with Papyrus's own
multilingual projection (`tools/language_source.py`): the Stories carry their `language` and `languageGroup` in their front matter, as the CMS rows do, and the site
serves English, Spanish and Chinese publicly. The language groups, the editions under `/es/` and `/zh/`, `page.alternates`, `page.link_map`, `hreflang`, the sitemaps and the
language listings are the engine's, not the test's. Every other page has no translation, so it has no switcher and no banner.
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))

CONTENT = REPOSITORY_ROOT / "tests" / "fixtures" / "content"

# The site's `languages` setting (editorial check settings): what the public flip will set on the live site; the fixture site sets it so translations are served.
LANGUAGES = {"primary": "en", "enabled": ["en", "es-419", "zh-Hans"], "public": ["en", "es-419", "zh-Hans"]}

CHINESE_SLUG = "如何引导一篇报道"  # the slug a translation of "How to steer a story" is drafted with by the `characters` policy (Papyrus's `localized_slug`)
STEER = {"en": "/field-notes/steer-a-story/", "es-419": "/es/field-notes/dirigir-una-historia/", "zh-Hans": f"/zh/field-notes/{CHINESE_SLUG}/"}
MONITOR = {"en": "/field-notes/run-a-monitor/", "es-419": "/es/field-notes/ejecutar-un-monitor/"}
UNTRANSLATED = "/field-notes/read-the-wire/"

# Each translation links to a translated page, an untranslated page, a page outside the site and a spot in itself: what keeps a reader in their language
# and what must say that it leaves it.
LINKS = {
    "es": "Lee también [cómo ejecutar un monitor](/field-notes/run-a-monitor/), [la crónica sin traducir](/field-notes/read-the-wire/), [una fuente](https://example.org/fuente) y [el principio](#top).",
    "zh": "另见[如何运行监控](/field-notes/run-a-monitor/)、[未翻译的报道](/field-notes/read-the-wire/)、[一个来源](https://example.org/source)。",
}
TRANSLATED_PAGES = {
    # folder, slug: (title, dek, language tag, group, language of the links, type)
    ("field-notes", "dirigir-una-historia"): ("Cómo dirigir una historia", "Añade una fuente, señala una afirmación o pide otro enfoque, y mira cómo cambia el borrador.", "es-419", "steer-a-story", "es", "article"),
    ("field-notes", CHINESE_SLUG): ("如何引导一篇报道", "添加来源、标记一项说法，或要求换个角度，然后看草稿如何变化。", "zh-Hans", "steer-a-story", "zh", "article"),
    ("field-notes", "ejecutar-un-monitor"): ("Cómo ejecutar un monitor", "Un monitor vigila una fuente y avisa a la redacción cuando cambia.", "es-419", "run-a-monitor", "es", "article"),
}
CONCEPT = {"en": "/wiki/agent-evals/", "es-419": "/es/concepts/evaluaciones-de-agentes/"}


def write_content(directory: Path) -> Path:
    content = directory / "content"
    shutil.copytree(CONTENT, content)
    for (folder, slug), (title, dek, tag, group, links, kind) in TRANSLATED_PAGES.items():
        (content / folder / f"{slug}.md").write_text(
            f"---\ntitle: {json.dumps(title, ensure_ascii=False)}\ndek: {json.dumps(dek, ensure_ascii=False)}\ndate: 2026-10-27\ntags: [Steering]\nlanguage: {tag}\nlanguageGroup: {group}\n"
            f"drafting: {{by: agent, at: 2026-10-26}}\napproval: {{status: approved, by: Ada Reader, at: 2026-10-27}}\n---\n\n{LINKS[links]}\n",
            encoding="utf-8",
        )
    (content / "wiki" / "evaluaciones-de-agentes.md").write_text(
        "---\ntype: wiki_page\ntitle: Evaluaciones de agentes\nkind: concept\norder: 2\nlanguage: es-419\nlanguageGroup: agent-evals\n"
        "description: Pruebas que miden lo que puede hacer un agente, normalmente ejecutándolo en un conjunto de tareas y puntuando los resultados.\n"
        "review: {actor: human, name: Ada Reader, \"on\": 2026-10-29}\nupdated: 2026-10-29\n---\n\nLas evaluaciones de agentes ejecutan un agente en un conjunto fijo de tareas y puntúan los resultados.\n",
        encoding="utf-8",
    )
    return content


NOT_PUBLIC = {"primary": "en", "enabled": ["en", "es-419", "zh-Hans"]}  # the three languages are enabled and none is public: Papyrus serves the primary alone


def project_language_case(languages: dict = LANGUAGES) -> Path:
    from preview_local import project_fixture_site

    scratch = Path(tempfile.mkdtemp(prefix="mom-language-case-"))
    output_directory = scratch / "out"
    result = project_fixture_site(output_directory, content_directory=write_content(scratch), languages=languages)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return output_directory
