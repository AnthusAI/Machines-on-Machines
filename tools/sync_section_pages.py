"""Generate the section pages and the Reference list pages from templates.

`web/sections.json` lists the newsroom sections that have a page. `web/pages/section.template.md` is the one layout every
section page shares. This tool writes, for each section:

- `web/pages/sections/<id>.md`, the template with that section filled in;
- a `pages` entry (`section-<id>`, at `/<id>/`) and two `collections` (`<id>-articles` at `/<id>/articles/` and `<id>-posts`
  at `/<id>/posts/`, the full paginated lists the page's "More articles…" and "More posts…" links go to) in `web/projection.json`.

- `web/pages/sections/<id>-conversations.md`, the section's board of the forum (at `/<id>/conversations/`), from `web/pages/section-conversations.template.md`;
- `web/pages/videos.md`, `web/pages/findings.md`, `web/pages/sections/<id>-videos.md` and `web/pages/sections/<id>-findings.md` (a section's own lists, at
  `/<id>/videos/` and `/<id>/findings/`) from `web/pages/reference-list.template.md`, the one layout every list of References shares: a lead of the best few
  References in no section, then (on Videos and Findings only) one block per section with its best few, then one paged stream of the rest. None of them has a
  heading of its own on References that are in no section. Each section's lists have a `pages` entry.

Never edit those by hand.

    python3 tools/sync_section_pages.py           write them
    python3 tools/sync_section_pages.py --check   exit 1 when one differs (CI and tests)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
WEB = REPOSITORY_ROOT / "web"
PAGE_ID_PREFIX = "section-"
PRIMARY_LANGUAGE = "en"
VIDEOS_PAGE_ID_PREFIX = "sectionvideos-"
FINDINGS_PAGE_ID_PREFIX = "sectionfindings-"
CONVERSATIONS_PAGE_ID_PREFIX = "sectionconversations-"
LEAD_CARDS = 4                 # a feature, then a row of three
STREAM_FIRST_PAGE_CARDS = 60   # whole rows at 1, 2, 3, 4, 5 and 6 columns
PAGE_COUNT = LEAD_CARDS + STREAM_FIRST_PAGE_CARDS   # the hook lifts the first LEAD_CARDS out of the stream into the lead
# Phase A only: how far down the order the section blocks look; replaced by the engine's groups (Papyrus PPY-2d9715). A section whose best Reference ranks lower
# gets no block on /videos/ but stays reachable at its own list.
GROUP_SOURCE_COUNT = 500
# Phase A only: the section front's findings include mixes videos in and the hook drops them; replaced by notMedium (Papyrus PPY-a9402d).
FINDINGS_FETCHED_PAST_VIDEOS = 24
REFERENCE_LIST_PAGES = (
    # (file, page values) for the two pages that show the best of each section
    ("videos.md", {"CLASSES": "mom-videos ", "TITLE": "Videos", "LEAD": "Videos we think are worth watching.", "KIND": "videos", "NOUN": "videos", "MEDIUM": ' medium="video" minStars="3"', "SECTION": "",
                   "EMPTY": "No videos have been accepted yet.", "LIST_ID": "untagged", "groups": True, "HALFTONE": ' halftone="true"'}),
    ("findings.md", {"CLASSES": "", "TITLE": "Findings", "LEAD": "Every source our editors and Cyclotron have accepted. Each card says who accepted it.", "KIND": "findings", "NOUN": "findings",
                     "MEDIUM": "", "SECTION": "", "EMPTY": "Nothing has been accepted yet.", "LIST_ID": "untagged", "groups": True, "HALFTONE": ' halftone="true"'}),
)
COLLECTION_TYPES = (("articles", "article", "Articles"), ("posts", "post", "Posts"))
VIDEOS_FETCHED_ONE_MORE = 1   # the page asks for one video more than it shows, to know whether to say "More videos…"


def registry(web: Path = WEB) -> dict:
    return json.loads((web / "sections.json").read_text(encoding="utf-8"))


def page_text(section: dict, settings: dict, web: Path = WEB) -> str:
    text = (web / "pages" / "section.template.md").read_text(encoding="utf-8")
    fills = {
        "@ID@": section["id"], "@LABEL@": section["label"], "@ARTICLE_CARDS@": str(settings["articleCards"]),
        "@POST_CARDS@": str(settings["postCards"]), "@VIDEO_FETCH@": str(settings["videoCards"] + VIDEOS_FETCHED_ONE_MORE),
        "@VIDEO_CARDS@": str(settings["videoCards"]), "@FINDING_CARDS@": str(settings["findingCards"]),
        "@FINDING_FETCH@": str(FINDINGS_FETCHED_PAST_VIDEOS), "@ARTICLES_SHOWN@": str(settings["articleCards"] + 1),
    }
    for token, value in fills.items():
        text = text.replace(token, value)
    return text


def reference_list_text(values: dict, web: Path = WEB) -> str:
    """The Reference list template with its `@@if name` ... `@@end` blocks kept or dropped and its @TOKENS@ filled in."""
    text = (web / "pages" / "reference-list.template.md").read_text(encoding="utf-8")
    values = {"MORE_LABEL": f"More {values['NOUN']}", **values, "LEAD_CARDS": str(LEAD_CARDS), "PAGE_COUNT": str(PAGE_COUNT), "SOURCE_COUNT": str(GROUP_SOURCE_COUNT)}
    kept = values.get("groups", False)
    text = re.sub(r"@@if groups\n(.*?)@@end\n", (lambda found: found.group(1)) if kept else "", text, flags=re.S)
    text = re.sub(r"@@if notice\n(.*?)@@end\n", (lambda found: found.group(1)) if values.get("notice") else "", text, flags=re.S)
    for token, value in values.items():
        if token.isupper():
            text = text.replace(f"@{token}@", value)
    return text


def section_videos_lead(section: dict) -> str:
    return f"Every video filed under {section['label']}, this week's best first."


def section_findings_lead(section: dict) -> str:
    return f"Every source filed under {section['label']} that our editors and Cyclotron have accepted, this week's best first."


def section_videos_values(section: dict) -> dict:
    return {
        "CLASSES": "mom-videos ", "TITLE": f"{section['label']} videos", "LEAD": section_videos_lead(section), "KIND": "videos", "NOUN": "videos",
        "MEDIUM": ' medium="video" minStars="3"', "SECTION": f' section="{section["label"]}"', "EMPTY": f"No videos in {section['label']} yet.", "LIST_ID": "all", "groups": False, "HALFTONE": "",
    }


def section_findings_values(section: dict) -> dict:
    return {
        "CLASSES": "", "TITLE": f"{section['label']} findings", "LEAD": section_findings_lead(section), "KIND": "findings", "NOUN": "findings",
        "MEDIUM": "", "SECTION": f' section="{section["label"]}"', "EMPTY": f"No findings in {section['label']} yet.", "LIST_ID": "all", "groups": False, "HALFTONE": "",
    }


def section_videos_entry(section: dict) -> dict:
    return {
        "id": VIDEOS_PAGE_ID_PREFIX + section["id"], "path": f"{section['id']}/videos", "title": f"{section['label']} videos",
        "description": section_videos_lead(section), "source": f"pages/sections/{section['id']}-videos.md",
    }


def section_findings_entry(section: dict) -> dict:
    return {
        "id": FINDINGS_PAGE_ID_PREFIX + section["id"], "path": f"{section['id']}/findings", "title": f"{section['label']} findings",
        "description": section_findings_lead(section), "source": f"pages/sections/{section['id']}-findings.md",
    }


def section_conversations_text(section: dict, web: Path = WEB) -> str:
    text = (web / "pages" / "section-conversations.template.md").read_text(encoding="utf-8")
    return text.replace("@ID@", section["id"]).replace("@LABEL@", section["label"])


def section_conversations_lead(section: dict) -> str:
    return f"Editors and AI discussing {section['label']} stories and sources."


def section_conversations_entry(section: dict) -> dict:
    return {
        "id": CONVERSATIONS_PAGE_ID_PREFIX + section["id"], "path": f"{section['id']}/conversations", "title": f"{section['label']} conversations",
        "description": section_conversations_lead(section), "source": f"pages/sections/{section['id']}-conversations.md",
    }


def page_entry(section: dict) -> dict:
    """A section page is rendered in each language that has its file (`<id>.<tag>.md`, written below) and a name for the section in its strings."""
    return {
        "id": PAGE_ID_PREFIX + section["id"], "path": section["id"], "title": section["label"], "description": section["description"],
        "source": f"pages/sections/{section['id']}.md", "languages": "localize",
        "titleKey": f"section.{section['id']}.label", "descriptionKey": f"section.{section['id']}.description",
    }


def edition_tags(web: Path = WEB) -> list[str]:
    """The languages other than the primary that have interface strings: each gets a file for every section page."""
    return sorted(path.stem for path in (web / "strings").glob("*.json") if path.stem != PRIMARY_LANGUAGE)


def edition_page_text(section: dict) -> str:
    """The section page of a language edition: the one block that draws it from that language's Stories (`web/hooks.py`, `_edition_section`)."""
    return '::band{size="bare"}\n\n::include{kind="block" name="edition-section" section="' + section["id"] + '" depends="' + section["id"] + '"}\n'


