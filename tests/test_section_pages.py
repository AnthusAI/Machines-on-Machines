import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPOSITORY_ROOT / "web"))
sys.path.insert(0, str(REPOSITORY_ROOT / "tools"))

import hooks  # noqa: E402
import sync_section_pages  # noqa: E402


def page_with_sections(*pairs):
    pages = [SimpleNamespace(id=f"section-{path}", path=path, title=title) for path, title in pairs]
    pages.append(SimpleNamespace(id="about", path="about", title="About"))
    return SimpleNamespace(settings=SimpleNamespace(pages=pages))


class SectionPageRegistryTest(unittest.TestCase):
    def test_every_listed_section_has_a_generated_page_and_the_generated_files_are_current(self):
        self.assertEqual(sync_section_pages.stale_files(), [])
        sections = sync_section_pages.registry()["sections"]
        self.assertEqual(len(sections), 10)
        generated = {entry["path"] for entry in json.loads((REPOSITORY_ROOT / "web" / "projection.json").read_text())["pages"] if entry["id"].startswith("section-")}
        self.assertEqual(generated, {section["id"] for section in sections})

    def test_a_section_page_is_named_the_way_its_stories_name_the_section(self):
        for section in sync_section_pages.registry()["sections"]:
            entry = SimpleNamespace(topic=section["id"], section=None)
            self.assertEqual(hooks._topic_label(entry), section["label"], section["id"])


class ReferenceListPagesTest(unittest.TestCase):
    def read(self, relative):
        return (REPOSITORY_ROOT / "web" / "pages" / relative).read_text(encoding="utf-8")

    def test_every_section_has_a_page_a_videos_list_and_a_findings_list_in_that_order(self):
        projection = json.loads((REPOSITORY_ROOT / "web" / "projection.json").read_text())
        generated = [entry["id"] for entry in projection["pages"] if entry["id"].startswith(("section-", "sectionvideos-", "sectionfindings-"))]
        sections = sync_section_pages.registry()["sections"]
        self.assertEqual(len(generated), 30)
        self.assertEqual(generated, [name + section["id"] for section in sections for name in ("section-", "sectionvideos-", "sectionfindings-")])

    def test_there_is_no_redirect_from_the_old_wire_page(self):
        projection = json.loads((REPOSITORY_ROOT / "web" / "projection.json").read_text())
        self.assertNotIn("/wire/", json.dumps(projection.get("redirects", {})))

    def test_videos_is_a_lead_the_best_of_each_section_and_an_unheaded_stream(self):
        text = self.read("videos.md")
        self.assertIn("<!--sf:refs-lead:4-->", text)
        self.assertIn('data-source-count="500"', text)
        self.assertIn('count="64" paged="true" id="untagged"', text)
        self.assertIn('data-list-kind="videos"', text)
        self.assertNotIn("recommended", text)
        self.assertNotIn("All videos", text)

    def test_findings_has_no_pending_panel_either(self):
        self.assertEqual(self.read("findings.md").count('select="recommended"'), 0)
        self.assertIn('count="64" paged="true" id="untagged"', self.read("findings.md"))

    def test_a_sections_own_lists_are_a_lead_and_a_stream_with_no_section_blocks(self):
        for kind in ("videos", "findings"):
            text = self.read(f"sections/security-{kind}.md")
            self.assertIn('id="all"', text)
            self.assertIn('section="Privacy & Security"', text)
            self.assertNotIn("mom-by-section", text)
        self.assertIn('medium="video"', self.read("sections/security-videos.md"))
        self.assertNotIn("medium=", self.read("sections/security-findings.md"))

    def test_the_section_front_has_a_findings_panel_of_three(self):
        text = self.read("sections/security.md")
        self.assertIn("<!--sf:findings:3-->", text)
        self.assertIn('section="Privacy & Security" count="24"', text)


class SectionResolverTest(unittest.TestCase):
    def setUp(self):
        self.resolve = hooks._section_resolver(page_with_sections(("security", "Privacy & Security"), ("law-policy", "Law & Policy")))

    def test_a_section_is_found_by_its_id_or_its_title(self):
        self.assertEqual(self.resolve("security"), ("/security/", "Privacy & Security"))
        self.assertEqual(self.resolve("Privacy & Security"), ("/security/", "Privacy & Security"))
        self.assertEqual(self.resolve("Privacy &amp; Security"), ("/security/", "Privacy & Security"))
        self.assertEqual(self.resolve("Law &amp; Policy"), ("/law-policy/", "Law & Policy"))

    def test_a_section_without_a_page_and_a_missing_section_have_no_address(self):
        for name in ("robotics", "More videos", "", None):
            self.assertIsNone(self.resolve(name), name)

    def test_pages_that_are_not_section_pages_are_never_found(self):
        self.assertIsNone(self.resolve("about"))


class MoreLinkTest(unittest.TestCase):
    def test_the_link_names_the_section_and_ends_with_one_ellipsis(self):
        self.assertIn(">More Privacy &amp; Security…</a>", hooks._more_link("Privacy & Security", "/security/"))

    def test_there_is_no_link_without_a_page(self):
        self.assertEqual(hooks._more_link("Robotics", None), "")

    def test_the_title_links_only_when_there_is_a_page(self):
        self.assertIn('href="/science/"', hooks._linked_title("Math & Science", "/science/"))
        self.assertEqual(hooks._linked_title("Robotics", None), "Robotics")


class HomeGroupTest(unittest.TestCase):
    def group(self, name, count, label=None):
        return (
            f'<section class="papyrus-group rh-group papyrus-has-lead" data-section="{name}" data-label="{label or name}" data-index="0" data-count="{count}">'
            f'<header class="papyrus-group-head"><h2 class="papyrus-group-title">{label or name}</h2></header><a>card</a></section>'
        )

    def test_a_group_of_two_links_its_name_and_ends_with_more(self):
        html = hooks._home_groups(self.group("security", 2), hooks._section_resolver(page_with_sections(("security", "Privacy & Security"))))
        self.assertIn('<a class="mom-section-title-link" href="/security/">Privacy &amp; Security</a>', html)
        self.assertTrue(html.endswith('<p class="mom-more"><a class="mom-more-link" href="/security/">More Privacy &amp; Security…</a></p></section>'))

    def test_a_group_of_one_has_no_more_link_and_a_group_without_a_page_has_no_link_at_all(self):
        resolve = hooks._section_resolver(page_with_sections(("security", "Privacy & Security")))
        self.assertNotIn("mom-more", hooks._home_groups(self.group("security", 1), resolve))
        html = hooks._home_groups(self.group("robotics", 3), resolve)
        self.assertNotIn("<a class=", html)
        self.assertIn(">Robotics<", html)


if __name__ == "__main__":
    unittest.main()
