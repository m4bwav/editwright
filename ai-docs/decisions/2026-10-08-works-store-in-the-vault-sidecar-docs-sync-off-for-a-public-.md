---
title: Works store in the vault sidecar, docs sync off for a public repo
kind: decision
status: active
date: 2026-10-08
verified: 2026-10-08
stale_after: 2027-04-06
tags: [privacy, everlast]
summary: read before moving where manuscripts and author notes live
---

# Works store in the vault sidecar, docs sync off for a public repo

## Context
Manuscripts, style sheets, story bibles, accepted and rejected suggestions and author preferences must never reach the public repository. The kickoff offered the everlast vault's private sidecar or a gitignored `works/` folder junctioned from the vault.

## Decision
- `ew.py` keeps all of that in a works store outside the repository, found in this order: `--works`, `$EDITWRIGHT_WORKS`, `works` in a `.editwright.json` in the current folder, `works` in `~/.editwright.json`, then `~/editwright-works`. Each work is a folder (`work.json`, `style-sheet.md`, `story-bible.md`, `jobs/<date>-<n>-<level>/`); each author has `authors/<slug>.json` (tallies) and `<slug>.md` (taste notes).
- On the maintainer's machine `~/.editwright.json` points at the everlast vault's private sidecar for this project (`works/` inside it). The vault is a private git repository, so manuscripts are backed up and never public.
- The repository is registered with everlast in mode `repo` with `--sync off`. `works/`, `editwright-works/` and `.editwright.json` are gitignored as a second guard.

## Reasons
- The sidecar is what everlast recommends for anything private, and it already syncs to a private remote; a junction into the repository would add a path that one wrong `git add -f` could publish.
- Sync `pr` and `push` were rejected because everlast's docs-sync puts the machine's hostname in branch names and pull request text (cinewright HANDOFF, 2026-10-07), which leaks on a public repository.

## Consequences
Docs are committed by hand with the work. Large books grow the vault's git history; if that becomes a problem, keep `source.*` snapshots out of the vault and record only their hashes.

Related: see also [2026-10-08-human-authored-defaults-and-how-ai-written-words-are-counted.md](2026-10-08-human-authored-defaults-and-how-ai-written-words-are-counted.md)
