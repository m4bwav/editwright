# Learnings: editwright

Procedural lessons for [SKILL.md](SKILL.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first, by meaning (`evergreen.py search "<the lesson>" --kinds learnings` finds near-duplicates in every registered unit): add / update / retire / none. Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-002 · 2026-10-08 · suggest-refusal-costs-the-run: one bad quote plus the 10-turn eval default ended runs with nothing saved
- Trigger: 0.1.1 eval run, 2026-10-08: in two of three action-1 runs `ew.py suggest` refused the whole file over one quote that did not match clean.md, and the run hit the harness default of 10 turns before resubmitting, so no suggestions.json, ledger or check existed. An outcome-1 run was cut off at the limit before its reply.
- Hypothesis: the editing flow (skill, intake, show, stats, write JSON, suggest, check, reply) needs 8 to 12 turns; an all-or-nothing refusal adds two more.
- Rule: suggest saves the valid items and lists the refused ones; eval cases that run the full flow set `max_turns: 30` in prompt.md frontmatter (case.yaml ignores it).
- Evidence: T-20261008-4, C-20261008-4
- Scope: skill
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-08

### L-001 · 2026-10-08 · corrections-of-own-words-counted-as-ai: real typo and tense fixes counted as AI-written words
- Trigger: first real short-story pass (3,986 words), 2026-10-08. Of 35 proposed changes, three were scored as one AI-written word each although each only corrected the author's own word: says to said and road to rode (two edits on a four-letter word; the rule allows one) and blanks to planks (first letter differs; the author writes "planks" in the next sentence).
- Hypothesis: the correction rule (same first letter, at most one edit up to four letters) misses irregular verb forms and first-letter typos, and it ignores words the author already used nearby.
- Rule: count a replacement word as the author's when it is a known inflection of the removed word (irregular forms included) or when the same word appears in the author's text of the same or next paragraph; keep everything else strict.
- Evidence: job ledger of 2026-10-08 (private works store), T-20261008-3, fixed by C-20261008-2 (ledger 3 to 0 on the same job)
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-10-08
