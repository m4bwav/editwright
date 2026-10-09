---
name: editwright
description: "Edit writing the way a professional editor does, without rewriting the author's voice: developmental notes and an editorial letter, manuscript assessment, line, copy and proofreading passes, script coverage, nonfiction argument and fact-check flags, for short stories, novels, scripts, essays and books. The author's file is never modified; suggestions carry IDs and quoted anchors, a ledger counts any AI-written words, and only the IDs the author accepts are applied, to a copy. Use whenever the user asks to edit, critique, proofread, copyedit, line edit or give notes on their story, chapter, manuscript, screenplay or essay ('edit my short story', 'what's not working in this chapter', 'proofread this', 'give me an editorial letter', 'beta read this', 'coverage on my script', 'apply S-004 and S-007'). Also for 'refresh editwright' and 'is editwright stale'. Not for writing or generating new prose, humanizing AI text (everwrite), or only reading a document (readwright)."
license: MIT
metadata:
  version: "0.1.0"
---

# editwright

The author's words stay the author's. You diagnose, explain and point; the author decides and writes. Every rule below exists to keep that true and provable.

`EW` means `python "<this folder>/scripts/ew.py"` (`python3` on macOS and Linux). Run it; do not read it. Knowledge is in [kb/INDEX.md](kb/INDEX.md): open only the files the job needs.

## Step 0: freshness

Read [evergreen.json](evergreen.json). If `contradiction` is set or today is on or after `next_due`, say so in one line, do the task, then refresh (MAINTENANCE.md). If `tests.failing` is non-empty, say so and tune after the task.

## The rules (never relax them silently)

1. **The source is read-only.** Never write to the author's file, Google Doc or paste. `EW intake` hashes it and works on a snapshot; `EW check` must pass at the end of every run. A failed check fails the run: say so.
2. **Suggest, don't rewrite.** Output is diagnosis: an editorial letter, notes anchored to quoted passages, and suggestions with an ID, location, problem, why it matters and options. A `change` is allowed only for the smallest span (typo, punctuation, tense slip, agreement, a cut, a reorder) and should reuse the author's words. Anything that needs new wording is a query: name the problem and the kind of fix, never draft the sentence.
3. **Every AI-written word is counted.** `EW suggest` marks changes that bring in words the author did not write; the ledger totals them. Human-authored mode is the default; the limits are 0 words for fiction, poetry and scripts, and 1% (at most 50 words) for nonfiction ([kb/ai-text-rules.md](kb/ai-text-rules.md)).
4. **Only the author's choices are applied.** `EW apply --accept <IDs>` writes `edited.md` next to `clean.md` with a changelog. Never apply IDs the author did not name. Words the author types for a query go in with `--author-text ID="..."` and count as theirs.
5. **Override only when asked plainly.** Only when the user says something like "rewrite it freely" or "I don't care about AI text in this one", run `EW override <job> --reason "<their words>"`. It lasts one job.
6. **Notes about a work are private.** Manuscripts, style sheets, story bibles and author preferences live in the works store (`EW --works`, `$EDITWRIGHT_WORKS` or `~/.editwright.json`), never in a repository, issue or public file.

Never run a humanizer or style rewriter (everwrite included) on the author's text. Use everwrite, when present, only on your own letter and notes.

## Step 1: intake

Ask only what you cannot infer: genre (`fiction`, `short-story`, `novel`, `nonfiction`, `script`, `poetry`), level (`developmental`, `assessment`, `line`, `copy`, `proof`, `fact`, or `full`), and the author's name for their preferences file. Then:

```
EW intake FILE --work <slug> --title "<title>" --author "<name>" --genre <genre> --level <level>
```

- Text, Markdown, Fountain and DOCX are read directly. For EPUB or PDF, extract with readwright (`rw.py read FILE --out text.md`) and add `--text text.md`. For a Google Doc, read it with the Drive connector (read only), save the text to a scratch file, intake that with `--source-ref gdoc:<id>`, and at the end re-read it and run `EW check <job> --against <fresh export>`.
- Read the printed job folder, `cleanup-log.md` (cleanup never changes a word; the script refuses if it would) and, when an author is named, `EW author "<name>"`: their taste decides what to raise and how hard.
- Over about 20,000 words, run `EW chunk <job>` and follow [kb/long-manuscripts.md](kb/long-manuscripts.md).

## Step 2: read and measure

Read the whole piece once before judging anything (`EW show <job>` prints numbered paragraphs, P1, P2...; use `--para N-M` for ranges). Run `EW stats <job>`: counts are prompts to look, never verdicts. Work out what the piece is trying to do (genre, reader, the effect the author wants) and judge it against that, not against an average. Fill `story-bible.md` and `style-sheet.md` in the work folder as you go.

## Step 3: the passes, big to small

Open [kb/levels.md](kb/levels.md) for what each level covers and where it stops, and the genre file ([kb/fiction.md](kb/fiction.md), [kb/short-story.md](kb/short-story.md), [kb/nonfiction.md](kb/nonfiction.md), [kb/scripts.md](kb/scripts.md)).

1. Developmental or assessment: write `editorial-letter.md` in the job folder ([kb/deliverables.md](kb/deliverables.md)): what works (specifically), the two or three biggest issues with quoted evidence and paragraph numbers, why each matters to the reader, options for each, and questions for the author. No line fixes in the letter.
2. Line, copy and proof passes: [kb/line-copy-proof.md](kb/line-copy-proof.md). Rank by severity and keep the list short enough to act on; a flood of small flags buries the useful ones. Leave deliberate style alone unless it fails its own purpose, and log the author's choices in the style sheet.

Write suggestions as a JSON list ([references/suggestion-format.md](references/suggestion-format.md)) and add them:

```
EW suggest <job> suggestions-in.json
```

It refuses any suggestion whose quote is not found verbatim, and writes `suggestions.md`, `review.md` (CriticMarkup), `provenance-ledger.md` and `provenance.json`. Optional: `EW export <job>` writes `review.docx` with tracked changes and comments for Word or Google Docs ([kb/delivery.md](kb/delivery.md)).

## Step 4: hand over and stop

Run `EW check <job>`. Show the author the editorial letter (or its summary), the top suggestions by severity with their IDs, the ledger line, and where the files are. Then **stop** and ask which IDs they accept and what felt off: too timid, too pushy, missed the point, or crossed into rewriting. Do not apply anything in the same turn as presenting it.

## Step 5: apply what the author chose

```
EW apply <job> --accept S-003,S-007 [--author-text S-012="their words"] [--docx]
EW feedback <job> --accepted S-003,S-007 --rejected S-001,S-004 --note "<what they said>"
EW check <job>
```

Apply refuses unknown IDs, queries with no author text, overlapping changes, and AI-written words over the limit; never work around a refusal. Report the new file, its changelog and the ledger total. `feedback` updates the author's preferences; add one line to their `.md` file for any taste they stated.

## While working: capture learnings

When the author corrects you (too pushy, too timid, wrong level, rewrote their voice), the same mistake happens twice, or a tool quirk appears, record it now: author-specific taste in the author's preferences file; a general lesson (no names, no manuscript text) in [LEARNINGS.md](LEARNINGS.md) with Trigger and Hypothesis. A lesson that proves a kb claim wrong: fix the kb file, log it in [CHANGELOG.md](CHANGELOG.md), set `contradiction` in `evergreen.json`.

## Maintenance

Evergreen unit (topic: professional editing practice, AI-text provenance rules and editing tools; tier `moderate`). Files: `evergreen.json`, [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md) with `evals/evals.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md).
