# Tasks: Exorcist

- [x] 1. Prompt with fixed crypt list and JSON reply format (req 1, 2)
- [x] 2. `parse_labels` with unit tests for strays, duplicates, bad crypts and garbage (req 3)
- [x] 3. Resumable cache, usage file, early stop on long rate limits (req 4-6)
- [x] 4. Atomic `videos.json` write and `--limit` sampling (req 7, 8)
- [x] 5. 200-video sample: check labels by hand, measure tokens per video
  (v1 prompt dropped classics like Jobs' Stanford speech as "passing mentions"; v2 keeps by default)
- [ ] 6. Full run; record kept count and total tokens in README
