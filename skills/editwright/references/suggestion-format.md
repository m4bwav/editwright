# Suggestion format

Read when writing the JSON file for `ew.py suggest`. The script validates every item, saves the valid ones and lists the refused ones by item number. Fix those and run `suggest` again with the same file: items already saved are skipped.

```json
[
  {
    "level": "line",
    "category": "filter-word",
    "para": 12,
    "quote": "She saw the door swing open",
    "change": {"replace": "The door swung open"},
    "problem": "The filter verb puts Mara between the reader and the door.",
    "why": "This is the scare beat; distance blunts it.",
    "options": ["Cut 'She saw' and let the door move on its own.", "Keep it if her noticing late is the point."],
    "severity": 2
  },
  {
    "level": "developmental",
    "category": "stakes",
    "para": 40,
    "quote": "She realized the man was her brother.",
    "problem": "The reveal has no setup, so it reads as coincidence.",
    "why": "Readers accept a surprise they could have seen coming.",
    "options": ["Plant the brother in the opening scene.", "Delay the reveal to the last line."],
    "severity": 3
  }
]
```

## Fields

| Field | Required | Rule |
|---|---|---|
| `level` | yes | `developmental`, `assessment`, `line`, `copy`, `proof` or `fact` |
| `category` | yes | short kebab-case label (`pov-slip`, `pacing`, `stakes`, `dialogue-tag`, `filter-word`, `repetition`, `tense`, `agreement`, `typo`, `punctuation`, `consistency`, `claim-check`, `format`). Reuse labels: the author's preference tallies are kept per category |
| `problem` | yes | what is wrong, in one or two plain sentences |
| `quote` | for anchored items and every change | copied exactly from `clean.md` (as `ew.py show` prints it), short: the smallest span that shows the problem or that the change replaces |
| `para` | recommended | the P number from `ew.py show`; without it the quote must be unique in the text |
| `occurrence` | when the quote repeats in the paragraph | 1-based |
| `why` | recommended | why it matters to the reader or the market |
| `options` | recommended | kinds of fix, described, not drafted |
| `change` | optional | `{"replace": "..."}`; `""` cuts the quote. Smallest span, the author's own words wherever possible |
| `severity` | optional | 1 minor, 2 worth fixing (default), 3 serious |

## What may be a change, and what must be a query

A change is fine when it adds no words the author did not write: a typo or spelling fix, an inflection or tense fix of the author's word, punctuation, a cut, or a reorder. The script counts these as the author's.

Anything else (a new word, a new phrase, a new sentence) is AI-written text. In human-authored mode, write it as a query: name the problem and the kind of fix in `options`, and leave the words to the author. Do not slip example wording into `options` either. When the author's text for a query echoes words that appear in that suggestion's `change` or `options` but not in the quote, `apply` counts those words as AI-written, so a copied suggestion never passes as the author's.

## What the script adds

`id` (S-001, S-002, ...), `span` (character offsets in clean.md), `provenance` (reused, corrected, removed and new words), `ai_words`, `marked_ai_text`, `status`. Do not set them yourself.
