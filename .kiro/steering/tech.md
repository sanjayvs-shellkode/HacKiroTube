# Tech

- Pipeline: Python 3.12+, standard library only unless a dependency clearly pays for itself.
  HTTP via `urllib.request`. Data as JSON / JSONL under `data/`.
- Tests: `python -m unittest discover -s tests` (stdlib unittest, no pytest dependency).
- Site: Vite + TypeScript, static output, no backend.
- Stages communicate only through files in `data/`:
  `comments.jsonl` (harvest) -> `census.json` (census) -> `videos.json` (exorcist, LLM) and
  `graveyard.json` (necromancer, no LLM). Exorcist and Necromancer both read `census.json` and run independently.
  Each stage is rerunnable on its own.
- Cheap before smart: deterministic filtering (regex, API status) always runs before any LLM call.
  Track and report token usage of every LLM stage.
- Secrets (YouTube API key, LLM keys) come from environment variables, never committed.
