"""Publish: join videos.json and graveyard.json into the one small file the static site loads.

Usage: python pipeline/publish.py [--out site/public/catalog.json]
"""
import argparse
import json
import os
from datetime import datetime, timezone

YEAR = 365.25 * 86400
IMMORTAL_YEARS, IMMORTAL_RECOMMENDERS = 10, 5


def year(ts):
    return datetime.fromtimestamp(ts, timezone.utc).year


def immortal(v):
    """Recommended by 5+ people across 10+ years: the community keeps coming back to it."""
    return v["recommenders"] >= IMMORTAL_RECOMMENDERS and (v["last_seen"] - v["first_seen"]) / YEAR >= IMMORTAL_YEARS


def slim_video(v):
    return {"id": v["id"], "title": v["title"], "channel": v["channel"], "crypt": v["crypt"], "why": v["why"],
            "n": v["recommenders"], "from": year(v["first_seen"]), "to": year(v["last_seen"]),
            "alive": v["alive"], "immortal": immortal(v)}


def slim_grave(g):
    return {"id": g["id"], "title": g["title"], "n": g["recommenders"], "from": year(g["first_seen"]),
            "to": year(g["last_seen"]), "status": g["status"], "archive": g["archive"], "reupload": g["reupload"],
            "epitaph": (g["snippets"] or [""])[0], "comment": g["comment_ids"][0]}


def load(path):
    if not os.path.exists(path):  # stages run independently; publish whatever exists
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="site/public/catalog.json")
    args = ap.parse_args(argv)
    videos = [slim_video(v) for v in load("data/videos.json") if v["alive"]]  # dead ones live in the graveyard
    graves = [slim_grave(g) for g in load("data/graveyard.json")]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"videos": videos, "graves": graves}, f, ensure_ascii=False, separators=(",", ":"))
    print(json.dumps({"videos": len(videos), "immortals": sum(v["immortal"] for v in videos), "graves": len(graves),
                      "bytes": os.path.getsize(args.out)}))


if __name__ == "__main__":
    main()
