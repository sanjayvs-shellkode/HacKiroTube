# Design: Harvester

`pipeline/harvest.py`, stdlib only.

- `extract_ids(html_text) -> list[str]`: `html.unescape`, then one regex over the known URL forms. Order kept, duplicates removed.
- `walk(query, max_pages)`: generator over Algolia `search_by_date`, `tags=comment`, `hitsPerPage=1000`,
  `numericFilters=created_at_i<cursor`. The cursor is the oldest `created_at_i` on the page. Ties at the
  boundary second can be lost; acceptable at this scale.
- `main`: runs both queries, merges by `objectID`, writes to a temp file then renames (no partial output).

Record written:
```json
{"id": "50334048", "author": "khoirul", "created_at": 1793604546, "story_id": 50330000,
 "story_title": "...", "text": "<original html>", "video_ids": ["lP53ypyiqyM"]}
```
