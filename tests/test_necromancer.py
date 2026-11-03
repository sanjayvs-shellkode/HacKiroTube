import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from necromance import best_reupload, parse_title, tombstone  # noqa: E402

DEAD = "deaddeaddea"


def hit(vid, title, channel="c"):
    return {"id": vid, "title": title, "channel": channel}


class ParseTitle(unittest.TestCase):
    def test_meta_then_title_tag(self):
        self.assertEqual(parse_title('<meta name="title" content="Rich Hickey &amp; Simple">'), "Rich Hickey & Simple")
        self.assertEqual(parse_title("<title>\n  The Mother of All Demos - YouTube</title>"), "The Mother of All Demos")
        self.assertEqual(parse_title("<title>YouTube - Steve Jobs at Stanford</title>"), "Steve Jobs at Stanford")

    def test_error_pages_are_not_titles(self):
        for page in ["<title>YouTube</title>", "<title>YouTube - Broadcast Yourself.</title><meta name=\"title\" "
                     "content=\"This video is unavailable\">", "<title> - YouTube</title>", "no head at all"]:
            self.assertIsNone(parse_title(page), page)


class BestReupload(unittest.TestCase):
    def test_picks_closest_and_skips_self_and_weak(self):
        items = [hit(DEAD, "Simple Made Easy"), hit("aaaaaaaaaaa", "Totally different talk"),
                 hit("bbbbbbbbbbb", "Simple Made Easy - Rich Hickey (2011)"), hit("ccccccccccc", "simple made easy!")]
        self.assertEqual(best_reupload("Simple Made Easy", DEAD, items)["id"], "ccccccccccc")
        self.assertIsNone(best_reupload("Simple Made Easy", DEAD, items[:2]))

    def test_reworded_long_title_matches_but_short_overlap_does_not(self):
        water = "This Is Water - Full version-David Foster Wallace Commencement Speech"
        self.assertIsNotNone(best_reupload(water, DEAD, [hit("x", "This Is Water by David Foster Wallace (Full Speech)")]))
        self.assertIsNone(best_reupload("Steve Jobs Stanford", DEAD, [hit("x", "Steve Jobs iPhone keynote")]))
        self.assertIsNone(best_reupload(water, DEAD, [hit("x", "David Foster Wallace interview 2003 full")]))


class Tombstone(unittest.TestCase):
    def test_status_and_archive_fallback(self):
        v = {"id": DEAD, "recommenders": 4, "first_seen": 1, "last_seen": 2, "comment_ids": ["1"], "snippets": []}
        lost = tombstone(v, {"id": DEAD, "archive": None, "title": None})
        self.assertEqual(lost["status"], "lost")
        self.assertTrue(lost["archive"].startswith("https://web.archive.org/web/*/"))
        self.assertEqual(tombstone(v, {"archive": "https://web.archive.org/x", "title": "t"})["status"], "archived")
        self.assertEqual(tombstone(v, {"archive": None, "title": "t", "hits": [hit("x", "T")]})["status"], "resurrected")
        self.assertEqual(tombstone(v, {"archive": None, "title": "t", "hits": [hit(DEAD, "t")]})["status"], "lost")


if __name__ == "__main__":
    unittest.main()
