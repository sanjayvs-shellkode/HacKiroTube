# KiroTube

A haunted archive of the videos Hacker News has recommended since 2007, inspired by
[HackerTube](https://www.tokenpost.com/news/technology/45979). KiroTube also finds the
recommended videos that have died and tries to resurrect them.

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
