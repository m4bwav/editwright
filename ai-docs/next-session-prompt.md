# Next session: refine editwright on the owner's reactions

Paste everything below the line into a fresh Claude Code session started in the editwright repository.

---

Continue editwright (public repo m4bwav/editwright, v0.1.1 released 2026-10-09). Read `AGENTS.md`, `ai-docs/HANDOFF.md`, the end of `ai-docs/log.md` and `skills/editwright/LEARNINGS.md` first. Use the editwright skill for any edit work; the works store is configured in `~/.editwright.json` (private, never copy anything from it into the repository). If `claude plugin list` still shows editwright 0.1.0, ask the owner to run `claude plugin marketplace update mark-local` and reinstall editwright@mark-local (the auto-mode classifier refused it), and run `ew.py` from the main checkout meanwhile.

The first real pass on the owner's short story is done and re-scored under 0.1.1 (job `the-old-crash-site/jobs/20261008-1-full` in the works store: `editorial-letter.md`, `suggestions.md`, `provenance-ledger.md`, `review.docx`; 53 suggestions, 0 AI-written words). The owner was asked which suggestion IDs they accept and what felt off: too timid, too pushy, missed the point, or crossed into rewriting.

1. If the owner's reactions are in this conversation, turn each into a fix. Route each with `evergreen-learn`: author-specific taste goes to the author's preferences file (`ew.py feedback` plus a line in `authors/<slug>.md`); a general lesson with no identifying details goes to `skills/editwright/LEARNINGS.md` or a kb file. If the reactions are not here yet, ask for them, then do step 2 while you wait.
2. Fix issue #4 (L-003 `suggest-dedupe-key-before-validation`) as 0.1.2 on a branch: key built after validation, `problem` in the key, no write when nothing was added, a test with items that have no `para`. Bump the version in the five places AGENTS.md lists, CHANGELOG entry, run tests and evals, open a PR and assign it to the owner with label needs-review. After merge: tag, `gh release create` with `python scripts/package.py`'s zip, reinstall, and update the wiki's Suggestion-Format and FAQ fault notes (procedure in `ai-docs/notes/2026-10-08-wiki-run/2026-10-08-github-wiki.md`).
3. Apply only the IDs the owner accepts, into a new file (`ew.py apply ... --accept ...`); words the owner types for a query go in with `--author-text`. Run `ew.py check`, and confirm the Google Doc's modified time is still 2026-04-02 (Drive connector metadata, read only). Never write to the Google Doc.
4. Ask the owner the open design question in HANDOFF (nearby-word swaps that change meaning).
5. Repeat until the owner says it is good.

Rules: no AI attribution anywhere; plain short sentences, no em dashes in repository prose; nothing private in the public repository; estimate in agent time. Keep `ai-docs/` current (log, HANDOFF, decisions).

Before you stop, rewrite `ai-docs/next-session-prompt.md` for the session after yours, and end it with this same instruction: write the next prompt, with this instruction included.
