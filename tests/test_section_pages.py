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
        self.assertIn('href="/science/"', hooks._linked_title("Science", "/science/"))
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
