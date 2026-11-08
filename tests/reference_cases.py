"""Reference snapshots for every case a Videos, Findings or section list page must handle: no Reference filed under a section, some, all, a few, and none accepted.

The rolling seven-day buckets are counted back from the day the site is rendered, so every date here is built from the day the test runs and never written down.
`write_reference_case` writes the snapshot (`home-page/references.json`) and the thread files beside it, and returns what a scenario should find on the pages.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_HOME_PAGE_DIRECTORY = REPOSITORY_ROOT / "tests" / "fixtures" / "_data" / "home-page"
SECTIONS_FILE = REPOSITORY_ROOT / "web" / "sections.json"

from papyrus_content.home_page.ordering import order_in_buckets, rank_records  # noqa: E402

CASES = ("none", "some", "all", "few", "empty")
KINDS = ("video", "finding")
PAGELESS_SECTION = "Papyrus"   # a section name this site has no page for: its References count as filed under no section
RECOMMENDED_PER_KIND = 5
RECOMMENDED_PER_KIND_IN_NONE = 40   # the "none" case also has more pending References than the Just Found page's first page holds (59), so that page has data files
HOURS_BETWEEN_RECORDS = 1
FIVE_STAR_INDEX = 121
FIVE_STAR_DAYS_AGO = 20
STARRED_EVERY = 10
STARRED_BELOW_INDEX = 100
FILED_FROM_INDEX = 100          # in the "some" case a filed Reference is never among the first page of the engine's list (see the Phase A note in web/hooks.py)
FILED_SPACING = 4
PAGELESS_POSITIONS = (1, 40, 122)
CONFIDENCE_START = {"finding": (0.99, 0.004), "video": (0.45, 0.0015)}   # videos rank below findings inside a week, so a findings list's first page holds no video


def filed_section_labels() -> list[str]:
    return [section["label"] for section in json.loads(SECTIONS_FILE.read_text(encoding="utf-8"))["sections"]]


def recommended_count(case: str) -> int:
    return RECOMMENDED_PER_KIND_IN_NONE if case == "none" else RECOMMENDED_PER_KIND


def section_sequence(case: str) -> list[str | None]:
    """One entry per accepted Reference, best first: the section it is filed under, or None."""
    if case == "none":
        return [None] * 200
    if case == "some":
        sequence: list[str | None] = [None] * 170
        remaining = {"Privacy & Security": 12, "Math & Science": 4, "Agents": 1}
        position = FILED_FROM_INDEX
        while any(remaining.values()):
            for label in list(remaining):
                if remaining[label]:
                    sequence[position] = label
                    remaining[label] -= 1
                    position += FILED_SPACING
        for position in PAGELESS_POSITIONS:
            sequence[position] = PAGELESS_SECTION
        return sequence
    if case == "all":
        sequence = ["Privacy & Security"] * 75
        sequence[3] = sequence[20] = sequence[40] = sequence[60] = "Math & Science"
        sequence[10] = "Agents"
        return sequence
    if case == "few":
        return [None, None, "Math & Science", "Math & Science", "Math & Science"]
    return []


def is_starred(case: str, kind: str, index: int, section: str | None) -> bool:
    """Stars lift a Reference above every unrated one, videos and findings alike. A starred video would take a place in the first page of a findings list (the engine
    cannot leave videos out yet; Phase A drops them here), so only the "none" case stars videos: the findings pages of the other cases keep a clean first page."""
    return index % STARRED_EVERY == 5 and index < STARRED_BELOW_INDEX and section is None and (kind == "finding" or case == "none")


def record_key(case: str, kind: str, index: int | str) -> str:
    return hashlib.sha256(f"{case}-{kind}-{index}".encode()).hexdigest()[:12]


def accepted_record(case: str, kind: str, index: int, section: str | None, base: datetime) -> dict:
    key = record_key(case, kind, index)
    five_star = index == FIVE_STAR_INDEX and section is None
    accepted = base - (timedelta(days=FIVE_STAR_DAYS_AGO) if five_star else timedelta(hours=index * HOURS_BETWEEN_RECORDS))
    start, step = CONFIDENCE_START[kind]
    video = kind == "video"
    record = {
        "key": key, "status": "accepted", "title": f"Case {case} {kind} {index}", "authors": [],
        "url": f"https://www.youtube.com/watch?v={key}" if video else f"https://example.org/{case}/{kind}/{index}",
        "host": "youtube.com" if video else "example.org", "mediaType": "text/html",
        "arrivedAt": (accepted - timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ"), "sourceDate": accepted.strftime("%Y-%m-%d"),
        "actor": "cyclotron", "shareable": True, "versionNumber": 1, "acceptedAt": accepted.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "confidence": round(start - step * index, 4), "summary": f"A fictional {kind} number {index} of the {case} case.", "siteName": "Example",
    }
    if video:
        record["medium"] = "video"
    if section:
        record["section"] = section
    if five_star:
        record["stars"] = 5
    elif is_starred(case, kind, index, section):
        record["stars"] = 4
    return record


def recommended_record(case: str, kind: str, index: int, base: datetime) -> dict:
    key = record_key(case, kind, f"recommended-{index}")
    arrived = base - timedelta(hours=index + 1)
    video = kind == "video"
    record = {
        "key": key, "status": "recommended", "title": f"Case {case} recommended {kind} {index}", "authors": [],
        "url": f"https://www.youtube.com/watch?v={key}" if video else f"https://example.org/{case}/{kind}/recommended/{index}",
        "host": "youtube.com" if video else "example.org", "mediaType": "text/html", "arrivedAt": arrived.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sourceDate": arrived.strftime("%Y-%m-%d"), "actor": "cyclotron", "shareable": True, "versionNumber": 1,
        "confidence": round(0.97 - 0.01 * index, 2), "summary": f"A fictional recommended {kind} number {index}.", "siteName": "Example",
    }
    if video:
        record["medium"] = "video"
    return record


def ranked(records: list[dict]) -> list[dict]:
    positions = rank_records([({name: value for name, value in record.items() if name != "stars"}, record.get("stars")) for record in records])
    return [{**record, "rank": positions[record["key"]]} for record in records]


def expected_for(records: list[dict], today: date) -> dict:
    """What the pages should show, from the site's point of view: a section with no page here counts as no section."""
    filed_labels = set(filed_section_labels())
    accepted = [record for record in records if record["status"] == "accepted"]
    ordered = order_in_buckets(accepted, "week", today)
    sections: dict[str, list[str]] = {}
    unfiled: list[str] = []
    for record in ordered:
        label = record.get("section")
        if label in filed_labels:
            sections.setdefault(label, []).append(record["url"])
        else:
            unfiled.append(record["url"])
    return {
        "total": len(ordered), "urls": [record["url"] for record in ordered], "unfiled": unfiled, "by_section": sections,
        "titles": {record["url"]: record["title"] for record in ordered},
        "pageless": [record["url"] for record in ordered if record.get("section") == PAGELESS_SECTION],
        "recommended": [record["url"] for record in records if record["status"] == "recommended"],
    }


