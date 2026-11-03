# Requirements: Exorcist

## User story
As a KiroTube visitor, I want only videos people genuinely recommend, each in a crypt with a one-line reason,
without the project burning HackerTube-scale tokens to get there.

## Acceptance criteria (EARS)
1. THE SYSTEM SHALL read `data/census.json` and send each video's title, channel and snippets to the LLM in batches.
2. THE SYSTEM SHALL ask for `keep`, one `crypt` from a fixed list, and a `why` of at most 15 words, as JSON.
3. IF a label has an unknown id, a non-bool `keep` or the reply is not JSON THEN THE SYSTEM SHALL drop it
   and retry that video on the next run; an unknown crypt becomes `Other`.
4. THE SYSTEM SHALL append labels to `data/exorcist.jsonl` after every batch and skip labelled videos on rerun.
5. THE SYSTEM SHALL add each response's token usage to `data/exorcist_usage.json`, even when the run stops early.
6. IF the provider rate-limits for more than 5 minutes THEN THE SYSTEM SHALL stop so the run can resume later.
7. THE SYSTEM SHALL write kept videos to `data/videos.json` atomically. `--limit` samples N new videos.
8. THE SYSTEM SHALL call OpenRouter (`OPENROUTER_API_KEY`, default) or Groq (`GROQ_API_KEY`) via `--provider`; `--model` picks the model (default `openai/gpt-oss-20b`, low reasoning effort).
