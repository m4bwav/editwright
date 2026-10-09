---
title: Human-authored defaults and how AI-written words are counted
kind: decision
status: active
date: 2026-10-08
verified: 2026-10-08
stale_after: 2027-04-06
tags: [provenance, thresholds]
summary: read before changing the word limits or the counting rule
---

# Human-authored defaults and how AI-written words are counted

## Context
The kickoff asked for a provenance ledger, a word limit that apply enforces, 0 new words in fiction and a small allowance in nonfiction, with the numbers decided and explained. The research ([../research/2026-10-08-ai-text-provenance.md](../research/2026-10-08-ai-text-provenance.md)) found that since 2026-08-14 Claude watermarks words it chooses, that KDP separates AI-assisted editing from AI-generated text, that the Authors Guild Human Authored mark allows only de minimis AI text, and that Clarkesworld, Asimov's, Uncanny, Writers of the Future and the Nebulas refuse AI-written text. No policy publishes a number.

## Decision
- Limits in human-authored mode (`THRESHOLDS` in `ew.py`): 0 AI-written words for fiction, short stories, novels, poetry, scripts and other; nonfiction 1% of the piece and at most 50 words per job, whichever is lower.
- Counting: a change's words are compared with the span it replaces. Reused words, cuts, reorders, punctuation, and spelling or inflection corrections of the author's own word (same first letter, at most one edit for words up to four letters and two for longer) count as the author's. Everything else is AI-written.
- Words the author types (`--author-text`) are the author's, except words that the same suggestion offered in its `change` or `options` and the author did not have before: those are counted as AI-written (no laundering).
- `apply` requires explicit IDs (no "all"), refuses unknown IDs, queries without author text, overlapping changes, and any total over the limit. `override` needs the user's own words as its reason and lasts one job.

## Reasons
- 0 in fiction is the only number that is safe under the strictest venues, which forbid any AI-written text.
- Nonfiction fixes (a missing article, a connective) are routine and KDP calls editing "AI-assisted"; 1% capped at 50 words keeps that to trivial amounts.
- Corrections of the author's own word are the mechanical fixes the Authors Guild and the Copyright Office's proofreading box accept; treating them as the author's lets proofreading work at 0.
- The echo rule answers the Grammarly Authorship laundering bug the tools survey found.

## Rejected alternatives
- A per-chapter cap (the research's proposal): a job is often a chapter already, and per-job is simpler to explain and check.
- Allowing approved mechanical fixes in fiction as a setting: the correction rule already covers them without a setting.
- Counting words from anywhere in the manuscript as the author's: the AI still chose and placed them.

## Consequences
A one-letter word swap (hat to hot) passes as a correction; the ledger lists every correction by name so the author can see it. Contractions ("do not" to "don't") count as one AI-written word. Revisit when a policy publishes a number or the author asks for a different limit.

Related: builds on [../research/2026-10-08-ai-text-provenance.md](../research/2026-10-08-ai-text-provenance.md); see also [../research/2026-10-08-tools-survey.md](../research/2026-10-08-tools-survey.md)
