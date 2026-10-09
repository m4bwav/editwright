# Handoff

Updated 2026-10-09. Read this first, then [log.md](log.md) and [next-session-prompt.md](next-session-prompt.md).

## Current state

- Public repo https://github.com/m4bwav/editwright, v0.1.1 released 2026-10-09 (tag on main 8d9a0d5, `editwright.zip` asset, 21 files, 70 KB). v0.1.0 also released (2026-10-08).
- Installed as editwright@mark-local, still the 0.1.0 install: the marketplace update and reinstall were refused by the auto-mode classifier on 2026-10-09 and are left for the owner (`claude plugin marketplace update mark-local`, then uninstall and install editwright@mark-local). Until then run `skills/editwright/scripts/ew.py` from the main checkout, which is 0.1.1.
- Unit tests 31/31; CI green on Linux, macOS, Windows with Python 3.9 and 3.14. Eval suite 9/9 (T-20261008-5).
- Wiki at 0.1.1 (commit e9b7a76), verified; see [the wiki notes](notes/2026-10-08-wiki-run/2026-10-08-github-wiki.md).
- README banner merged (PR #3).
- First real pass on the owner's short story: job `the-old-crash-site/jobs/20261008-1-full` in the private works store. Resubmitted under 0.1.1 on 2026-10-09 with `--replace-all`: the same 53 IDs, ledger 0 AI-written words (S-012, S-022, S-025 went from 1 to 0), review.docx re-exported, check passed, the Google Doc's modified time still 2026-04-02 (unchanged). Waiting for the owner's reactions.

## Open

- Issue #4: suggest's skip key is built before validation and leaves out `problem` (L-003). Fix for 0.1.2: key after validation, add `problem`, no write when nothing was added, a test with items without `para`. Workaround: `--replace-all` and a `para` on every note.
- wikiwright issue #10 (diffout splits on `## ` inside output). wikiwright PR #9 (L-153, L-154) from the first wiki run.
- Design question for the owner: the nearby-word rule credits any swap to a content word in a neighbouring paragraph, even a change of meaning (cart to wagon). Keep, or require the swap to look like a typo fix?

## Next single action

Run [next-session-prompt.md](next-session-prompt.md).
