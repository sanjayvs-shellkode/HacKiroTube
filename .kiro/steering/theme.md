# Theme and voice

- Halloween, but the theme maps to real behaviour: dead video = deleted video, resurrection = found copy.
  Art that carries state must match the data: a ghost rising from a tombstone only for a found re-upload,
  a cracked stone only for a lost video. Ambient cartoons (moon, bats, the mascot ghost) live in the header
  and empty states only, never on top of content.
- Vocabulary: topics are "crypts", dead videos get "tombstones", long-lived favourites are "immortals",
  the MCP server is the "seance". Keep these terms consistent in code, UI and docs.
- Palette: Kiro violet. Background #19161d / panels #211d25, text #f3eefb, accent violet #b080ff,
  buttons and active state #7138cc with white text, ghost green #80ffb5 for links, pumpkin #ff9a4d for the
  Immortal badge only.
- Art: hand-drawn inline SVG in `site/src/art.ts`, decorative and `aria-hidden`; no external image assets.
- UI copy is short and a little wry. Accessibility is not optional: contrast AA, keyboard navigable,
  respect `prefers-reduced-motion` (all animation sits inside a `no-preference` query).
