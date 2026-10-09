# Next session: refine editwright on the owner's reactions

Paste everything below the line into a fresh Claude Code session started in the editwright repository.

---

Continue editwright (public repo m4bwav/editwright, v0.1.0 released, installed as editwright@mark-local). Read `AGENTS.md`, `ai-docs/HANDOFF.md`, the end of `ai-docs/log.md` and `skills/editwright/LEARNINGS.md` first. Use the installed editwright skill for any edit work; the works store is configured in `~/.editwright.json` (private, never copy anything from it into the repository).

The first real pass on the owner's short story is done (job `the-old-crash-site/20261008-1-full` in the works store: `editorial-letter.md`, `suggestions.md`, `provenance-ledger.md`, `review.docx`). The owner was asked which suggestion IDs they accept and what felt off: too timid, too pushy, missed the point, or crossed into rewriting.

1. If the owner's reactions are in this conversation, turn each into a fix. Route each with `evergreen-learn`: author-specific taste goes to the author's preferences file (`ew.py feedback` plus a line in `authors/<slug>.md`); a general lesson with no identifying details goes to `skills/editwright/LEARNINGS.md` or a kb file. If the reactions are not here yet, ask for them and stop.
2. 0.1.1 (L-001 and L-002 fixes) is in pull request #2. If it is merged: tag v0.1.1 on main, `gh release create v0.1.1` with `python scripts/package.py`'s `dist/editwright.zip` and the CHANGELOG entries as notes, `claude plugin marketplace update mark-local`, reinstall editwright@mark-local, and update the wiki's version-bearing pages (list in `ai-docs/notes/2026-10-08-wiki-run/2026-10-08-github-wiki.md`). If it is not merged yet, say so and continue with the owner's reactions on the 0.1.0 install.
3. Re-run the job's suggestions through 0.1.1 before applying (`ew.py suggest <job> <file> --replace-all` keeps the same IDs when the file is the same), so the ledger shows 0 AI-written words for the corrections.
4. Apply only the IDs the owner accepts, into a new file (`ew.py apply ... --accept ...`); words the owner types for a query go in with `--author-text`. Run `ew.py check`, and confirm the Google Doc's modified time is unchanged (Drive connector metadata, read only). Never write to the Google Doc.
5. Repeat until the owner says it is good.

Rules: no AI attribution anywhere; plain short sentences, no em dashes in repository prose; nothing private in the public repository; estimate in agent time. Keep `ai-docs/` current (log, HANDOFF, decisions).

Before you stop, rewrite `ai-docs/next-session-prompt.md` for the session after yours, and end it with this same instruction: write the next prompt, with this instruction included.
