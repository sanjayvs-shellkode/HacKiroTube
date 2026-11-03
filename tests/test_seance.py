import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from seance import handle  # noqa: E402

CAT = {"videos": [
    {"id": "a", "title": "Inventing on Principle", "channel": "Bret", "crypt": "Programming", "why": "talk",
     "n": 40, "immortal": True},
    {"id": "b", "title": "Rust in an hour", "channel": "X", "crypt": "Programming", "why": "intro", "n": 9,
     "immortal": False}],
    "graves": [{"id": "z", "title": "Dont Talk to Police", "epitaph": "", "status": "resurrected", "n": 120}]}


def call(name, **args):
    return handle(CAT, {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                        "params": {"name": name, "arguments": args}})["result"]


class Seance(unittest.TestCase):
    def test_handshake_and_listing(self):
        self.assertEqual(handle(CAT, {"id": 1, "method": "initialize", "params": {}})["result"]["serverInfo"]["name"],
                         "hackirotube-seance")
        self.assertIsNone(handle(CAT, {"method": "notifications/initialized"}))
        self.assertEqual(len(handle(CAT, {"id": 2, "method": "tools/list"})["result"]["tools"]), 3)

    def test_tools(self):
        self.assertIn('"id": "a"', call("search_videos", query="principle")["content"][0]["text"])
        self.assertNotIn('"id": "b"', call("search_videos", immortals_only=True)["content"][0]["text"])
        self.assertIn("Programming", call("list_crypts")["content"][0]["text"])
        self.assertIn("Police", call("visit_graveyard", status="resurrected")["content"][0]["text"])

    def test_bad_input_is_an_error_not_a_crash(self):
        self.assertTrue(call("search_videos", nonsense=1)["isError"])
        self.assertEqual(handle(CAT, {"id": 3, "method": "tools/call", "params": {"name": "nope"}})["error"]["code"],
                         -32602)


if __name__ == "__main__":
    unittest.main()
