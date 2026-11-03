import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from publish import YEAR, immortal  # noqa: E402


class Immortal(unittest.TestCase):
    def test_needs_both_many_people_and_many_years(self):
        self.assertTrue(immortal({"recommenders": 5, "first_seen": 0, "last_seen": 10 * YEAR}))
        self.assertFalse(immortal({"recommenders": 4, "first_seen": 0, "last_seen": 15 * YEAR}))
        self.assertFalse(immortal({"recommenders": 50, "first_seen": 0, "last_seen": 9 * YEAR}))


if __name__ == "__main__":
    unittest.main()
