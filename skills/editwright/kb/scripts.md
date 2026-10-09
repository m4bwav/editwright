---
title: Scripts
kind: kb
checked: 2026-10-08
summary: Read when editing a screenplay or stage play, checking script format, or writing coverage.
---
# Scripts

Source: [scripts, nonfiction and books note](../../../ai-docs/research/2026-10-08-scripts-nonfiction-books.md), section 1.

## editwright vs cinewright
Writing new scripts belongs to cinewright (https://github.com/m4bwav/cinewright, its cinewright-script skill). Link to it; never copy its content.

| Job | Owner |
|---|---|
| Write a new script, break a story into beats, shot cards, line length for AI voices | cinewright-script |
| Read an existing script and write notes or coverage | editwright |
| Proofread format (sluglines, cues, parentheticals, transitions, page count) | editwright |
| Flag an on-the-nose line or a scene with no turn | editwright (suggest only; point to cinewright-script for the scene-turn idea) |
| Rewrite dialogue | neither by default; editwright quotes the line, names the problem, queries the author |

cinewright's AI-voice pacing rules do not apply to scripts for human performers.

## Format checklist (screenplay)
Mechanical, safe to flag every time:
- Page numbers present. `FADE IN:` at the left margin.
- Every slugline has INT/EXT, place and time, on one line.
- Character cues spelled the same throughout; a known major character not labelled MAN or WOMAN.
- Names not in caps inside dialogue (caps for the cue and first introduction only).
- Parentheticals short and rare; long ones are action in disguise.
- Action paragraphs short; big description blocks are a named complaint.
- No `!!!` or `???`. Transitions sparing; camera directions mostly absent in a spec script.
- Page count against target (one page is about one minute for screenplays only). An outlier length is a note, not an error.

Judgement, flag with a reason:
- Overused "we see"; speaking to the reader in action lines.
- Excess wardrobe description; quoting other films.
- Many flashbacks in the first ten pages.
- Characters reduced to looks, age or nationality.

Source: scriptmag.com, "20 Little Things That Make Script Readers Hate Your Screenplay" (2018).

Stage plays (US convention, secondary sources only): name in caps centred above the speech and in caps in directions; directions indented, in parentheses, often italic; act and scene headings centred; directions show action, not thoughts or backstory. Many contests want act-scene-page numbers (unverified as universal). No page-equals-minute rule. Edit a play in the format it arrives in and tell the user to check the theatre's or contest's own rules.

## Fountain essentials (fountain.io/syntax, spec 1.1)
- Scene heading: line starts INT, EXT, EST, INT./EXT, INT/EXT or I/E; force with leading `.`; scene numbers `#1A#`.
- Character: uppercase line, blank line before, none after; extensions `(O.S.)`; force with `@`.
- Parenthetical in `( )`; dual dialogue: `^` after the second cue; lyrics: `~`.
- Transition: uppercase ending `TO:`, blank lines around; force with `>`. Centred: `>THE END<`.
- Emphasis `*italic*`, `**bold**`, `_underline_`; escape with `\`.
- Title page `Key: value` at top; page break `===`; sections `#` and synopses `=` do not print.
- Notes `[[ ]]` and boneyard `/* */` do not print.

editwright writes notes as `[[note: ...]]` and never touches text outside them. Use `/* */` only when the author asks to park cut text.

## Coverage report
1. Header: title, writer, form, genre, pages, setting, period, draft date.
2. Logline: one or two sentences with protagonist, conflict, tone.
3. Synopsis: one to two pages, present tense, neutral.
4. Grid: each category rated (Excellent/Good/Fair/Poor or numbers).
5. Comments, then verdicts for script and writer: Pass, Consider or Recommend. Recommend is rare.

Sources: glcoverage.com (2024); a Duke alumni coverage template.

Rubric, each row citing pages:
- Premise: is the hook clear in the logline, and fresh?
- Structure: page numbers of inciting incident, act breaks, midpoint, climax; does the main conflict start too late?
- Character: does the protagonist want something and change; are minor characters distinct?
- Dialogue: distinct voices; on the nose; written rather than spoken?
- Pacing: where momentum drops; repeated beats?
- Marketability: genre, budget signals, comparables. Mark as opinion.

"Black List style" request: score Premise, Plot, Character, Dialogue, Setting 1 to 10, give Overall separately (not an average), and say it imitates, and is not, a Black List evaluation (secondary source; blcklst.com unreachable).

Common reader complaints: generic voice copying an existing show; dialogue from the writer, not the character; a strong opening that loses momentum and repeats its best beat; main conflict starting late after world-building (creativescreenwriting.com).

Related: [levels.md](levels.md), [deliverables.md](deliverables.md), [line-copy-proof.md](line-copy-proof.md), [ai-text-rules.md](ai-text-rules.md)
