---
title: Long manuscripts
kind: kb
checked: 2026-10-08
summary: Read when the manuscript runs 80k to 150k words; chapter cards, bible as memory, map/reduce passes and token budgets.
---
# Long manuscripts (80k to 150k words)

Source for this file: [scripts, nonfiction and books note](../../../ai-docs/research/2026-10-08-scripts-nonfiction-books.md), section 3.

## Why the procedure exists
- NoCha (arxiv.org/abs/2406.16264): true/false claims about novels. Best model then 55.8% pair accuracy; far better on one-sentence claims than global ones; wrong explanations even for right labels; worse on speculative fiction with heavy world-building.
- FABLES (arxiv.org/abs/2404.01261): unfaithful summary claims were mostly about events and character states and needed indirect reasoning to catch. Summaries omitted key elements and over-weighted late events. No LLM rater matched humans at spotting unfaithful claims.
- Too Long, Didn't Model (arxiv.org/abs/2505.14925): no frontier model kept stable plot, world and time understanding past 64k tokens.
- PRELUDE (arxiv.org/abs/2508.09848): right answers for wrong reasons; 30%+ reasoning gap to humans.
- These test older models; no 2026 result shows the problem solved.

Rules that follow:
1. A 1M window lets the model see the book. It does not make global judgements reliable.
2. Every global claim ("the subplot is dropped", "she already knew this in chapter 3") needs quoted passages with chapter and paragraph, re-checked against those passages.
3. Build summaries per chapter from the text, short and factual.
4. Never let the model grade its own summary as faithful.

## Memory files (beside the manuscript, not in chat)
- `style-sheet.md`: style decisions.
- `chapter-cards/NN.md`, 300 to 500 tokens each: one line per scene with its function, characters present, timed events, facts asserted (names, ages, places, objects), open threads, the chapter's job. Each line cites a location.
- `bible.md` (fiction) or `claims.md` (nonfiction), merged from the cards, under about 20k tokens.
- `continuity-log.md`: each conflict, both locations quoted, open or resolved by the author.
- `notes/`: letter and per-chapter notes.

## Passes
0. Measure: count words and tokens. Split at chapter headings (scene breaks in long chapters). Chunks of 4k to 10k words.
1. Map: one call per chapter, chapter plus style sheet. Output the card only; no opinions yet.
2. Reduce: merge cards into the bible and a one-line-per-chapter outline. A fact with two values is a candidate continuity error; log both locations. (Hierarchical merging was more coherent than one running summary: BooookScore, arxiv.org/abs/2310.00785.)
3. Verify: for each candidate and global note, load only the cited passages; confirm or drop; quote the lines.
4. Developmental read: outline, bible and verified log; write the letter citing chapters.
5. Line and copy: per chapter, with style sheet, that chapter's card, bible entries for who and what appears, neighbouring cards. Suggestions only.

## Token budgets
Tokens per word is unresolved. Anthropic's model page says 1M tokens is about 555k words on the current tokenizer (about 1.8 tokens a word) and about 750k on older models (about 1.33), yet the same page says 200k tokens is about 150k words, the old ratio (platform.claude.com/docs/en/models/opus-4-7/overview). Plan with 1.8 and count real tokens before committing. Dialogue, names and invented words push it up.

| Words | x1.8 | x1.33 |
|---|---|---|
| 80k | ~144k | ~107k |
| 100k | ~180k | ~133k |
| 120k | ~216k | ~160k |
| 150k | ~270k | ~200k |

1M-context model:
- The whole book fits. Use one whole-book call only for "find all mentions" questions, and still verify by quoting.
- Passes 1 and 5 per call: instructions ~5k, style sheet ~2k, bible ~20k, chapter 7k to 18k, neighbours ~2k, output reserve 8k to 16k. Total 45k to 65k, near the 64k drift region.
- Pass 4: outline 3k to 6k plus bible ~20k plus log, under 50k; add up to three chapters if needed.
- Cache the fixed prefix (instructions, style sheet, bible) across chapter calls; batch when results can wait.

200k-context model:
- Never load the whole book; a 100k-word novel is about 180k tokens.
- Per call: instructions ~4k, style sheet ~2k, bible capped ~15k, chapter up to ~18k, output ~8k. About 50k; keep half the window free.
- Global questions go through the bible, cards and targeted passage loads only. Past 15k, split the bible (characters, places, timeline) and load only what a chapter touches.

Nonfiction uses the same passes: cards carry each chapter's claim, grounds, warrant and checkable facts; reduce builds the argument map and claim table ([nonfiction.md](nonfiction.md)).

Related: [deliverables.md](deliverables.md), [fiction.md](fiction.md), [nonfiction.md](nonfiction.md), [levels.md](levels.md)
