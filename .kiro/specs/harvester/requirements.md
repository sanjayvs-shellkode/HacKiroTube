# Requirements: Harvester

## User story
As the KiroTube pipeline, I want every HN comment that links a YouTube video, so later stages
can classify and verify them without spending LLM tokens on comments with no video link.

## Acceptance criteria (EARS)
1. WHEN the harvester runs THE SYSTEM SHALL query the HN Algolia API for comments matching `youtube.com` and `youtu.be`.
2. WHEN a query has more than 1000 results THE SYSTEM SHALL page backwards by `created_at_i` until no results remain.
3. THE SYSTEM SHALL keep only comments whose unescaped text contains at least one valid 11-character YouTube video ID
   (watch, youtu.be, embed, shorts, live, v/ URL forms).
4. THE SYSTEM SHALL write one JSON object per kept comment to `data/comments.jsonl`, deduplicated by comment id.
5. WHEN `--max-pages` is given THE SYSTEM SHALL stop each query after that many pages (sampling mode).
6. WHEN the run finishes THE SYSTEM SHALL print hits scanned, comments kept, and unique video IDs.
7. IF a request fails THE SYSTEM SHALL retry with backoff and abort after 5 failures without writing a partial file.
