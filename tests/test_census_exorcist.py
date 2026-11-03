import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from census import aggregate  # noqa: E402
from exorcise import parse_labels  # noqa: E402

A, B = "aaaaaaaaaaa", "bbbbbbbbbbb"


def c(id, author, t, ids, text="<p>watch this</p>"):
    return {"id": id, "author": author, "created_at": t, "video_ids": ids, "text": text}


class Aggregate(unittest.TestCase):
    def test_counts_distinct_authors_and_span(self):
        comments = [c("1", "x", 30, [A, B]), c("2", "x", 10, [A]), c("3", "y", 20, [A]), c("4", None, 5, [A])]
        [v] = aggregate(comments, 2)
        self.assertEqual((v["id"], v["recommenders"], v["first_seen"], v["last_seen"]), (A, 2, 5, 30))
        self.assertEqual(len(v["snippets"]), 3)
        self.assertEqual(v["snippets"][0], "watch this")
        self.assertEqual(v["comment_ids"], ["1", "2", "3", "4"])


class ParseLabels(unittest.TestCase):
    def test_validates_and_drops_strays(self):
        content = json.dumps({"videos": [
            {"id": A, "keep": True, "crypt": "Space", "why": "great"},
            {"id": A, "keep": False, "crypt": "Math"},          # duplicate, ignored
            {"id": B, "keep": True, "crypt": "Made Up Crypt"},  # unknown crypt -> Other
            {"id": "ccccccccccc", "keep": True},                # not asked about
            {"id": B, "keep": "yes"},                           # not bool
        ]})
        rows = parse_labels(content, {A, B})
        self.assertEqual([(r["id"], r["keep"], r["crypt"]) for r in rows], [(A, True, "Space"), (B, True, "Other")])

    def test_garbage_is_empty(self):
        for content in ["not json", "[]", '{"videos": "x"}', None]:
            self.assertEqual(parse_labels(content, {A}), [], content)


if __name__ == "__main__":
    unittest.main()
