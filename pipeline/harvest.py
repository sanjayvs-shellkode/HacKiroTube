"""Harvester: pull HN comments that link YouTube videos from the HN Algolia API.

Usage: python pipeline/harvest.py [--max-pages N] [--out data/comments.jsonl]
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.parse

from net import request_json

API = "https://hn.algolia.com/api/v1/search_by_date"
QUERIES = ("youtube.com", "youtu.be")
FIELDS = "comment_text,created_at_i,author,story_id,story_title"

YT_ID = re.compile(
    r"(?:youtu\.be/|youtube(?:-nocookie)?\.com/(?:watch\?(?:[^\s\"'<>]*?&)?v=|embed/|shorts/|live/|v/))"
    r"([A-Za-z0-9_-]{11})(?![A-Za-z0-9_-])"
)


def extract_ids(text):
    """Video IDs in order of first appearance; HN text is HTML-escaped (&#x2F;, &amp;)."""
    return list(dict.fromkeys(YT_ID.findall(html.unescape(text or ""))))


def walk(query, max_pages=None):
    """Yield hits newest-first, paging backwards with a created_at_i cursor (Algolia caps a query at 1000 hits).
    shortcut: hits sharing the boundary second can be skipped, upgrade to <= plus dedupe if counts look off."""
    cursor, pages = None, 0
    while max_pages is None or pages < max_pages:
        params = {"query": query, "tags": "comment", "hitsPerPage": 1000, "attributesToRetrieve": FIELDS}
        if cursor is not None:
            params["numericFilters"] = f"created_at_i<{cursor}"
        hits = request_json(f"{API}?{urllib.parse.urlencode(params)}")["hits"]
        if not hits:
            return
        yield from hits
        cursor = min(h["created_at_i"] for h in hits)
        pages += 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--max-pages", type=int, help="pages per query (sampling)")
    ap.add_argument("--out", default="data/comments.jsonl")
    args = ap.parse_args(argv)

    kept, scanned = {}, 0
    for q in QUERIES:
        for h in walk(q, args.max_pages):
            scanned += 1
            ids = extract_ids(h.get("comment_text"))
            if ids and h["objectID"] not in kept:
                kept[h["objectID"]] = {
                    "id": h["objectID"], "author": h.get("author"), "created_at": h["created_at_i"],
                    "story_id": h.get("story_id"), "story_title": h.get("story_title"),
                    "text": h["comment_text"], "video_ids": ids,
                }
        print(f"{q}: scanned so far {scanned}, kept {len(kept)}", file=sys.stderr)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    tmp = args.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for c in sorted(kept.values(), key=lambda c: c["created_at"]):
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    os.replace(tmp, args.out)  # no partial file on failure

    videos = {v for c in kept.values() for v in c["video_ids"]}
    print(json.dumps({"hits_scanned": scanned, "comments_kept": len(kept), "unique_videos": len(videos)}))


if __name__ == "__main__":
    main()
