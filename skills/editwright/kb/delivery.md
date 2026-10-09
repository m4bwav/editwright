---
title: Delivery formats
kind: kb
checked: 2026-10-08
summary: Read when choosing or producing output: suggestions.md, CriticMarkup review.md, the provenance ledger, review.docx or Google Docs.
---
# Delivery formats

Source: [delivery formats note](../../../ai-docs/research/2026-10-08-delivery-formats.md).

## Hard rule
Never write to the author's original document. Every output is a copy or a file beside it. Suggestions live beside the text until the author acts (the Word Copilot and Docs Proofread pattern).

## Default outputs (stdlib, no install)
1. `suggestions.md`: the source of truth. One entry per suggestion: id, location (chapter, paragraph, quoted context), original, proposed (if a replacement), reason, category, confidence. The author accepts by id; `ew.py apply` acts only on accepted ids.
2. `review.md`: CriticMarkup copy of the text (fletcher.github.io/MultiMarkdown-6/syntax/critic.html):
   - insertion `{++text++}`, deletion `{--text--}`, substitution `{~~old~>new~~}`
   - comment on a span: `{==span==}{>>reason<<}`
   - readable raw; GitHub and VS Code show braces literally; Obsidian's Commentator plugin gives accept and reject; MultiMarkdown 6 `-a` accepts all, `-r` rejects all.
   - If the text already contains `{++`, `{--`, `{~~`, `{==` or `{>>`, escape or refuse those passages.
3. Provenance ledger: every AI-written word with location, per [ai-text-rules.md](ai-text-rules.md).

Hundreds of suggestions overwhelm writers in any format; formats are views of the list, so cap the list first ([line-copy-proof.md](line-copy-proof.md)).

## Optional: review.docx
- Tracked changes (`w:ins`, `w:del` with `w:delText`) and comments (`word/comments.xml`, anchored by `commentRangeStart`, `commentRangeEnd`, `commentReference`), written with zipfile and string splicing, no third-party packages.
- Tested: pandoc 3.12 (`--track-changes=all`) and LibreOffice read the result as insertion, deletion and anchored comment. Not yet opened in Microsoft Word; test desktop Word and Word for the web before claiming support.
- For a .docx source, write a copy of the author's own file to keep their styles. For a markdown source, pandoc can turn `.insertion`, `.deletion` and `.comment-start/.comment-end` spans into a .docx when installed, but it rebuilds the document.
- Pitfalls: runs split by formatting (match on paragraph text, split runs, copy `w:rPr`); one id counter above existing ids; merge into an existing comments.xml (pandoc output always has one); ElementTree rewrites namespace prefixes, so splice strings; `xml:space="preserve"` on padded text; keep zip order with `[Content_Types].xml` first; v1 covers body paragraphs only; a suggestion crossing a field, hyperlink, footnote or content control falls back to a comment; never touch existing revisions.
- comments.xml alone is enough for flat, unresolved comments; add `commentsExtended.xml` only if Word drops something the author needs.
- python-docx 1.2.0 has comments but no tracked-changes API (reference only).

## Google Docs routes
- Upload and convert (zero credentials): upload review.docx to Drive and let it convert. Google: "Any tracked changes in Microsoft Office become suggestions in Google Docs" (support.google.com/docs/answer/6033474). Comments come across too (untested with editwright output). The result is a new Doc beside the original. The claude.ai Drive connector can do the upload (`create_file`, base64 .docx) but cannot comment or suggest itself.
- Docs API (new, not used by editwright yet): since 2026-09-30 GA, `batchUpdate` with `writeControl.writeMode: SUGGEST` writes suggestions and `InsertCommentRequest` with a `range` anchors comments (developers.google.com/workspace/docs/release-notes). Needs OAuth. A replace is DeleteContentRange plus InsertText; apply from the end backwards. This route writes into an existing Doc; under the hard rule, use it only on a copy. Recheck release notes before building.
- Drive API comments do not anchor in Docs; do not use them.

Related: [ai-text-rules.md](ai-text-rules.md), [line-copy-proof.md](line-copy-proof.md), [deliverables.md](deliverables.md), [scripts.md](scripts.md)