def collection_entries(section: dict) -> list[dict]:
    return [
        {
            "id": f"{section['id']}-{name}", "base": f"{section['id']}/{name}", "label": f"{section['label']} {label.lower()}",
            "description": f"Every {label.lower()[:-1]} in {section['label']}, newest first.",
            "select": {"sections": [section["id"]], "types": [kind]}, "pageSize": 24, "featuredCount": 0, "sort": "date",
        }
        for name, kind, label in COLLECTION_TYPES
    ]


def generated_projection(settings: dict, web: Path = WEB) -> dict:
    projection = json.loads((web / "projection.json").read_text(encoding="utf-8"))
    ours = lambda entry: str(entry["id"]).startswith((PAGE_ID_PREFIX, VIDEOS_PAGE_ID_PREFIX, FINDINGS_PAGE_ID_PREFIX, CONVERSATIONS_PAGE_ID_PREFIX))
    others = [{**entry, "languages": "localize", "titleKey": f"nav./{entry['id']}/.label", "descriptionKey": f"nav./{entry['id']}/.description"} if entry["id"] in LOCALIZED_PAGES else entry
              for entry in projection["pages"] if not ours(entry)]
    at = next(index for index, entry in enumerate(others) if entry["id"] == "about")
    projection["pages"] = others[:at] + [entry for section in settings["sections"] for entry in (page_entry(section), section_videos_entry(section), section_findings_entry(section), section_conversations_entry(section))] + others[at:]
    owned = {entry["id"] for section in settings["sections"] for entry in collection_entries(section)}
    kept = [entry for entry in projection.get("collections", []) if entry["id"] not in owned and not entry["id"].endswith(("-articles", "-posts"))]
    projection["collections"] = kept + [entry for section in settings["sections"] for entry in collection_entries(section)]
    projection.setdefault("homePage", {}).setdefault("references", {})["paging"] = {"pageSize": 24}
    return projection


