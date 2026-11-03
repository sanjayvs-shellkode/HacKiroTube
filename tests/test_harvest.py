import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from harvest import extract_ids  # noqa: E402

ID = "dQw4w9WgXcQ"


class ExtractIds(unittest.TestCase):
    def test_url_forms(self):
        for url in [
            f"https://www.youtube.com/watch?v={ID}",
            f"https://m.youtube.com/watch?feature=share&v={ID}&t=30",
            f"https://youtu.be/{ID}?t=5",
            f"https://www.youtube.com/embed/{ID}",
            f"https://www.youtube-nocookie.com/embed/{ID}",
            f"https://youtube.com/shorts/{ID}",
            f"https://www.youtube.com/live/{ID}",
            f"http://www.youtube.com/v/{ID}",
        ]:
            self.assertEqual(extract_ids(url), [ID], url)

    def test_hn_escaped_html_dedupes_href_and_text(self):
        text = (f'<a href="https:&#x2F;&#x2F;youtu.be&#x2F;{ID}" rel="nofollow">'
                f"https:&#x2F;&#x2F;youtu.be&#x2F;{ID}</a> and watch?x=1&amp;v=abcdefghijk")
        self.assertEqual(extract_ids(text), [ID])
        self.assertEqual(extract_ids("youtube.com/watch?x=1&amp;v=abcdefghijk"), ["abcdefghijk"])

    def test_rejects_non_videos(self):
        for text in ["I love YouTube", "https://www.youtube.com/@channel", "https://youtu.be/short",
                     f"https://youtu.be/{ID}extra", "", None]:
            self.assertEqual(extract_ids(text), [], text)


if __name__ == "__main__":
    unittest.main()
