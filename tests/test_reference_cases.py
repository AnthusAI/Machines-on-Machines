import json
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "tests"))
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import reference_cases  # noqa: E402
from projection_support import project_reference_case  # noqa: E402

TODAY = date(2026, 11, 8)


def written(case):
    with tempfile.TemporaryDirectory() as scratch:
        expected = reference_cases.write_reference_case(Path(scratch), case, TODAY)
        return json.loads((Path(scratch) / "home-page" / "references.json").read_text()), expected


class ReferenceCasesTest(unittest.TestCase):
    def accepted(self, snapshot, medium):
        return [record for record in snapshot["references"] if record["status"] == "accepted" and (record.get("medium") == "video") == (medium == "video")]

    def test_none_has_two_hundred_unfiled_of_each_kind(self):
        snapshot, expected = written("none")
        for kind, medium in (("videos", "video"), ("findings", "finding")):
            self.assertEqual(len(self.accepted(snapshot, medium)), 200)
            self.assertEqual(len(expected[kind]["unfiled"]), 200)
            self.assertEqual(expected[kind]["by_section"], {})
            self.assertTrue(all("section" not in record for record in self.accepted(snapshot, medium)))

    def test_some_files_eighteen_under_pages_and_three_under_a_section_with_no_page(self):
        snapshot, expected = written("some")
        videos = expected["videos"]
        self.assertEqual({label: len(urls) for label, urls in videos["by_section"].items()}, {"Privacy & Security": 13, "Math & Science": 4, "Agents": 1})
        self.assertEqual(len(videos["pageless"]), 3)
        self.assertEqual(len(videos["unfiled"]), 152)
        self.assertEqual(videos["total"], 170)

    def test_all_has_nothing_unfiled_and_a_section_longer_than_a_first_page(self):
        _snapshot, expected = written("all")
        self.assertEqual(expected["videos"]["unfiled"], [])
        self.assertEqual({label: len(urls) for label, urls in expected["findings"]["by_section"].items()}, {"Privacy & Security": 70, "Math & Science": 4, "Agents": 1})

    def test_few_and_empty(self):
        _snapshot, few = written("few")
        self.assertEqual((len(few["videos"]["unfiled"]), len(few["videos"]["by_section"]["Math & Science"])), (2, 3))
        snapshot, empty = written("empty")
        self.assertEqual(empty["videos"]["total"], 0)
        self.assertEqual(len([record for record in snapshot["references"] if record["status"] == "recommended"]), 2 * reference_cases.recommended_count("empty"))
        self.assertFalse(self.accepted(snapshot, "video") or self.accepted(snapshot, "finding"))

    def test_keys_and_addresses_are_unique_and_ranks_run_from_one_without_gaps(self):
        for case in reference_cases.CASES:
            snapshot, _expected = written(case)
            records = snapshot["references"]
            self.assertEqual(len({record["key"] for record in records}), len(records), case)
            self.assertEqual(len({record["url"] for record in records}), len(records), case)
            self.assertEqual(sorted(record["rank"] for record in records), list(range(1, len(records) + 1)), case)

    def test_recommended_records_exist_in_every_case_and_are_not_expected_on_the_lists(self):
        for case in reference_cases.CASES:
            snapshot, expected = written(case)
            self.assertEqual(len([record for record in snapshot["references"] if record["status"] == "recommended"]), 2 * reference_cases.recommended_count(case), case)
            self.assertEqual(len(expected["findings"]["recommended"]), reference_cases.recommended_count(case), case)
            self.assertFalse(set(expected["findings"]["recommended"]) & set(expected["findings"]["urls"]))

    def test_the_five_star_record_is_older_than_seven_days_and_ranks_first_in_the_shared_order(self):
        snapshot, expected = written("none")
        stars = [record for record in snapshot["references"] if record.get("stars") == 5]
        self.assertEqual(len(stars), 2)
        for record in stars:
            self.assertGreater(TODAY - datetime.fromisoformat(record["acceptedAt"].replace("Z", "+00:00")).date(), timedelta(days=7))
        self.assertEqual(sorted(record["rank"] for record in stars), [1, 2])
        self.assertEqual(expected["videos"]["urls"].index(next(record["url"] for record in stars if record.get("medium") == "video")) >= 150, True)

    def test_dates_are_built_from_the_day_given(self):
        snapshot, _expected = written("few")
        newest = max(record["acceptedAt"] for record in snapshot["references"] if record["status"] == "accepted")
        self.assertTrue(newest.startswith(TODAY.isoformat()))

    def test_projecting_none_writes_at_least_two_chunk_files(self):
        output, _expected = project_reference_case("none")
        chunks = sorted((output / "reference-lists" / "videos" / "untagged").glob("*.json"))
        self.assertGreaterEqual(len(chunks), 2)


if __name__ == "__main__":
    unittest.main()
