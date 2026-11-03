"""Census: count distinct recommenders per video, keep the popular ones, ask YouTube which are still alive.

Deterministic, 0 LLM tokens. Needs YOUTUBE_API_KEY.
Usage: python pipeline/census.py [--min-recommenders 3] [--in data/comments.jsonl] [--out data/census.json]
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.parse

from net import load_env, request_json

YT_API = "https://www.googleapis.com/youtube/v3/videos"
SNIPPETS, SNIPPET_CHARS = 3, 200


def plain(text):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text or "")).split())


def aggregate(comments, min_recommenders):
    """Group comments by video; return videos with at least min_recommenders distinct authors, most loved first."""
    vids = {}
    for c in comments:
        for vid in c["video_ids"]:
            v = vids.setdefault(vid, {"id": vid, "authors": set(), "first_seen": c["created_at"],
                                      "last_seen": c["created_at"], "comment_ids": [], "snippets": []})
            v["authors"].add(c["author"])
            v["first_seen"] = min(v["first_seen"], c["created_at"])
            v["last_seen"] = max(v["last_seen"], c["created_at"])
            v["comment_ids"].append(c["id"])
            if len(v["snippets"]) < SNIPPETS:
                v["snippets"].append(plain(c["text"])[:SNIPPET_CHARS])
    out = []
    for v in vids.values():
        n = len(v.pop("authors") - {None})  # deleted HN accounts have no author
        if n >= min_recommenders:
            out.append({**v, "recommenders": n})
    return sorted(out, key=lambda v: (-v["recommenders"], v["first_seen"]))


def youtube_status(ids, key):
    """videos.list omits deleted and private videos, so absent = dead. 50 ids per call, 1 quota unit each."""
    found = {}
    for i in range(0, len(ids), 50):
        q = urllib.parse.urlencode({"part": "snippet,contentDetails", "id": ",".join(ids[i:i + 50]), "maxResults": 50})
        for item in request_json(f"{YT_API}?{q}", headers={"X-goog-api-key": key}).get("items", []):
            s = item["snippet"]
            found[item["id"]] = {"title": s["title"], "channel": s["channelTitle"],
                                 "published": s["publishedAt"], "duration": item["contentDetails"].get("duration")}
        print(f"youtube: {min(i + 50, len(ids))}/{len(ids)}", file=sys.stderr)
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--min-recommenders", type=int, default=3)
    ap.add_argument("--in", dest="inp", default="data/comments.jsonl")
    ap.add_argument("--out", default="data/census.json")
    args = ap.parse_args(argv)
    load_env()
    key = os.environ.get("YOUTUBE_API_KEY") or sys.exit("set YOUTUBE_API_KEY")

    with open(args.inp, encoding="utf-8") as f:
        videos = aggregate(map(json.loads, f), args.min_recommenders)
    found = youtube_status([v["id"] for v in videos], key)
    for v in videos:
        v["alive"] = v["id"] in found
        v.update(found.get(v["id"], {"title": None, "channel": None, "published": None, "duration": None}))

    tmp = args.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False)
    os.replace(tmp, args.out)
    alive = sum(v["alive"] for v in videos)
    print(json.dumps({"videos": len(videos), "alive": alive, "dead": len(videos) - alive}))


if __name__ == "__main__":
    main()
