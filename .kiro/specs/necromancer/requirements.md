# Requirements: Necromancer

## User story
As a HacKiroTube visitor, I want a tombstone for every recommended video that died, with its name and
any copy that survived, so the community's lost recommendations are not simply gone.

## Acceptance criteria (EARS)
1. THE SYSTEM SHALL read dead videos (`alive: false`) from `data/census.json`, most recommenders first. No LLM.
2. THE SYSTEM SHALL ask the Wayback availability API for the watch page snapshot closest to the first HN recommendation.
3. WHEN a 200 snapshot exists THE SYSTEM SHALL recover the title from its raw page, rejecting YouTube error pages.
4. WHEN a title is known THE SYSTEM SHALL search YouTube (5 hits, 100 quota units) and cache the hits,
   at most `--search-budget` searches per run (default 90), stopping cleanly on quota errors.
5. THE SYSTEM SHALL call a hit a possible resurrection only at title similarity >= 0.85 and never the dead id itself.
6. THE SYSTEM SHALL mark each tombstone `resurrected` (re-upload found), `archived` (snapshot only) or `lost`,
   and always give an archive.org link.
7. THE SYSTEM SHALL save progress per video to `data/necromancer.jsonl`, skip finished work on rerun,
   pause 8s between archive.org lookups (1s and 4s were rate-limited), stop the Wayback pass cleanly on a persistent 429,
   and write `data/graveyard.json` atomically with the tombstones exhumed so far.
