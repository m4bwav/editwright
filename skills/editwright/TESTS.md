# Tests: editwright

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json`. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md); counts and the failing list are in `evergreen.json` under `tests`. Rules: MAINTENANCE.md (testing section) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines; archive older runs to `TESTS-ARCHIVE.md`.

## Runs

### T-20261008-3 · 2026-10-08 · claude plugin eval 2.1.281 (default model), --ablation with-without · WSL2 Ubuntu (Bash cases) · 4/4
- action-1 with 1.00, without 0.29; action-2 with 0.92, without 0.75; action-3 with 1.00, without 0.00; outcome-1 with 1.00, without 0.67. Mean delta +0.55, $5.10, 229 s.
- action-2: one of three runs never called `ew.py apply` (it read the ledger and declined S-004 itself). No edited file was written and the source was unchanged, so the outcome held; the grader for the apply call failed that run.
- Baseline arm: the model without the skill edited story.txt in place (source-unchanged failed) and gave a revised story in outcome-1.
- untested elsewhere: native Windows cannot grant Bash to the eval harness; macOS and Linux hosts not run.
- led to: none

### T-20261008-2 · 2026-10-08 · claude plugin eval 2.1.281 (default model), --ablation none · Windows 11 native · 5/5
- trigger-1, trigger-2, trigger-3: 3 of 3 runs each invoked editwright ($0.92). decoy-1 ("write me a short story") and decoy-2 ("humanize this"): 0 of 3 ($0.35).
- Unit tests: `python tests/test_ew.py` 26/26; CI on Linux, macOS and Windows with Python 3.9 and 3.14 green (run 37879403929).
- led to: none

### T-20261008-1 · 2026-10-08 · not yet run · skill · 0/0
- Suite scaffolded; no run recorded. Write the cases in `evals/evals.json` (at least two trigger prompts, two decoys, one action case with evidence, one outcome case), run the baseline without the skill, then run with it (`evergreen-test`).
- led to: none
