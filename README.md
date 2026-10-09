# editwright

![A typed manuscript page on a wooden desk in warm window light, its margins marked in red pencil with carets, circles and check marks, two sticky tabs on its edge and a red pencil lying beside it](assets/banner.jpg)

An editor for your AI agent that marks the page and never writes on it.

editwright edits writing the way a professional editor does: developmental notes and an editorial letter, manuscript assessment, line editing, copyediting and proofreading, script coverage and nonfiction fact-check flags. It works on short stories, novels, screenplays, essays and books. The author keeps every word:

- **Your file is never modified.** editwright hashes it at intake, works on a copy, and checks the hash again at the end of every run.
- **Suggestions, not rewrites.** You get a letter, notes anchored to quoted passages, and a list of suggestions with IDs (S-001, S-002...). Each one says what is wrong, why it matters and what kinds of fix exist. Where a fix needs new wording, it is a question for you, not a sentence written for you.
- **Every AI-written word is counted.** A provenance ledger counts the words any change would bring in that you did not write. By default fiction allows none and nonfiction allows 1% (at most 50 words). Copying a suggestion's example wording does not make it yours: the ledger still counts it.
- **Only your choices are applied.** Tell it which IDs you accept; it writes `edited.md` beside the cleaned copy, with a changelog tying each change to its ID.

## Why "the author writes every word"

Since 2026-08-14, text written by new Claude models carries a watermark (a version of Google's SynthID), and OpenAI marks ChatGPT text for EU users. The mark sits only in words the model chose: Anthropic says a light proofread of human text leaves "very little (if anything)" for it to attach to. Watermark checkers are open only to regulators and researchers today. The rules that matter more to writers are about who wrote the words. Amazon KDP calls AI editing of your own text "AI-assisted" (no disclosure) but AI-written text "AI-generated". The Authors Guild's Human Authored mark allows only trivial AI text. Clarkesworld, Asimov's, Uncanny, Writers of the Future and the Nebulas refuse AI-written text. The US Copyright Office asks you to disclaim AI-written passages. AI detectors also misfire on plain human prose. Keeping the words yours avoids all of that. Sources and dates: [skills/editwright/kb/ai-text-rules.md](skills/editwright/kb/ai-text-rules.md).

## Install

Claude Code:

```
/plugin marketplace add m4bwav/editwright
/plugin install editwright@editwright
```

GitHub Copilot CLI: `copilot plugin marketplace add m4bwav/editwright`, then `copilot plugin install editwright@editwright`. With `gh` 2.90 or newer: `gh skill install m4bwav/editwright editwright`.

Claude Desktop and claude.ai: download `editwright.zip` from the [latest release](https://github.com/m4bwav/editwright/releases/latest), then Customize > Skills > Upload skill.

It needs Python 3.9 or newer and nothing else. [readwright](https://github.com/m4bwav/readwright) helps with EPUB and PDF manuscripts.

## Use

Ask in your own words: "edit my short story ./story.md", "give me an editorial letter for chapter 3", "proofread this essay", "coverage on my script", then "apply S-003 and S-007". The agent runs the `ew.py` command-line tool for everything that is counting or bookkeeping and keeps the judgment for itself:

| Command | What it does |
|---|---|
| `ew.py intake FILE --genre short-story --level full --author "Name"` | snapshot and hash the source; write `clean.md` (encoding, whitespace, quotes, dashes, paragraph breaks; never a word) and `cleanup-log.md` |
| `ew.py show JOB --para 10-20` | numbered paragraphs, the anchors suggestions use |
| `ew.py stats JOB` | sentence-length spread, close repeats, -ly adverbs, filter and crutch words, dialogue share (counts, not verdicts) |
| `ew.py chunk JOB` | split a long manuscript into chunks of whole paragraphs |
| `ew.py suggest JOB file.json` | validate suggestions (every quote must be found verbatim) and write `suggestions.md`, `review.md` (CriticMarkup) and the ledger |
| `ew.py export JOB` | `review.docx` with tracked changes and comments for Word or Google Docs |
| `ew.py apply JOB --accept S-001,S-004` | apply only those IDs to a new file, refusing unknown IDs, overlaps and AI-written words over the limit |
| `ew.py feedback JOB --accepted ... --rejected ...` | learn which kinds of suggestion this author takes |
| `ew.py check JOB` | confirm the source never changed |
| `ew.py override JOB --reason "..."` | turn human-authored mode off for one job, only when you say so plainly |

## Privacy

editwright makes no network calls and sends your manuscript nowhere beyond the agent you already use. Manuscripts, style sheets, story bibles and your preferences are kept in a works folder on your machine: `~/editwright-works` by default, or the folder named by `EDITWRIGHT_WORKS` or by `works` in `~/.editwright.json`. Point it at a private, backed-up folder. Nothing about your work is written to this repository.

## How it was built

Research notes with sources and dates are in [ai-docs/research/](ai-docs/research/); the editing knowledge the skill reads is in [skills/editwright/kb/](skills/editwright/kb/INDEX.md). The skill is an evergreen unit: it re-checks its research on a schedule and carries the tests that prove it works ([TESTS.md](skills/editwright/TESTS.md)).

Banner image generated locally with Z-Image Turbo in ComfyUI, seed 3581877482, with the typed lines softened afterwards; prompt and workflow in [assets/banner-workflow.api.json](assets/banner-workflow.api.json).

## License

MIT. See [LICENSE](LICENSE).