def write_reference_case(data_directory: Path, case: str, today: date) -> dict:
    if case not in CASES:
        raise ValueError(f"unknown case {case!r}")
    base = datetime(today.year, today.month, today.day, 12, tzinfo=timezone.utc)
    sequence = section_sequence(case)
    by_kind = {
        kind: [accepted_record(case, kind, index, section, base) for index, section in enumerate(sequence)]
        + [recommended_record(case, kind, index, base) for index in range(recommended_count(case))]
        for kind in KINDS
    }
    all_records = ranked([record for kind in KINDS for record in by_kind[kind]])   # one order over every Reference, as the snapshot has it
    expected = {
        ("videos" if kind == "video" else "findings"): expected_for([record for record in all_records if (record.get("medium") == "video") == (kind == "video")], today)
        for kind in KINDS
    }
    fixture = json.loads((FIXTURE_HOME_PAGE_DIRECTORY / "references.json").read_text(encoding="utf-8"))
    snapshot = {"generatedAt": base.strftime("%Y-%m-%dT%H:%M:%SZ"), "corpus": fixture["corpus"], "fields": fixture["fields"], "references": all_records}
    target = Path(data_directory) / "home-page"
    target.mkdir(parents=True, exist_ok=True)
    (target / "references.json").write_text(json.dumps(snapshot, indent=1, ensure_ascii=False), encoding="utf-8")
    shutil.copy(FIXTURE_HOME_PAGE_DIRECTORY / "threads.json", target / "threads.json")
    shutil.copytree(FIXTURE_HOME_PAGE_DIRECTORY / "threads", target / "threads", dirs_exist_ok=True)
    return expected
