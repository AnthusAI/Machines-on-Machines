"""A fixture site that has translations, for the language switcher's tests.

The ordinary fixture site is English only. This case copies its content and adds Spanish and Chinese pages for one article ("How to steer a story": all three
languages) and a Spanish page for another ("How to run a monitor": English and Spanish, no Chinese), each under its language's URL prefix (`/es/`, `/zh/`; Chinese's
slug is its title's own characters), plus a Spanish and a Chinese section list and home that exist only for what is translated. It says which pages are translations of one
another in `web/language-groups.json` (see web/languages.py). Every other page has no translation, so it has no switcher and no banner.
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))

from language_site import article_section, listing_groups, listing_pages  # noqa: E402
from languages import INTERFACE_STRINGS  # noqa: E402
CONTENT = REPOSITORY_ROOT / "tests" / "fixtures" / "content"

CHINESE_SLUG = "如何引导一篇报道"  # drafted from the Chinese title by the `characters` policy (web/languages.py)
STAND_IN_SLUG = "stand-in-chinese-1"  # the engine reduces slugs to ASCII for now, so the page is projected here and moved (tools/preview_local.py)
UNICODE_PAGE_PATHS = {f"/zh/field-notes/{CHINESE_SLUG}/": f"/zh/field-notes/{STAND_IN_SLUG}/"}
STEER = {"en": "/field-notes/steer-a-story/", "es-419": "/es/field-notes/dirigir-una-historia/", "zh-Hans": f"/zh/field-notes/{CHINESE_SLUG}/"}  # Chinese drafts its slug from its title, in characters
MONITOR = {"en": "/field-notes/run-a-monitor/", "es-419": "/es/field-notes/ejecutar-un-monitor/"}
UNTRANSLATED = "/field-notes/read-the-wire/"
PREFIXES = {"es-419": "es", "zh-Hans": "zh"}
STORIES = {"es-419": [("Cómo dirigir una historia", "/es/field-notes/dirigir-una-historia/"), ("Cómo ejecutar un monitor", "/es/field-notes/ejecutar-un-monitor/")],
           "zh-Hans": [("如何引导一篇报道", f"/zh/field-notes/{STAND_IN_SLUG}/")]}  # the listing links to the stand-in address, which the projection then writes as the real one
GROUPS = [STEER, MONITOR, *listing_groups(PREFIXES)]
PREFIXED_SECTIONS = {key: value for tag, prefix in PREFIXES.items() for key, value in article_section(prefix, INTERFACE_STRINGS[tag]).items()}
HOME_PAGES = [page for tag, prefix in PREFIXES.items() for page in listing_pages(tag, prefix, INTERFACE_STRINGS[tag], STORIES[tag])]

# Each translation links to a translated page, an untranslated page, a page outside the site and a spot in itself: what keeps a reader in their language
# and what must say that it leaves it.
LINKS = {
    "es": "Lee también [cómo ejecutar un monitor](/field-notes/run-a-monitor/), [la crónica sin traducir](/field-notes/read-the-wire/), [una fuente](https://example.org/fuente) y [el principio](#top).",
    "zh": "另见[如何运行监控](/field-notes/run-a-monitor/)、[未翻译的报道](/field-notes/read-the-wire/)、[一个来源](https://example.org/source)。",
}
TRANSLATED_PAGES = {
    # folder, slug: (title, dek, language of the links)
    ("es-field-notes", "dirigir-una-historia"): ("Cómo dirigir una historia", "Añade una fuente, señala una afirmación o pide otro enfoque, y mira cómo cambia el borrador.", "es"),
    ("zh-field-notes", STAND_IN_SLUG): ("如何引导一篇报道", "添加来源、标记一项说法，或要求换个角度，然后看草稿如何变化。", "zh"),
    ("es-field-notes", "ejecutar-un-monitor"): ("Cómo ejecutar un monitor", "Un monitor vigila una fuente y avisa a la redacción cuando cambia.", "es"),
}


def write_content(directory: Path) -> Path:
    content = directory / "content"
    shutil.copytree(CONTENT, content)
    for (folder, slug), (title, dek, links) in TRANSLATED_PAGES.items():
        (content / folder).mkdir(exist_ok=True)
        (content / folder / f"{slug}.md").write_text(
            f"---\ntitle: {json.dumps(title, ensure_ascii=False)}\ndek: {json.dumps(dek, ensure_ascii=False)}\ndate: 2026-10-27\ntags: [Steering]\n"
            f"drafting: {{by: agent, at: 2026-10-26}}\napproval: {{status: approved, by: Ada Reader, at: 2026-10-27}}\n---\n\n{LINKS[links]}\n",
            encoding="utf-8",
        )
    return content


def project_language_case() -> Path:
    from preview_local import project_fixture_site

    scratch = Path(tempfile.mkdtemp(prefix="mom-language-case-"))
    output_directory = scratch / "out"
    result = project_fixture_site(output_directory, content_directory=write_content(scratch), language_groups=GROUPS, language_prefixes=PREFIXES,
                                    extra_sections=PREFIXED_SECTIONS, extra_pages=HOME_PAGES, unicode_page_paths=UNICODE_PAGE_PATHS)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return output_directory
