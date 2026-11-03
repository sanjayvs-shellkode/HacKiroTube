import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
from net import load_env  # noqa: E402


class LoadEnv(unittest.TestCase):
    def test_parses_and_real_env_wins(self):
        text = '\ufeff# comment\nA_KEY="quoted"\nexport B_KEY=plain\n\nC_KEY=x=y\nnot a pair\nKEEP=fromfile\n'
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"KEEP": "real"}, clear=True):
            p = Path(d) / ".env"
            p.write_text(text, encoding="utf-8")
            load_env(str(p))
            self.assertEqual(dict(os.environ), {"A_KEY": "quoted", "B_KEY": "plain", "C_KEY": "x=y", "KEEP": "real"})


if __name__ == "__main__":
    unittest.main()