def projection_text(projection: dict) -> str:
    return json.dumps(projection, indent=2, ensure_ascii=False) + "\n"


LOCALIZED_PAGES = ("findings", "videos", "conversations")   # the pages a language renders (docs/multilingual-serving.md: authored pages in an edition)


def edition_strings(tag: str, web: Path = WEB) -> dict:
    return json.loads((web / "strings" / f"{tag}.json").read_text(encoding="utf-8"))


def edition_reference_values(base: dict, kind: str, strings: dict) -> dict:
    """The values of a Reference list page in a language: its words from the language's strings, its structure the English page's, and the line that says the items are in their original language."""
    return {**base, "TITLE": strings[f"nav./{kind}/.label"], "LEAD": strings[f"list.{kind}.lead"], "NOUN": strings[f"list.{kind}.noun"], "EMPTY": strings[f"list.{kind}.empty"],
            "notice": True, "NOTICE": strings["list.originalNotice"],
            "MORE_LABEL": strings["list.more"].format(noun=strings[f"list.{kind}.noun"])}


def edition_conversations_text(strings: dict, web: Path = WEB) -> str:
    text = (web / "pages" / "conversations.md").read_text(encoding="utf-8")
    text = text.replace('title="Conversations" lead="The forum. Editors and AI discuss our stories and sources."', f'title="{strings["nav./conversations/.label"]}" lead="{strings["list.conversations.lead"]}"')
    text = text.replace('empty="No conversations yet."', f'empty="{strings["list.conversations.empty"]}"')
    notice = f'::raw\n<p class="mom-original-notice">{strings["list.originalNotice"]}</p>\n::endraw\n\n'
    return text.replace("::raw\n<!--sf:forum-->", notice + "::raw\n<!--sf:forum-->", 1)


def wanted_files(web: Path = WEB) -> dict[Path, str]:
    settings = registry(web)
    sections_folder = web / "pages" / "sections"
    files = {sections_folder / f"{section['id']}.md": page_text(section, settings, web) for section in settings["sections"]}
    for section in settings["sections"]:
        for tag in edition_tags(web):
            files[sections_folder / f"{section['id']}.{tag}.md"] = edition_page_text(section)
        files[sections_folder / f"{section['id']}-videos.md"] = reference_list_text(section_videos_values(section), web)
        files[sections_folder / f"{section['id']}-findings.md"] = reference_list_text(section_findings_values(section), web)
        files[sections_folder / f"{section['id']}-conversations.md"] = section_conversations_text(section, web)
    for name, values in REFERENCE_LIST_PAGES:
        files[web / "pages" / name] = reference_list_text(values, web)
        for tag in edition_tags(web):
            kind = name.removesuffix(".md")
            files[web / "pages" / f"{kind}.{tag}.md"] = reference_list_text(edition_reference_values(values, kind, edition_strings(tag, web)), web)
    for tag in edition_tags(web):
        files[web / "pages" / f"conversations.{tag}.md"] = edition_conversations_text(edition_strings(tag, web), web)
    files[web / "projection.json"] = projection_text(generated_projection(settings, web))
    return files


def stale_files(web: Path = WEB) -> list[Path]:
    wanted = wanted_files(web)
    stale = [path for path, text in wanted.items() if not path.is_file() or path.read_text(encoding="utf-8") != text]
    folder = web / "pages" / "sections"
    stale += [path for path in folder.glob("*.md") if path not in wanted] if folder.is_dir() else []
    return stale


def write_files(web: Path = WEB) -> None:
    (web / "pages" / "sections").mkdir(exist_ok=True)
    for path, text in wanted_files(web).items():
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(web.parent) if web == WEB else path}")


if __name__ == "__main__":
    arguments = sys.argv[1:]
    chosen = Path(arguments[arguments.index("--web") + 1]).resolve() if "--web" in arguments else WEB
    if "--check" in arguments:
        stale = stale_files(chosen)
        for path in stale:
            print(f"{path} is out of date; run python3 tools/sync_section_pages.py")
        raise SystemExit(1 if stale else 0)
    write_files(chosen)
