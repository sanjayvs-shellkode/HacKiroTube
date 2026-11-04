# Devpost draft (paste into the Kiroween 2026 form)

Numbers as of 2026-11-03. Update the graveyard counts once the Necromancer finishes.

## Tagline

Karpathy's HackerTube, rebuilt with Kiro for Halloween: the videos Hacker News recommends, plus a séance for the ones that died.

## The name

HacKiroTube = **Hac**ker News + **Kiro** + Hacker**Tube**. Every part of the name comes from where the project came from.

## Credit

The idea is Andrej Karpathy's, not mine. He built HackerTube, a catalog of the YouTube videos Hacker News users recommend,
and I read about it in the news ([TokenPost](https://www.tokenpost.com/news/technology/45979)). I took that idea and
built my own version from scratch, for fun, for the Kiroween 2026 Halloween contest. All credit for the original concept
goes to him. The Halloween part (finding the dead videos and trying to resurrect them) is what I added.

## Inspiration

Reading about Karpathy's HackerTube, where an LLM read about 40k HN comments and listed the 6,454 videos the community recommends,
I wondered what happened to the old ones. Twenty years of link rot must have taken talks people still cite.
Kiroween's Resurrection theme made it obvious: HackerTube shows what HN loves, and HacKiroTube also counts what HN lost
and tries to bring it back.

## What it does

- **Crypts:** 11,363 living videos that 3 or more HN users recommended, sorted into topic crypts, each with a one-line reason people recommend it.
- **Immortals:** 763 videos recommended by 5+ people across 10+ years.
- **Graveyard:** 791 recommended videos are dead (deleted or private). Each gets a tombstone: the recovered title, how many people mourned it, an archive.org link, and a possible re-upload when one exists. The art follows the data: a ghost rises only from a resurrected grave, and a cracked stone means lost.
- **Séance:** an MCP server, so you can ask Kiro for "a classic talk on distributed systems" and get the catalog back.
- Keyboard shortcuts, watched state in local storage, JSON export, no accounts, no backend.

## How I built it

A Python standard-library pipeline. Stages talk only through files:

1. **Harvester:** HN Algolia API. 283,173 comments scanned, 189,162 unique video IDs. 0 tokens.
2. **Census:** keeps videos with 3+ distinct recommenders (12,811), then asks YouTube `videos.list` which are alive. 0 tokens.
3. **Exorcist (the only LLM stage):** `openai/gpt-oss-20b` via OpenRouter labels each video with its crypt, a keep/drop decision and a reason. 3.12M tokens total.
4. **Necromancer:** for each dead video, finds a Wayback snapshot from when HN first linked it, recovers the title, then searches YouTube for a re-upload. 0 tokens.
5. **Publish + site:** one 3 MB `catalog.json`, served by a Vite + TypeScript static site with inline SVG art.

Cheap before smart: regex and API checks remove everything they can before any LLM call. HackerTube spent 504M input tokens.
HacKiroTube covers about twice as many videos with 2.5M input tokens, about 0.5% as much.

## How I used Kiro

- **Specs:** `.kiro/specs/` holds requirements, design and tasks for harvester, census, exorcist, necromancer and site. Each stage was built against its spec.
- **Steering:** `product.md` (scope and non-goals), `tech.md` (stdlib only, the file-based stage contract, token tracking) and `theme.md` (palette, vocabulary, and the rule that state-carrying art must match the data).
- **Hooks:** `.kiro/hooks/tests-on-save.json` runs the unit test suite after every agent file write.
- **MCP:** the Séance (`pipeline/seance.py`), a stdlib MCP server with `search_videos`, `list_crypts` and `visit_graveyard`.
- **Kiro Crew:** ran the long Exorcist and Necromancer jobs as background processes while the site was built in parallel. A daily scheduled Kiro Crew job resumes the Necromancer and republishes the catalog until every tombstone is searched.

## Challenges

- The first Exorcist prompt was too strict. It dropped Steve Jobs' Stanford speech and Randy Pausch's Last Lecture as "passing mentions". I rewrote it to treat 3+ recommenders as evidence.
- Groq retired the model I started with mid-build. OpenRouter replaced it with one environment variable.
- archive.org rate limits (HTTP 429) forced the Necromancer to slow down and resume cleanly.
- YouTube search costs 100 quota units a call, so re-upload searches run about 90 a day, most-mourned first.
- Old YouTube pages title themselves "YouTube - Title", newer ones "Title - YouTube". The title recovery handles both.

## What's next

- Finish the re-upload searches for every tombstone, and recheck living videos weekly for new deaths.
- Run the same pipeline on another community (Lobsters, r/programming).

## Built with

python, vite, typescript, youtube-data-api, hn-algolia-api, wayback-machine, openrouter, mcp, kiro

---

# Demo video script (about 3 minutes)

| Time | Screen | Voice-over |
|---|---|---|
| 0:00-0:20 | HackerTube article, then a "Video unavailable" page | "I read about Andrej Karpathy's HackerTube in the news: the videos Hacker News loves. The idea is his, so full credit to him. I rebuilt it for fun for Kiroween, because click enough old links and you hit this." |
| 0:20-0:50 | HacKiroTube home, browse a crypt, press `j`/`k`, `w` | "HacKiroTube: 11,000 videos HN recommended since 2007, sorted into crypts. Keyboard driven, no account." |
| 0:50-1:10 | Immortals tab | "Immortals are the ones people keep recommending across ten years or more." |
| 1:10-1:50 | Graveyard: open Don't Talk to the Police, a resurrected grave, then a lost one | "791 recommended videos are dead. The Necromancer recovers each title from the Wayback Machine and hunts for a re-upload. A ghost means I found one; a cracked stone means it's gone." |
| 1:50-2:20 | Kiro chat calling the Séance: "find a classic talk on distributed systems", then "what's in the graveyard?" | "The Séance is an MCP server, so Kiro can query the archive directly." |
| 2:20-2:50 | `.kiro/` folder: specs, steering, hook firing after an edit | "Built in Kiro with specs per stage, steering for the theme and tech rules, and a hook that runs the tests on every write." |
| 2:50-3:00 | Token comparison line | "Same idea, twice the videos, half a percent of the tokens." |
