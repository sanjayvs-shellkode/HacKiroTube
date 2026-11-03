# Requirements: Census

## User story
As the KiroTube pipeline, I want the popular videos and their live/dead status before any LLM call,
so the Exorcist sees real titles and only spends tokens on videos several people recommended.

## Acceptance criteria (EARS)
1. THE SYSTEM SHALL group `data/comments.jsonl` by video and count distinct non-null HN authors as recommenders.
2. THE SYSTEM SHALL keep videos with at least `--min-recommenders` (default 3) recommenders.
3. THE SYSTEM SHALL record first/last recommendation time, comment ids and up to 3 plain-text snippets of 200 chars.
4. THE SYSTEM SHALL check every kept id with YouTube `videos.list` in batches of 50 and mark ids absent from the reply as dead.
5. THE SYSTEM SHALL read the key from `YOUTUBE_API_KEY` and send it as a header, never in a URL or log.
6. THE SYSTEM SHALL write `data/census.json` atomically and print video, alive and dead counts.
