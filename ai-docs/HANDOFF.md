# Handoff

Updated 2026-10-08. Read this first, then [log.md](log.md) and [next-session-prompt.md](next-session-prompt.md).

## Current state

- Public repo https://github.com/m4bwav/editwright, v0.1.0 released 2026-10-08 (tag on main e7bd36e, `editwright.zip` asset). Installed as editwright@mark-local (user scope) and registered in evergreen.
- One skill (`skills/editwright/`), 11 kb files, `ew.py` CLI. Unit tests 26/26; CI green on Linux, macOS, Windows with Python 3.9 and 3.14; budget green (description 979 chars, SKILL.md about 2,050 tokens).
- Eval suite 9/9 (TESTS.md T-20261008-2 and T-20261008-3): triggers 3/3 each, decoys 0/3 each, Bash cases with the skill 1.00, 0.92, 1.00, 1.00 against 0.29, 0.75, 0.00, 0.67 without. Bash cases run in WSL2 (see AGENTS.md Commands).
- Research: five notes in [research/](research/); decisions: one skill, word limits and counting, works store and sync off.
- First real pass done on the owner's short story (run with 0.1.0): job in the private works store (the vault sidecar's `works/`, see the decision on the works store). 53 suggestions, editorial letter, review.docx, check passed, the Google Doc's modified time unchanged. Waiting for the owner's reactions.

## In progress

- The owner reviews the letter and suggestions and says which IDs they accept and what felt off.
- README hero image: a background run was still generating at the end of the session; if no hero-image pull request exists, make one (comfyui-gen skill, banner at assets/banner.jpg like cinewright).

## 0.1.1 (pull request #2, waiting for review)

- Fixes LEARNINGS L-001 `corrections-of-own-words-counted-as-ai` (irregular forms, commonly confused words, the author's own word nearby; on the owner's story the ledger went from 3 false AI words to 0) and the wiki run's findings (echo check counts copied runs, changelog wording for author text, a refused intake writes nothing, README Privacy lookup order, kb/delivery source of truth). Tests 31/31, evals 9/9 (T-20261008-5); also L-002 (suggest keeps valid items; eval cases need 30 turns in prompt.md frontmatter).
- After merge: tag v0.1.1, release with `editwright.zip`, `claude plugin marketplace update mark-local` and reinstall, update the wiki's version-bearing pages (list in [notes/2026-10-08-wiki-run/](notes/2026-10-08-wiki-run/2026-10-08-github-wiki.md)).
- wikiwright lessons from the wiki run: m4bwav/wikiwright PR #9 (L-153, L-154).

## Next single action

Run [next-session-prompt.md](next-session-prompt.md).
