# Changelog: editwright

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20261107-1 · 2026-11-07 · Non-author intake question; Nebula wording from the rule; detector and watermark facts
- because: R-20261107-1
- files: SKILL.md (Step 1: intake), kb/ai-text-rules.md, kb/short-story.md (Nebula line)
- Intake asks a non-author about contract limits. The Nebula line now quotes the rule.

### C-20261106-1 · 2026-11-06 · Release 0.2.2: believing pass and two-sides flag
- because: user request (book distillation, Tannen, The Argument Culture)
- files: kb/nonfiction.md (Argument check)
Two argument steps added. Not yet run on a manuscript.

### C-20261105-1 · 2026-11-05 · Release 0.2.1: style flags name their ground
- because: user request (book distillation, Cameron, Verbal Hygiene)
- files: kb/line-copy-proof.md (Before a pervasive or laborious change), SKILL.md (metadata)
- A style flag now says whether it rests on reader harm, a house rule or taste. Not yet run on a manuscript.

### C-20261104-1 · 2026-11-04 · Release 0.2.0: Saller's copyediting practice; apply refuses a changed source
- because: R-20261104-1, user request
- files: kb/deliverables.md (queries, Handover), kb/line-copy-proof.md (Before a pervasive or laborious change, Repeated fixes), kb/long-manuscripts.md, kb/INDEX.md, SKILL.md (Step 4, Step 5, metadata), scripts/ew.py (VERSION, source_drift, cmd_apply, cleanup, cmd_intake, cmd_suggest), ../../tests/test_ew.py, ../../.claude-plugin/plugin.json, ../../plugin.json, evergreen.json
- `apply` refuses when the author's source changed since intake, says per ID whether its quote survives, takes `--against` for a fresh export and `--from-snapshot` on the author's plain words, which the changelog records. A byte-only change passes with a note. Cleanup already logged by type; it now also logs extra blank lines and every em dash it makes, and intake prints the types. The suggest skip key includes `occurrence`, so a repeated fix listed per location in one paragraph is no longer dropped. No word-changing rule was added.

### C-20261008-4 · 2026-10-08 · suggest keeps the valid items; eval cases get 30 turns
- because: L-002, T-20261008-4
- files: scripts/ew.py (cmd_suggest), SKILL.md (Step 3), references/suggestion-format.md, ../../tests/test_ew.py, ../../evals/build_cases.py (max_turns in prompt.md frontmatter)
- `suggest` saves every valid suggestion, lists refused ones by item number and skips items already saved, so a resubmitted file adds only the fixed ones. The Bash eval cases run with 30 turns and 600 seconds (prompt.md frontmatter) instead of the defaults of 10 and 300, and outcome-1's judge criterion says that showing a cut or typo fix made of the author's own words is fine.

### C-20261008-3 · 2026-10-08 · Release 0.1.1
- because: L-001, the wiki run of 2026-10-08 (../../ai-docs/notes/2026-10-08-wiki-run/2026-10-08-github-wiki.md)
- files: ../../.claude-plugin/plugin.json, ../../plugin.json, scripts/ew.py (VERSION), SKILL.md (metadata), evergreen.json, ../../README.md (Privacy), kb/delivery.md
- Version 0.1.1 in the five places AGENTS.md lists. README Privacy lists the full works-store lookup order. kb/delivery.md names suggestions.json as the source of truth.

### C-20261008-2 · 2026-10-08 · Real corrections stop counting as AI-written words; copied runs count; cleaner refusals
- because: L-001 corrections-of-own-words-counted-as-ai, the wiki run of 2026-10-08
- files: scripts/ew.py (IRREGULAR, CONFUSED, is_correction, nearby_words, provenance, echoed_words, cmd_apply changelog, remove_tree, cmd_intake), ../../tests/test_ew.py
- A change between forms of one irregular word (says to said, are to were) or between commonly confused words (road to rode, your to you're) is a correction of the author's word. A one-for-one swap to a content word the author wrote in the same or a neighbouring paragraph (blanks to planks) counts as the author's; a pure addition never does. Author text that copies a run of three or more words from the suggestion now counts the common words in that run as AI-written too. The apply changelog says "the author wrote N new words" for author text. A refused intake (for example a PDF without --text) writes nothing. On the first real story the ledger went from 3 AI-written words, all false, to 0.

### C-20261008-1 · 2026-10-08 · Created as an evergreen unit
- because: user request
- files: SKILL.md, RESEARCH.md, LEARNINGS.md, evergreen.json (skills: also TESTS.md and evals/evals.json)
- Initial version. Tier `moderate`, interval 30d. See R-20261008-1 for the research basis; the first test run, for a skill, is logged in TESTS.md.
