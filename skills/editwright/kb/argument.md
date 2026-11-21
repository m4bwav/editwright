---
title: Argument order and skim tests
kind: kb
checked: 2026-11-21
summary: Read during a developmental or structural pass on persuasive nonfiction (essays, op-eds, briefs, proposals, memos): how many reasons, which first, where objections and concessions sit, the close, paragraph links and the first-sentence skim.
---
# Argument order and skim tests

Each item is a flag and a question for the author, never a rewrite. Book rules from advocacy and plain-writing manuals, unverified against readers: Scalia and Garner, *Making Your Case* (2008), cited by section; Garner, *Legal Writing in Plain English*, 3rd ed. (2023), cited by section; Zinsser, *On Writing Well*, cited by chapter. Claims and warrants: [nonfiction.md](nonfiction.md). Maps and containers: [structure.md](structure.md).

## Order of the case
- `scattershot`: more than three independent reasons. Ask which two or three carry the case; a long list reads as under-analysed and the weak reasons tax the strong (Making Your Case, sec. 12).
- `buried-lead-argument`: the reason the author's own summary calls decisive comes last. Strongest first, unless logic forces an order (a threshold question goes first) (sec. 7).
- Objections in the middle. A piece arguing first gives its positive case, then answers the strongest objection, then closes. A reply clears the opponent's strongest point first. Flag `buried-objection` when the rebuttal opens the piece defensively or is the last thing read, and `missing-objection` when an obvious one is never met (sec. 8, 9; Legal Writing sec. 30).
- `missing-concession`: the piece's own facts raise a weakness it never admits. Suggest stating it early and saying why it does not decide the matter (sec. 11).
- `ad-hominem-tone`: attacks on motive (dishonest, disingenuous, bad faith, lying). Query showing the facts and letting the reader judge (sec. 19).
- Label drift. Note in the style sheet the names the author gives events and parties; flag a switch, since a chosen label persuades only if it holds (sec. 20).
- `weak-close`: "for all the foregoing reasons" and its kin. The close recalls the main reasons and says what the reader should do (sec. 21). Stop when done: an ending that replays the body in short is `summary-ending` (On Writing Well, ch. 9).
- In a factual narrative, consecutive paragraphs that each open with a different source's name read source by source: `source-by-source`; ask for time order.

## Paragraph links
`EW stats` prints `bridged openers: N of M`: openers that link back by a pointing word (this, that, these, those, such), a connective (but, also, so, for example, as a result...) or an echo of a content word from the last two sentences before. Garner's floor is about a third (Legal Writing, sec. 25). Under it is a place to read, not a finding: lists, letters and reference notes score low by design. For a listed paragraph that needs a link, query `no-bridge` and name the kind of link, never the words.

## First-sentence skim
`EW show <job> --firsts` prints only the first sentence of each paragraph. Read them in a row: they should tell most of the story (Legal Writing, sec. 24). Flag `citation-opener` when a paragraph opens on a case name or source instead of its point; query putting the point first. Also check the last sentence of each paragraph: it should lead into the next, not trail off on a date, citation or qualifier (On Writing Well, ch. 9).

## Bracketed cuts
For clutter, mark removable words with a `bracket` item (see [../references/suggestion-format.md](../references/suggestion-format.md)) so the author reads the sentence without them and decides (On Writing Well, ch. 3). For a long, padded paragraph, one query may say it could lose about a quarter of its words, with the candidates as bracket items (Legal Writing, sec. 5). Zinsser's view that many drafts lose half their words is a prompt, never a target.

Related: [nonfiction.md](nonfiction.md), [structure.md](structure.md), [clarity.md](clarity.md)
