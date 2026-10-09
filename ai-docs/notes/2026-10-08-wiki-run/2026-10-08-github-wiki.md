---
title: GitHub wiki written and published for 0.1.0
kind: note
date: 2026-10-08
verified: 2026-10-08
stale_after: 2027-04-08
tags: [wiki, docs, 0.1.0, github]
summary: "the wiki's pages, where their git working copy is, how every example was verified against the v0.1.0 release, the facts found on the way, the inaccuracies in the shipped docs, and how to update the wiki; read before touching the wiki or the README sentences listed under inaccuracies"
---

# GitHub wiki for 0.1.0

## Summary

Wrote and published https://github.com/m4bwav/editwright/wiki with the wikiwright skill (0.9.1): ten pages plus sidebar and footer, written from the README, AGENTS.md, SKILL.md, the kb, the suggestion format, `ew.py` and its `-h` output, the tests and the evals. Every command example was run against the `v0.1.0` tag's `ew.py` with an invented story and essay. Wiki commit `3dbb6ed`. `live`: 10 pages, 0 failures; everwrite `tells.py`: 0 strong.

Pages: Home, Getting-Started, How-It-Works, Commands, Suggestion-Format, Provenance-and-AI-Text-Rules, Delivery-Formats, Works-Store-and-Privacy, FAQ, Development, _Sidebar, _Footer.

## Where the pages are

A sibling clone of this repository named `editwright.wiki`, branch `master`, remote `https://github.com/m4bwav/editwright.wiki.git`. Plain markdown links between pages, LF line endings.

## How it was published

Preflight: `placeholder` (the maintainer had saved the first page). Pages committed over the placeholder and pushed with a plain fast-forward. `wikiwright.py live m4bwav/editwright <wiki dir>`: 10 pages 200 (Home 301), sidebar and footer render, 22 anchor links to 6 pages, 0 broken.

## Updating the wiki later

1. `git -C <wiki dir> pull --ff-only`, then edit the pages.
2. Re-verify: check out the new tag in a scratch folder, then on Linux or WSL run `python3 2026-10-08-wiki-verify.py <checkout>/skills/editwright/scripts/ew.py <checkout>` (it rebuilds `/tmp/demo` from scratch and sets `HOME` inside it, so no real works store is read). Mask the checkout path as `<checkout>`, then `wikiwright.py diffout 2026-10-08-wiki-verify.out.txt <new output>`. The job folders carry the run date (`20261008-1-full`), so every page that shows one changes with the date: either rerun on a new date and update those lines, or keep the old date by editing nothing that shows it.
3. `wikiwright.py outputs <wiki dir> <new output> --address ''`, `wikiwright.py snippets <wiki dir> 2026-10-08-wiki-verify.py`, `wikiwright.py check <wiki dir> --version <new>`, and the everwrite checker.
4. Commit, push, `wikiwright.py live m4bwav/editwright <wiki dir>`. Pages that name the version: Home ("About these pages", "Links"), Getting-Started (gh skill tag, zip contents), Commands (intro), Development (checkout lines, release-notes numbers), Provenance-and-AI-Text-Rules (kb checked date), Delivery-Formats (kb checked date), Works-Store-and-Privacy (`works_root` in 0.1.0, the PDF leftover), FAQ (two "in 0.1.0" answers), _Footer.

## How the examples were verified

`2026-10-08-wiki-verify.py` holds every command the pages show as text, runs each with bash in `/tmp/demo` against the release's `ew.py`, and prints `$ command`, the merged output and `$ echo $?`. Saved output: `2026-10-08-wiki-verify.out.txt` (57 cases, the last three in the repository checkout: tests, budget and zip build). Ran on Ubuntu under WSL, Python 3.14.4; a smoke run (intake, check, status) on Windows with Python 3.14.6. `outputs`: 71 outputs checked, 0 missing, 5 skipped (commands typed into agents, the usage synopsis, a unittest timing). `snippets`: no code blocks of a checked language (the pages use console transcripts), 6 commands. Tests: 26 passed on Windows (3.14.6) and Linux (3.14.4). `claude plugin validate .` passed. `gh skill install m4bwav/editwright editwright --dir <scratch>` installed the skill from `refs/tags/v0.1.0`. The release zip lists 21 files.

Not tested: the Claude Code and Copilot plugin installs, the claude.ai upload, Python 3.9, macOS, opening review.docx in Word, LibreOffice or Google Docs, the 50-word nonfiction cap (needs over 5,000 words), long manuscripts, the evals.

## Facts verified while writing (not in the README)

- The works store lookup also takes `--works`, a `.editwright.json` in the current folder (relative paths from that folder) and `EDITWRIGHT_CONFIG`.
- The work slug comes from the file name, not `--title`; use `--work`.
- Each `apply` builds a fresh file from `clean.md` (`edited.md`, `edited-2.md`...); earlier applied IDs are not carried over. `status` and `job.json`'s `applied` describe the newest file; `status` lists only `edited.md`.
- `review.md` and `review.docx` drop the later of two overlapping changes.
- `stats` leaves out headings and scene breaks (130 words where intake counts 133).
- `job.json` stores the source's absolute path; the store holds full read-only copies of each manuscript. `check` writes `last-check.txt` at the store root.
- On Windows the read-only snapshot makes Python's `shutil.rmtree` fail with "Access is denied"; `rm -rf` in Git Bash works.
- Exit codes: `apply` without `--accept` and `override` with a reason under three words exit 2.

## Inaccuracies found in the shipped docs and behaviour

1. README "Every AI-written word is counted ... Copying a suggestion's example wording does not make it yours: the ledger still counts it." The echo check skips stop words: retyping S-004's "the way mules will" counted 1 AI word where the proposal counted 3 (`apply-echo` case). Fiction still refuses it; the nonfiction allowance can undercount.
2. The apply changelog's "Words" column labels the author's own `--author-text` words "AI-written: ..." while the last column says "author" (`changelog-md` case). Display only; totals are right.
3. A refused intake (PDF without `--text`) leaves `works/<work>/jobs/<date>-1-full/source.pdf` with no `job.json` (`store` case): `intake` copies the snapshot before reading the text.
4. README "Privacy" names `EDITWRIGHT_WORKS`, `~/.editwright.json` and the default only; the code also reads `--works`, `./.editwright.json` (checked before the user file) and `EDITWRIGHT_CONFIG`.
5. `skills/editwright/TESTS.md` in the v0.1.0 tag and release zip still shows the scaffold entry ("not yet run · 0/0") while the release notes report 9/9; the working tree has an uncommitted update.
6. `kb/delivery.md` calls `suggestions.md` "the source of truth"; in the code `suggestions.json` is, and `suggestions.md` is rebuilt from it.

## Gotchas

- `wikiwright.py outputs` reads a block after "The config file is JSON:" as output; phrase input lead-ins without a colon.
- The Write tool stripped trailing spaces from the story text, so the "trailing spaces removed" rule does not show in the cleanup log example.

Related: see also [../HANDOFF.md](../HANDOFF.md), [../log.md](../log.md).
