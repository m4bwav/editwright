---
title: One skill with an on-demand kb, not sibling skills
kind: decision
status: active
date: 2026-10-08
verified: 2026-10-08
stale_after: 2027-04-06
tags: [design, skills]
summary: read before adding a skill to editwright
---

# One skill with an on-demand kb, not sibling skills

## Context
The kickoff allowed a router skill plus "as few sibling skills as the research justifies" (developmental, line/copy/proof, apply/provenance). Every skill's description is loaded in every session, and on claude.ai each uploaded skill is a separate folder that cannot reach a sibling's scripts (cinewright LEARNINGS L-006 `claude-ai-plugin-skill-folder-unknown`).

## Decision
One skill, `editwright`, holds the rules, intake, the passes and apply. Level and genre knowledge sits in `skills/editwright/kb/` (eleven small files, read on demand from `skills/editwright/kb/INDEX.md`); the JSON format sits in `references/`; one CLI, `skills/editwright/scripts/ew.py`, sits inside the skill folder.

## Reasons
- The levels share one intake, one rule set, one suggestion file and one ledger; splitting them would repeat the rules in each SKILL.md and risk a sibling that forgets them.
- One description (979 characters) is the smallest always-loaded cost; the kb costs nothing until a pass needs it.
- The skill folder is self-contained, so the claude.ai ZIP upload works with its script and kb.
- Triggers for "proofread this", "editorial letter", "apply S-004" all fit one description.

## Rejected alternatives
- Router plus developmental, line-copy-proof and apply skills: four descriptions loaded every session and the rules copied four times, for no trigger the single description misses.
- Separate genre skills (fiction, scripts, nonfiction): genre is knowledge, not procedure; kb files do it cheaper.

## Consequences
SKILL.md must stay short (budget: 2,500 tokens green). Revisit if a trigger case shows the single description missing a level (for example plain "proofread" requests going elsewhere), or if apply needs to run without the editing context.

Related: see also [../research/2026-10-08-tools-survey.md](../research/2026-10-08-tools-survey.md)
