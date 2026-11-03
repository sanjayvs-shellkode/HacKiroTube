# Product: KiroTube

KiroTube is a haunted archive of the videos Hacker News has recommended since 2007.
It is inspired by Karpathy's HackerTube and adds one thing HackerTube does not do:
it finds recommended videos that have since died (deleted, private, taken down) and
tries to resurrect them (archived copy, re-upload, recovered context).

## Features
- Harvester: pull HN comments containing YouTube links (HN Algolia API).
- Exorcist: LLM separates genuine recommendations from spam/passing mentions, assigns topics.
- Necromancer: checks every video's status, finds dead ones, searches for resurrections.
- Graveyard: tombstone page for dead videos. Immortals: videos recommended across many years.
- Seance: MCP server so Kiro can query the catalog.
- Static site: topic "crypts", keyboard shortcuts, local-storage watched state, JSON export.

## Non-goals
- No accounts, no backend, no video hosting. Link and embed only; dead videos link to archive.org.

## Hackathon
Target category: Resurrection (Kiroween). Judged on potential value, use of Kiro, creativity.
Every Kiro feature used (specs, steering, hooks, crew agents, MCP) should be documented in the write-up.
