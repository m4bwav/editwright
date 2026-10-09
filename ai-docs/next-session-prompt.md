# Next session: refine editwright on the owner's reactions

Paste everything below the line into a fresh Claude Code session started in the editwright repository.

---

Continue editwright (public repo m4bwav/editwright, v0.1.0 released, installed as editwright@mark-local). Read `AGENTS.md`, `ai-docs/HANDOFF.md`, the end of `ai-docs/log.md` and `skills/editwright/LEARNINGS.md` first. Use the installed editwright skill for any edit work; the works store is configured in `~/.editwright.json` (private, never copy anything from it into the repository).

The first real pass on the owner's short story is done (job `the-old-crash-site/20261008-1-full` in the works store: `editorial-letter.md`, `suggestions.md`, `provenance-ledger.md`, `review.docx`). The owner was asked which suggestion IDs they accept and what felt off: too timid, too pushy, missed the point, or crossed into rewriting.

1. If the owner's reactions are in this conversation, turn each into a fix. Route each with `evergreen-learn`: author-specific taste goes to the author's preferences file (`ew.py feedback` plus a line in `authors/<slug>.md`); a general lesson with no identifying details goes to `skills/editwright/LEARNINGS.md` or a kb file. If the reactions are not here yet, ask for them and stop.
2. Fix LEARNINGS L-001 `corrections-of-own-words-counted-as-ai` in `ew.py` (irregular verb forms; a replacement word the author already uses in the same or next paragraph), with tests in `tests/test_ew.py`.
3. Re-run the affected evals (`python evals/build_cases.py` if the job format changed; triggers natively, Bash cases in WSL2 as AGENTS.md says), log a `T-` entry, bump to 0.1.1 in the five places AGENTS.md lists, and open a pull request assigned to m4bwav with the label needs-review. After it is merged, tag v0.1.1, publish the release with `editwright.zip`, and update the local install (`claude plugin marketplace update mark-local`, then reinstall).
4. Apply only the IDs the owner accepts, into a new file (`ew.py apply ... --accept ...`); words the owner types for a query go in with `--author-text`. Run `ew.py check`, and confirm the Google Doc's modified time is unchanged (Drive connector metadata, read only). Never write to the Google Doc.
5. Repeat until the owner says it is good.

Rules: no AI attribution anywhere; plain short sentences, no em dashes in repository prose; nothing private in the public repository; estimate in agent time. Keep `ai-docs/` current (log, HANDOFF, decisions).

Before you stop, rewrite `ai-docs/next-session-prompt.md` for the session after yours, and end it with this same instruction: write the next prompt, with this instruction included.
