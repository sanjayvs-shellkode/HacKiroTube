"""Necromancer: for every dead video, dig up its archived page, recover its name, and look for a re-upload.

Reads data/census.json, writes data/graveyard.json. Progress per video goes to data/necromancer.jsonl,
so reruns skip finished work. Re-upload search costs 100 YouTube quota units per video (about 90 a day on
the free 10,000), most-mourned first; rerun daily until every named tombstone has been searched.
Usage: python pipeline/necromance.py [--search-budget 90]
"""
import argparse
import difflib
import html
import json
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime, timezone

from net import load_env, request_json

WAYBACK = "https://archive.org/wayback/available"
YT_SEARCH = "https://www.googleapis.com/youtube/v3/search"
PATIENCE = 9  # archive.org blocks bursts for minutes; 9 attempts back off ~4 min in total
PAUSE = 8  # seconds between lookups: ~2 requests per 9s, about 13/min
MATCH = 0.85  # title similarity needed to call a search hit a possible resurrection
NOT_A_TITLE = re.compile(r"^(youtube)?$|unavailable|removed|private video|deleted video|not available|broadcast yourself", re.I)


def watch_url(vid):
    return f"https://www.youtube.com/watch?v={vid}"


def parse_title(page):
    """Video title from an archived watch page, or None if the snapshot shows an error page."""
    for pat in (r'<meta\s+name="title"\s+content="([^"]*)"', r'<meta\s+property="og:title"\s+content="([^"]*)"',
                r"<title[^>]*>(.*?)</title>"):
        m = re.search(pat, page, re.I | re.S)
        if m:
            # "Title - YouTube" today, "YouTube - Title" around 2008
            t = re.sub(r"^\s*YouTube\s*-\s*|\s*-\s*YouTube\s*$", "", " ".join(html.unescape(m.group(1)).split()))
            return None if NOT_A_TITLE.search(t) else t
    return None


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def similarity(a, b):
    """Character similarity, or word overlap for titles of 4+ words (re-uploads reword long titles)."""
    a, b = norm(a), norm(b)
    score = difflib.SequenceMatcher(None, a, b).ratio()
    wa, wb = set(a.split()), set(b.split())
    if min(len(wa), len(wb)) >= 4:
        score = max(score, len(wa & wb) / min(len(wa), len(wb)))
    return score


def best_reupload(title, dead_id, hits):
    """Closest cached search hit, or None below MATCH. Never the dead video itself."""
    best = None
    for h in hits:
        if h["id"] == dead_id:
            continue
        score = similarity(title, h["title"])
        if score >= MATCH and (best is None or score > best["score"]):
            best = {**h, "score": round(score, 2)}
    return best


def exhume(v):
    """Wayback snapshot closest to the first HN recommendation, when the video was surely alive."""
    when = datetime.fromtimestamp(v["first_seen"], timezone.utc).strftime("%Y%m%d")
    q = urllib.parse.urlencode({"url": watch_url(v["id"]), "timestamp": when})
    snap = request_json(f"{WAYBACK}?{q}", attempts=PATIENCE).get("archived_snapshots", {}).get("closest") or {}
    row = {"id": v["id"], "archive": None, "title": None}
    if snap.get("available") and str(snap.get("status")) == "200":
        row["archive"] = snap["url"]
        try:  # id_ = raw page without the Wayback toolbar
            row["title"] = parse_title(request_json(f"https://web.archive.org/web/{snap['timestamp']}id_/{watch_url(v['id'])}",
                                                    text=True, attempts=PATIENCE))
        except RuntimeError as e:
            print(f"  {v['id']}: snapshot unreadable ({e})", file=sys.stderr)
    return row


def search(title, key):
    """Top 5 hits, cached so matching can be retuned without spending quota again."""
    q = urllib.parse.urlencode({"part": "snippet", "q": title, "type": "video", "maxResults": 5})
    items = request_json(f"{YT_SEARCH}?{q}", headers={"X-goog-api-key": key}).get("items", [])
    return [{"id": it["id"]["videoId"], "title": html.unescape(it["snippet"]["title"]),
             "channel": it["snippet"]["channelTitle"]} for it in items if it["id"].get("videoId")]


def tombstone(v, row):
    reupload = best_reupload(row["title"], v["id"], row["hits"]) if row.get("title") and row.get("hits") else None
    status = "resurrected" if reupload else "archived" if row.get("archive") else "lost"
    return {"id": v["id"], "title": row.get("title"), "recommenders": v["recommenders"],
            "first_seen": v["first_seen"], "last_seen": v["last_seen"], "comment_ids": v["comment_ids"],
            "snippets": v["snippets"], "status": status, "reupload": reupload,
            # dead videos always link to archive.org, even when no snapshot was found (product non-goal: no hosting)
            "archive": row.get("archive") or f"https://web.archive.org/web/*/{watch_url(v['id'])}"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--search-budget", type=int, default=90, help="max YouTube searches this run (100 units each)")
    ap.add_argument("--in", dest="inp", default="data/census.json")
    ap.add_argument("--out", default="data/graveyard.json")
    args = ap.parse_args(argv)
    load_env()
    key = os.environ.get("YOUTUBE_API_KEY") or sys.exit("set YOUTUBE_API_KEY")
    cache = "data/necromancer.jsonl"

    with open(args.inp, encoding="utf-8") as f:
        dead = [v for v in json.load(f) if not v["alive"]]  # census order: most recommenders first
    rows = {}
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            rows = {r["id"]: r for r in map(json.loads, f)}  # later lines win

    def save(row):
        rows[row["id"]] = row
        with open(cache, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    for n, v in enumerate(dead, 1):
        if v["id"] not in rows:
            try:
                save(exhume(v))
            except RuntimeError as e:  # archive.org 429s past our retries: stop here, rerun resumes
                print(f"wayback stopped at {n}/{len(dead)}: {e}", file=sys.stderr)
                break
            time.sleep(PAUSE)  # 1s and 4s pauses both got 429s from archive.org
            if n % 25 == 0:
                print(f"wayback: {n}/{len(dead)}", file=sys.stderr)

    searched = 0
    for v in dead:
        row = rows.get(v["id"])
        if not row or not row["title"] or "hits" in row or searched >= args.search_budget:
            continue
        try:
            hits = search(row["title"], key)
        except RuntimeError as e:  # quotaExceeded is a 403; stop searching, keep everything found so far
            print(f"search stopped: {e}", file=sys.stderr)
            break
        searched += 1
        save({**row, "hits": hits})

    graves = [tombstone(v, rows[v["id"]]) for v in dead if v["id"] in rows]  # unvisited ones join on rerun
    tmp = args.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(graves, f, ensure_ascii=False)
    os.replace(tmp, args.out)
    count = lambda s: sum(g["status"] == s for g in graves)  # noqa: E731
    pending = sum(1 for r in rows.values() if r["title"] and "hits" not in r)
    print(json.dumps({"dead": len(dead), "exhumed": len(graves), "named": sum(bool(g["title"]) for g in graves), "searched_now": searched,
                      "search_pending": pending, "resurrected": count("resurrected"),
                      "archived": count("archived"), "lost": count("lost")}))


if __name__ == "__main__":
    main()
