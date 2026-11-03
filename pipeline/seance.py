"""Seance: an MCP server (stdio, JSON-RPC 2.0) that lets Kiro query the HacKiroTube catalog.

Usage: python pipeline/seance.py [--catalog site/public/catalog.json]
Reads the file publish.py writes; rerun publish to refresh what the spirits know.
"""
import argparse
import json
import sys
from collections import Counter

PROTOCOL = "2025-06-18"
LIMIT = {"type": "integer", "minimum": 1, "maximum": 50, "default": 10}
TOOLS = [
    {"name": "search_videos", "description": "Search living HN-recommended videos by words in the title, channel "
     "or reason. Optional crypt (topic) filter and immortals_only. Most-recommended first.",
     "inputSchema": {"type": "object", "properties": {
         "query": {"type": "string"}, "crypt": {"type": "string"},
         "immortals_only": {"type": "boolean", "default": False}, "limit": LIMIT}}},
    {"name": "list_crypts", "description": "List the topic crypts with how many videos each holds.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "visit_graveyard", "description": "List tombstones of dead videos, most-mourned first. Optional "
     "status: resurrected (possible re-upload found), archived (archive.org page only) or lost.",
     "inputSchema": {"type": "object", "properties": {
         "query": {"type": "string"}, "status": {"type": "string", "enum": ["resurrected", "archived", "lost"]},
         "limit": LIMIT}}},
]


def words_match(query, *fields):
    hay = " ".join(f or "" for f in fields).lower()
    return all(w in hay for w in (query or "").lower().split())


def clamp(n):
    return max(1, min(int(n or 10), 50))


def search_videos(cat, query="", crypt=None, immortals_only=False, limit=10):
    hits = [v for v in cat["videos"] if words_match(query, v["title"], v["channel"], v["why"])
            and (not crypt or v["crypt"].lower() == crypt.lower()) and (v["immortal"] or not immortals_only)]
    hits.sort(key=lambda v: -v["n"])
    return [{**v, "url": f"https://www.youtube.com/watch?v={v['id']}"} for v in hits[:clamp(limit)]]


def list_crypts(cat):
    return dict(Counter(v["crypt"] for v in cat["videos"]).most_common())


def visit_graveyard(cat, query="", status=None, limit=10):
    hits = [g for g in cat["graves"] if words_match(query, g["title"], g["epitaph"])
            and (not status or g["status"] == status)]
    hits.sort(key=lambda g: -g["n"])
    return hits[:clamp(limit)]


HANDLERS = {"search_videos": search_videos, "list_crypts": list_crypts, "visit_graveyard": visit_graveyard}


def handle(cat, msg):
    """One JSON-RPC message in, one response dict out (None for notifications)."""
    method, mid = msg.get("method"), msg.get("id")
    if mid is None:
        return None
    if method == "initialize":
        result = {"protocolVersion": msg.get("params", {}).get("protocolVersion", PROTOCOL),
                  "capabilities": {"tools": {}}, "serverInfo": {"name": "hackirotube-seance", "version": "0.1.0"}}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = msg.get("params", {})
        fn = HANDLERS.get(params.get("name"))
        if not fn:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": "unknown tool"}}
        try:
            text, is_error = json.dumps(fn(cat, **(params.get("arguments") or {})), ensure_ascii=False), False
        except (TypeError, ValueError) as e:  # bad arguments from the client
            text, is_error = f"the spirits are confused: {e}", True
        result = {"content": [{"type": "text", "text": text}], "isError": is_error}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--catalog", default="site/public/catalog.json")
    args = ap.parse_args(argv)
    with open(args.catalog, encoding="utf-8") as f:
        cat = json.load(f)
    out = sys.stdout
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            reply = handle(cat, json.loads(line))
        except json.JSONDecodeError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        if reply:
            out.write(json.dumps(reply, ensure_ascii=False) + "\n")
            out.flush()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252; MCP needs UTF-8
    sys.stdin.reconfigure(encoding="utf-8")
    main()
