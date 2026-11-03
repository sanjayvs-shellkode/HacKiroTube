"""Shared HTTP: JSON over urllib, retrying only transient failures (429, 5xx, network)."""
import json
import os
import time
import urllib.error
import urllib.request


def load_env(path=".env"):
    """Load KEY=VALUE lines into os.environ; real environment variables win. Values are never printed."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:  # -sig: Notepad may save a BOM
        for line in f:
            key, sep, value = line.strip().removeprefix("export ").partition("=")
            if sep and key.strip() and not key.lstrip().startswith("#"):
                os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def request_json(url, data=None, headers=None, attempts=6, text=False):
    """GET, or POST when data is given; text=True returns the body as str (HTML pages).
    Secrets go in headers, so error text (URL without query) never leaks them."""
    body = None if data is None else json.dumps(data).encode()
    hdrs = {"User-Agent": "HacKiroTube", "Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(url, data=body, headers=hdrs)
    where = url.split("?")[0]
    for i in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace") if text else json.load(r)
        except urllib.error.HTTPError as e:
            if (e.code != 429 and e.code < 500) or i == attempts - 1:
                raise RuntimeError(f"HTTP {e.code} from {where}: {e.read()[:300]!r}") from None
            wait = float(e.headers.get("retry-after") or 2 ** i)
            if wait > 300:  # daily quota, not a blip: stop so the caller's progress file can be resumed later
                raise RuntimeError(f"HTTP {e.code} from {where}: rate limited for {wait:.0f}s, rerun later") from None
        except OSError as e:  # URLError, timeouts
            if i == attempts - 1:
                raise RuntimeError(f"giving up on {where}: {e}") from None
            wait = 2 ** i
        time.sleep(wait)
