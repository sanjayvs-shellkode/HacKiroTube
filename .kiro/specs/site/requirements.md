# Requirements: Site

## User story
As a visitor, I want to browse what HN recommends by crypt, find the long-lived immortals,
and mourn the dead in a graveyard, quickly and from the keyboard, with no account.

## Acceptance criteria (EARS)
1. THE SYSTEM SHALL be a static Vite + TypeScript build that loads one `catalog.json` from `pipeline/publish.py`.
2. THE SYSTEM SHALL offer three views by URL hash: Crypts (filterable by crypt), Immortals (5+ people over 10+ years),
   and Graveyard (tombstones, most-mourned first).
3. WHEN the visitor types in search THE SYSTEM SHALL filter the current view by title.
4. THE SYSTEM SHALL support j/k, o/Enter, w, /, 1-3, x and ? shortcuts, with a help dialog listing them.
5. THE SYSTEM SHALL store watched videos in localStorage only.
6. WHEN the visitor exports THE SYSTEM SHALL download the current filtered view as JSON.
7. THE SYSTEM SHALL label a re-upload as a "possible" resurrection and always link dead videos to archive.org.
8. THE SYSTEM SHALL meet AA contrast, be fully keyboard navigable, and disable transitions under
   `prefers-reduced-motion`. Status is conveyed in text, never colour alone.
