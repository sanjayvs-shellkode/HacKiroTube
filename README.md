# HacKiroTube

A haunted archive of the videos Hacker News has recommended since 2007, inspired by
[HackerTube](https://www.tokenpost.com/news/technology/45979). HacKiroTube also finds the
recommended videos that have died and tries to resurrect them.

The idea is Andrej Karpathy's HackerTube; this is an independent rebuild, made for fun for the Kiroween 2026
contest. The name is **Hac**ker News + **Kiro** + Hacker**Tube**.

## Pipeline

```
python pipeline/harvest.py            # -> data/comments.jsonl      (0 tokens)
python pipeline/census.py             # -> data/census.json         (0 tokens, needs YOUTUBE_API_KEY)
python pipeline/exorcise.py --limit 200   # -> data/videos.json     (LLM, needs OPENROUTER_API_KEY or --provider groq; resumable)
python pipeline/necromance.py         # -> data/graveyard.json      (0 tokens; ~90 re-upload searches/day, rerun daily)
python pipeline/publish.py            # -> site/public/catalog.json (joins the two above)
cd site && npm install && npm run build   # -> site/dist/ (static, host anywhere)
python -m unittest discover -s tests
```

## Seance (MCP server)

`pipeline/seance.py` is a stdlib MCP server over stdio that reads `site/public/catalog.json`.
Tools: `search_videos` (words, crypt, immortals only), `list_crypts`, `visit_graveyard` (resurrected / archived / lost).
Register it in `.kiro/settings/mcp.json`:

```json
{ "mcpServers": { "hackirotube-seance": { "command": "python", "args": ["pipeline/seance.py"],
  "autoApprove": ["search_videos", "list_crypts", "visit_graveyard"] } } }
```

## Hooks

`.kiro/hooks/tests-on-save.json` runs the unit tests after every file write by the agent.

## Numbers so far (harvest, 2026-11-02)

| Stage | Count |
|---|---|
| HN comments scanned (`youtube.com` + `youtu.be` queries) | 283,173 |
| Comments with a real video link (regex, 0 tokens) | 261,742 |
| Unique video IDs | 189,162 |
| Videos recommended by 2+ distinct people | 29,953 |
| Videos recommended by 3+ distinct people | 12,811 |
| Videos recommended by 5+ distinct people | 4,873 |

| Census: 3+ recommenders, checked with YouTube `videos.list` (0 tokens) | 12,811 |
| ...still alive | 12,020 |
| ...dead (deleted or private): future tombstones | 791 |
| Exorcist sample (`openai/gpt-oss-20b`, 200 videos) | 199 kept, ~229 tokens/video |

Date range 2007-02-28 to 2026-11-02. For comparison, HackerTube used 39,834 comments and listed 6,454 videos.
