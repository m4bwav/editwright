---
title: AI text rules
kind: kb
checked: 2026-10-08
summary: Read before any replacement, and when an author asks about watermarks, detectors, disclosure or copyright; holds the AI-word thresholds and how ew.py counts.
---
# AI text rules

Source: [AI text provenance note](../../../ai-docs/research/2026-10-08-ai-text-provenance.md).

## What to tell the author (short and accurate)
- Claude now watermarks its text. Anthropic announced it on 2026-08-14: a version of Google DeepMind's SynthID-Text approach, carried in word choices, with no hidden characters and no user identity (anthropic.com/news/claude-text-watermark). It covers current models including Opus 5.5 and Sonnet 5.5 (support.claude.com article 16266773).
- The mark attaches only to words Claude chooses. Anthropic: when Claude proofreads a person's text, "there's very little (if anything) for the watermark to attach to". Words the author types carry none.
- SynthID is Google's (Gemini). Google says it survives light edits and weakens after thorough rewriting or translation (ai.google.dev/responsible/docs/safeguards/synthid).
- OpenAI announced textGrain on 2026-10-05: ChatGPT and Codex text for EU users; opt-in in the API. OpenAI says it cannot identify users or prove human authorship (community.openai.com repost).
- Text checkers for these marks go to regulators, researchers and similar bodies, not publishers or readers. Claude's public checker does not check text (claude.com/check-files).
- EU AI Act Art. 50(2) exempts systems performing "an assistive function for standard editing" or that do not substantially alter the input; applies from 2026-08-02 (artificialintelligenceact.eu/article/50).
- Style detectors are a different, bigger risk. They guess from style and misfire on human prose: seven detectors averaged 61% false positives on non-native English essays (arxiv.org/abs/2304.02819). Substack lets readers scan posts with Pangram since July 2026. No tool can promise a clean score.
- Amazon KDP: AI edits, refines or error-checks your own text = "AI-assisted", no disclosure needed; text an AI created = "AI-generated" even after heavy edits, must be disclosed (kdp.amazon.com help G200672390).
- Authors Guild Human Authored: only a "de minimis" amount of AI-generated or AI-modified text, for example grammar-checker fixes; no number published (authorsguild.org/human-authored/faq).
- Strict markets: Clarkesworld, Asimov's, Uncanny, Writers of the Future and the Nebulas reject AI-written text and some reject AI "assistance" of any kind ([short-story.md](short-story.md)).
- US Copyright Office: AI assistance does not bar copyright; AI-generated material that is "more than de minimis" must be disclaimed (copyright.gov/ai). It has sent letters to authors whose books it suspected; answering "solely for proofreading" got them registered (authormedia.com, unverified).
- So editwright points at problems; the author writes the words.

## Default thresholds (AI-written words that may enter the text)
| Kind | Default |
|---|---|
| Fiction, short story, novel, poetry, scripts | 0 |
| Nonfiction | 1% of the piece, capped at 50 words per job |

The author may lower a threshold. Raising it is the author's explicit choice, logged in the ledger.

## How ew.py counts
Counted as the author's:
- words reused from the author's own text, including reorders
- cuts (deleting the author's words adds none)
- punctuation changes
- spelling and inflection corrections of a word the author wrote (tense slip, typo)
- words the author types via `--author-text`

Everything else that enters the text from a suggestion is AI-written and goes in the provenance ledger with its location. A span once AI-written stays AI-written even if the author later accepts or nudges it (Grammarly's laundering bug is the warning: [tools survey](../../../ai-docs/research/2026-10-08-tools-survey.md)).

## Why these numbers
- No publisher, platform, guild or office publishes a figure. "De minimis" is undefined. The numbers are editwright's choice.
- 0 for creative work: strict magazines and contests allow none, and the Human Authored allowance is undefined, so 0 is the only safe default.
- Small allowance for nonfiction: KDP treats editing and error-checking as assisted; the Copyright Office needs a disclaimer only above de minimis; the Human Authored rule names grammar checkers and indexes.
- The ledger lets the author answer a Copyright Office letter, a contract warranty or a detector dispute with evidence. Publish how it counts; vague percentages invite distrust.

Related: [delivery.md](delivery.md), [short-story.md](short-story.md), [line-copy-proof.md](line-copy-proof.md), [levels.md](levels.md)
