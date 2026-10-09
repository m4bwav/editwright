# AGENTS.md

Rules for any AI agent (Claude Code, Copilot, Cursor, Codex, Gemini CLI) working in this repository. `CLAUDE.md` imports this file and `.github/copilot-instructions.md` points here.

## What this is

editwright: a cross-agent plugin with one skill, `skills/editwright/`, that edits writing like a professional editor while the author writes every word. SKILL.md holds the rules and the passes; `kb/` holds the editing knowledge in small files read on demand (start at `kb/INDEX.md`); `references/suggestion-format.md` is the JSON the CLI takes; `scripts/ew.py` is the single standard-library CLI (intake and hashing, word-safe cleanup, counts, chunks, suggestions, provenance ledger, apply, review.docx export, author preferences). Evergreen companions sit beside SKILL.md (RESEARCH, CHANGELOG, LEARNINGS, TESTS, MAINTENANCE, `evergreen.json`, `evals/evals.json`). Unit tests are in `tests/`; runnable eval cases in the root `evals/` (`claude plugin eval` format); research notes, decisions, the log and the handoff under `ai-docs/` (start with `ai-docs/HANDOFF.md`).

## Rules

- The product promise is the rule set in SKILL.md: the source is read-only, suggestions not rewrites, every AI-written word counted, only accepted IDs applied, override only on the user's plain words. A change that weakens any of them needs a decision entry in `ai-docs/decisions/` and a test.
- `ew.py` stays one standard-library Python file (3.9 or newer) that runs on Windows, macOS and Linux, reads and writes UTF-8 with LF line endings, and never writes to the source file. Cleanup must never change a word (`check_words_same` guards it). Every change to the script gets a test in `tests/test_ew.py`; run `python tests/test_ew.py` before committing.
- Fixtures are invented text written at test time. Never commit a real manuscript, a real author's text, a style sheet or story bible of a real work, or author preferences. Those live in the private works store (see README, Privacy), never in this repository, an issue, a log or a test.
- Size budget: `python scripts/budget.py` (red fails CI; tell the maintainer about a yellow in one line). Keep SKILL.md under 200 lines and each kb file under 6,000 bytes.
- The skill is an evergreen unit. Before editing it read `skills/editwright/evergreen.json`; if `next_due` has passed or `contradiction` is set, say so and refresh after the task. Every change is logged in `skills/editwright/CHANGELOG.md` with its reason; lessons go to `LEARNINGS.md` with a code name, and are cited by that name, not a bare ID. Re-run the eval suite after SKILL.md changes.
- Research beats recall: policy, watermark and tool facts carry an `R-` entry in RESEARCH.md and a date; kb files carry `checked:`.
- A release bumps the version in `.claude-plugin/plugin.json`, `plugin.json`, `VERSION` in `ew.py`, `metadata.version` in SKILL.md and `version` in `evergreen.json` together, then tags `vX.Y.Z` and publishes a GitHub Release with the CHANGELOG entry as notes.
- No top-level `bin/` folder (Cowork refuses plugins that have one).
- Prose people read (README, SKILL.md, kb, letters the skill writes) is checked with the everwrite checker when available: `python <everwrite>/skills/everwrite/scripts/tells.py <files>`, zero strong findings. Never run it, or any humanizer, on an author's manuscript.
- Neighbours: readwright reads EPUB, PDF and DOCX manuscripts; cinewright owns screenplay writing (link to it, never copy); everwrite checks editwright's own prose.
- This is a public repository. Nothing in it names a person other than the author credit and published authors and organisations, a machine, an absolute local path, a private project or a credential. Plain short sentences, no em dashes, relative markdown links, never wikilinks.
- No AI attribution anywhere: no Co-Authored-By trailers, no "generated with" lines in commits, pull requests, releases or files.
- After the first push, changes go through pull requests assigned to the maintainer with the `needs-review` label; a docs-only pull request may be merged once its checks pass.

## Commands

- Tests: `python tests/test_ew.py`
- Budget: `python scripts/budget.py`
- Plugin manifest: `claude plugin validate .`
- Evals (Claude Code 2.1.281+): `claude plugin eval . --no-publish --trust-plugin --case "trigger-*"`; cases that need Bash run under WSL2 or Linux (see `ai-docs/`)

## everlast (session knowledge, load on demand)

- `ai-docs/INDEX.md` lists what past sessions learned here (solutions with verified commands, decisions with reasons, plans). At the start of a task, scan it and open only the entries whose title or tags match; no line matches: `everlast.py search "<key terms>"` before concluding nothing was recorded. Read `ai-docs/HANDOFF.md` when continuing unfinished work (everlast-resume skill).
- Before acting on an entry marked `(recheck due)`, run `everlast.py recheck <entry>`, re-run its Verified-by command only when that is read-only or safe (a build, a test, a version query), then record `everlast.py verify <entry>` or `verify <entry> --failed "what broke"`; a fix that changed is superseded, never reused blindly.
- Before finishing a task that hit a dead end, verified a non-obvious command, made a design choice, or taught you something about the user, record it (everlast-capture skill, or `everlast.py note` / `handoff`); rewrite `HANDOFF.md` when work is left unfinished. Say "nothing to record" when that is true.
- Anything naming a person, an internal host or name, a credential, or an opinion about people goes to the private sidecar (`--private`), never here. Lessons about the user or this machine go to the user tier (`--user`).
- Rules go in this file, system layout in CODEMAP.md; the doc set holds only what could not be re-derived from the code in a minute.
- Link documents together with relative markdown links: every markdown folder is reachable from an index whose lines say when to read each file (`ai-docs/INDEX.md` is generated from frontmatter; give entries a one-line `summary`), and an entry links the entries it relates to on a typed `Related:` line (`supersedes`, `contradicts`, `builds on`, `see also`). The set then reads as a graph for people in Obsidian and for agents alike. No wikilinks in the repo.
