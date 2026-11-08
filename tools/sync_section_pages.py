"""Generate the section pages from one template and one list of sections.

`web/sections.json` lists the newsroom sections that have a page. `web/pages/section.template.md` is the one layout every
section page shares. This tool writes, for each section:

- `web/pages/sections/<id>.md`, the template with that section filled in;
- a `pages` entry (`section-<id>`, at `/<id>/`) and two `collections` (`<id>-articles` at `/<id>/articles/` and `<id>-posts`
  at `/<id>/posts/`, the full paginated lists the page's "More articles…" and "More posts…" links go to) in `web/projection.json`.

Never edit those by hand.

    python3 tools/sync_section_pages.py           write them
    python3 tools/sync_section_pages.py --check   exit 1 when one differs (CI and tests)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
WEB = REPOSITORY_ROOT / "web"
PROJECTION = WEB / "projection.json"
REGISTRY = WEB / "sections.json"
TEMPLATE = WEB / "pages" / "section.template.md"
PAGE_ID_PREFIX = "section-"
COLLECTION_TYPES = (("articles", "article", "Articles"), ("posts", "post", "Posts"))
VIDEOS_FETCHED_ONE_MORE = 1   # the page asks for one video more than it shows, to know whether to say "More videos…"


def registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def page_text(section: dict, settings: dict) -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    fills = {
        "@ID@": section["id"], "@LABEL@": section["label"], "@ARTICLE_CARDS@": str(settings["articleCards"]),
        "@POST_LINES@": str(settings["postLines"]), "@VIDEO_FETCH@": str(settings["videoCards"] + VIDEOS_FETCHED_ONE_MORE),
        "@VIDEO_CARDS@": str(settings["videoCards"]), "@ARTICLES_SHOWN@": str(settings["articleCards"] + 1),
    }
    for token, value in fills.items():
        text = text.replace(token, value)
    return text


def page_entry(section: dict) -> dict:
    return {
        "id": PAGE_ID_PREFIX + section["id"], "path": section["id"], "title": section["label"], "description": section["description"],
        "source": f"pages/sections/{section['id']}.md",
    }


def collection_entries(section: dict) -> list[dict]:
    return [
        {
            "id": f"{section['id']}-{name}", "base": f"{section['id']}/{name}", "label": f"{section['label']} {label.lower()}",
            "description": f"Every {label.lower()[:-1]} in {section['label']}, newest first.",
            "select": {"sections": [section["id"]], "types": [kind]}, "pageSize": 24, "featuredCount": 0, "sort": "date",
        }
        for name, kind, label in COLLECTION_TYPES
    ]


def generated_projection(settings: dict) -> dict:
    projection = json.loads(PROJECTION.read_text(encoding="utf-8"))
    ours = lambda entry: str(entry["id"]).startswith(PAGE_ID_PREFIX)
    others = [entry for entry in projection["pages"] if not ours(entry)]
    at = next(index for index, entry in enumerate(others) if entry["id"] == "about")
    projection["pages"] = others[:at] + [page_entry(section) for section in settings["sections"]] + others[at:]
    owned = {entry["id"] for section in settings["sections"] for entry in collection_entries(section)}
    kept = [entry for entry in projection.get("collections", []) if entry["id"] not in owned and not entry["id"].endswith(("-articles", "-posts"))]
    projection["collections"] = kept + [entry for section in settings["sections"] for entry in collection_entries(section)]
    return projection


def projection_text(projection: dict) -> str:
    return json.dumps(projection, indent=2, ensure_ascii=False) + "\n"


def wanted_files() -> dict[Path, str]:
    settings = registry()
    files = {WEB / "pages" / "sections" / f"{section['id']}.md": page_text(section, settings) for section in settings["sections"]}
    files[PROJECTION] = projection_text(generated_projection(settings))
    return files


def stale_files() -> list[Path]:
    wanted = wanted_files()
    stale = [path for path, text in wanted.items() if not path.is_file() or path.read_text(encoding="utf-8") != text]
    folder = WEB / "pages" / "sections"
    stale += [path for path in folder.glob("*.md") if path not in wanted] if folder.is_dir() else []
    return stale


if __name__ == "__main__":
    if "--check" in sys.argv[1:]:
        stale = stale_files()
        for path in stale:
            print(f"{path.relative_to(REPOSITORY_ROOT)} is out of date; run python3 tools/sync_section_pages.py")
        raise SystemExit(1 if stale else 0)
    (WEB / "pages" / "sections").mkdir(exist_ok=True)
    for path, text in wanted_files().items():
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(REPOSITORY_ROOT)}")
