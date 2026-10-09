# Handoff

Updated 2026-10-08. Read this first, then [log.md](log.md) and [next-session-prompt.md](next-session-prompt.md).

## Current state

- Public repo https://github.com/m4bwav/editwright, v0.1.0 released 2026-10-08 (tag on main e7bd36e, `editwright.zip` asset). Installed as editwright@mark-local (user scope) and registered in evergreen.
- One skill (`skills/editwright/`), 11 kb files, `ew.py` CLI. Unit tests 26/26; CI green on Linux, macOS, Windows with Python 3.9 and 3.14; budget green (description 979 chars, SKILL.md about 2,050 tokens).
- Eval suite 9/9 (TESTS.md T-20261008-2 and T-20261008-3): triggers 3/3 each, decoys 0/3 each, Bash cases with the skill 1.00, 0.92, 1.00, 1.00 against 0.29, 0.75, 0.00, 0.67 without. Bash cases run in WSL2 (see AGENTS.md Commands).
- Research: five notes in [research/](research/); decisions: one skill, word limits and counting, works store and sync off.
- First real pass done on the owner's short story: job in the private works store (the vault sidecar's `works/`, see the decision on the works store). 53 suggestions, editorial letter, review.docx, check passed, the Google Doc's modified time unchanged. Waiting for the owner's reactions.

## In progress

- The owner reviews the letter and suggestions and says which IDs they accept and what felt off.
- Background work started this session: the GitHub wiki (wikiwright run) and a README hero image (pull request with label needs-review). Check their results in log.md.

## Known issue to fix in 0.1.1

- LEARNINGS L-001 `corrections-of-own-words-counted-as-ai`: says to said, road to rode and blanks to planks are counted as AI-written words. Fix `is_correction`/`provenance` in `ew.py` (irregular forms, the author's own word nearby), add tests, rerun the suite.

## Next single action

Run [next-session-prompt.md](next-session-prompt.md).
