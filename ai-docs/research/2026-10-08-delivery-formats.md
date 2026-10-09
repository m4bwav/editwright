---
title: Delivery formats for editwright suggestions
date: 2026-10-08
kind: note
summary: Read this when choosing or building how editwright hands suggestions to a writer (markdown, CriticMarkup, Word tracked changes, Google Docs suggestions).
tags: [research, docx, google-docs, formats]
---

# Delivery formats for editwright suggestions

Read this when you choose or build an output format for editwright's suggestions.
It covers Word tracked changes and comments, Google Docs, CriticMarkup and pandoc.
All facts were checked on 2026-10-08 against the URLs given.
Lines marked "Tested" were run on this PC (Windows 11, Python 3.14, pandoc 3.12, LibreOffice).

## Headline findings

1. A stdlib-only Python script (zipfile plus string or ElementTree edits) can write tracked changes and comments into a copy of a .docx. Tested: pandoc and LibreOffice both read the result as an insertion, a deletion and an anchored comment. Not yet opened in Microsoft Word.
2. Google changed the picture on 2026-09-30. The Docs API now writes suggestions (`writeControl.writeMode: SUGGEST`) and anchored comments (`InsertCommentRequest` with a `range`). This is generally available. Older advice that "suggestions are read-only" is stale.
3. The Claude.ai Google Drive connector cannot comment or suggest. It can upload a .docx and convert it to a Google Doc, and Google converts Word tracked changes into suggestions.
4. pandoc 3.12 writes real `w:ins`, `w:del` and comments into .docx from markdown spans. Tested.
5. python-docx 1.2.0 (2025-06-16) adds comments. It still has no tracked-changes API.

## 1. Word tracked changes and comments (OOXML)

### Structure

- Insertion: `<w:ins w:id=".." w:author=".." w:date="..">` wrapping one or more `<w:r>` runs with normal `<w:t>` text.
- Deletion: `<w:del ...>` wrapping runs whose text is in `<w:delText>`, not `<w:t>`.
  Source: Anthropic docx skill, https://raw.githubusercontent.com/anthropics/skills/main/skills/docx/SKILL.md (read 2026-10-08).
- `w:date` is ISO 8601 UTC. `w:author` is a free string. Word shows it as the reviewer name.
- Comment body lives in `word/comments.xml` as `<w:comment w:id w:author w:date w:initials>` holding normal paragraphs.
- The anchor lives in `document.xml`: `<w:commentRangeStart w:id="N"/>`, the anchored runs, `<w:commentRangeEnd w:id="N"/>`, then a run holding `<w:commentReference w:id="N"/>`.
  Source: pandoc docx writer source, https://github.com/jgm/pandoc/blob/main/src/Text/Pandoc/Writers/Docx/OpenXML.hs (read 2026-10-08).
- Package wiring for comments.xml (Tested, copied from pandoc 3.12 output):
  - `[Content_Types].xml`: `<Override PartName="/word/comments.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>`
  - `word/_rels/document.xml.rels`: a Relationship with `Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"` and `Target="comments.xml"`.
- Modern Word adds three optional parts:
  - `commentsExtended.xml` (`w15:commentEx`): resolved flag (`done="1"`) and reply threading (`paraIdParent`), keyed to the `w14:paraId` of the comment's last paragraph.
  - `commentsIds.xml` (`w16cid`): maps paraId to a `durableId`.
  - `commentsExtensible.xml` (`w16cex`): Office 2021+ extras such as `durableId` and UTC dates.
  Sources: python-docx comments analysis, https://python-docx.readthedocs.io/en/latest/dev/analysis/features/comments.html (read 2026-10-08); Open XML SDK CommentExtensible.DurableId, https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.office2021.word.commentsext.commentextensible.durableid?view=openxml-3.0.1 (2026-10-08).
- For flat, unresolved, unthreaded comments, `comments.xml` alone is enough. python-docx 1.2.0 writes only that part and its docs say commentsExtended and commentsIds are "not supported by the initial implementation". Source: same python-docx analysis page (2026-10-08).
- The Anthropic docx skill's helper generates "six linked XML files (comments.xml, commentsExtended.xml, etc.)" when it wants full modern fidelity. Source: anthropics/skills docx SKILL.md (2026-10-08).

### Minimal working example (Tested)

Inside one `<w:p>` of `word/document.xml`. "The quick fox jumped over." becomes "The slow fox jumped over." with a comment on "jumped".

```xml
<w:r><w:t xml:space="preserve">The </w:t></w:r>
<w:del w:id="101" w:author="editwright" w:date="2026-10-08T00:00:00Z">
  <w:r><w:delText>quick</w:delText></w:r>
</w:del>
<w:ins w:id="102" w:author="editwright" w:date="2026-10-08T00:00:00Z">
  <w:r><w:t>slow</w:t></w:r>
</w:ins>
<w:r><w:t xml:space="preserve"> fox </w:t></w:r>
<w:commentRangeStart w:id="0"/>
<w:r><w:t>jumped</w:t></w:r>
<w:commentRangeEnd w:id="0"/>
<w:r><w:commentReference w:id="0"/></w:r>
<w:r><w:t xml:space="preserve"> over.</w:t></w:r>
```

`word/comments.xml`:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:comment w:id="0" w:author="editwright" w:date="2026-10-08T00:00:00Z" w:initials="EW">
    <w:p><w:r><w:t>Tense check.</w:t></w:r></w:p>
  </w:comment>
</w:comments>
```

Test method (2026-10-08): a 30-line stdlib script copied every zip entry of a pandoc-made .docx, replaced the paragraph, wrote comments.xml, and added the content type and relationship only when missing.
`pandoc out.docx --track-changes=all -t markdown` returned `[quick]{.deletion ...}[slow]{.insertion ...} fox [Tense check.]{.comment-start ...}jumped[]{.comment-end ...} over.`
LibreOffice headless conversion to .odt kept `text:changed-region` and `office:annotation` entries with author editwright.
Still to do: open the file in desktop Word and Word for the web and confirm no repair prompt.

### Can stdlib-only Python do it?

Yes, for edits inside existing paragraphs. zipfile and xml.etree.ElementTree (or careful string work) are enough. Nothing in the format needs lxml.
The real work is text location, not packaging. See pitfalls.

### Pitfalls

- Runs split across formatting. A phrase like "quick brown" may sit in several `<w:r>` elements because of spell-check marks, rsids, bookmarks or partial bold. Match on the paragraph's concatenated text, then split runs at the match boundaries and copy each run's `<w:rPr>` onto the new pieces. The Anthropic skill ships `merge_runs.py` to coalesce fragmented runs first. Source: anthropics/skills docx SKILL.md (2026-10-08).
- Inside `<w:rPr>`, element order is schema-enforced. A `<w:del/>` marker for a deleted paragraph mark must come before the other rPr children. Source: same.
- Deleting a whole paragraph means a `<w:del>` around every run plus a deleted paragraph mark, which means "merge with the next paragraph". Source: same.
- `w:id` values. pandoc gives the first `w:ins` and `w:del` the same id 1 (Tested). Use one counter across all ins, del and comment ids, starting above any id already in the file, to be safe.
- Existing parts. pandoc output always contains a `word/comments.xml`, even with no comments. Tested: blindly adding a second one makes a zip with a duplicate name. Merge into an existing comments.xml and keep its next free id.
- ElementTree rewrites namespace prefixes (ns0:, ns1:) and drops unused declarations. Word relies on `mc:Ignorable="w14 w15 wp14"` naming prefixes that must stay declared, or it reports the file as corrupt. Either register every namespace in the root with `ET.register_namespace` before parsing, or splice text and never reserialize the whole document. String splicing on a parsed index is the safer stdlib route.
- rsids (`w:rsidR` and friends) are optional. Leave existing ones alone and do not invent new ones.
- `w14:paraId` values are needed only if you write commentsExtended. They are 8 hex digits below 0x80000000 and must be unique in the document.
- Fields, hyperlinks, footnote references, smart tags and `w:sdt` content controls nest runs one level deeper. Skip suggestions that cross them in v1.
- Text in tables, headers, footers, footnotes and comments lives in other parts or deeper trees. Scope v1 to body paragraphs and say so.
- Keep the zip entry order and keep `[Content_Types].xml` first. Copy each `ZipInfo` to keep names and compression.
- `xml:space="preserve"` is needed on any `w:t` or `w:delText` with leading or trailing spaces.

### Existing libraries (for reference, not dependencies)

| Library | What it does | Notes | Source (read 2026-10-08) |
|---|---|---|---|
| python-docx 1.2.0 | Comments via `document.add_comment(runs, text, author, initials)` | No tracked changes. Released 2025-06-16. Needs lxml. | https://python-docx.readthedocs.io/en/latest/user/comments.html, https://pypi.org/pypi/python-docx/json |
| docx-editor | Tracked changes and comments, accept and reject, word-level diff of rewritten paragraphs | MIT. Core depends only on defusedxml. | https://github.com/pablospe/docx-editor/ |
| Python-Redlines | Compares two .docx files into a redline | MIT. Calls a bundled .NET binary (Docxodus DocxDiff engine). 1.0.0 removed WmlComparer. | https://github.com/JSv4/Python-Redlines |
| jubarte-redlines, paper-docx | Redline from two documents, accept and reject | Found by search, not reviewed. | https://libraries.io/pypi/jubarte-redlines, https://libraries.io/pypi/paper-docx |
| Aspose.Words, docx4j | Full revision models | Commercial (.NET, Java, Python) and Java respectively. Not stdlib. | vendor sites |
| Anthropic docx skill | Unzip, edit document.xml by hand, rezip, validate with `scripts/validate.py --original --author`; comment.py builds the comment parts | Good reference for rules and validation ideas. | https://raw.githubusercontent.com/anthropics/skills/main/skills/docx/SKILL.md |

A second route worth noting: generate the redline with a diff between the original and an "accepted" copy (the Python-Redlines idea). editwright already has exact suggestions, so direct insertion is simpler and more faithful.

## 2. Google Docs

### Docs API (current)

- 2026-09-30, generally available: "Full comment and suggestion management". Read comment threads, create comments and replies with `InsertCommentRequest` and `AddCommentReplyRequest`, and "write edits as suggestions" by "setting `writeControl.writeMode` to `SUGGEST`". Developer preview began 2026-07-07. Source: https://developers.google.com/workspace/docs/release-notes (read 2026-10-08).
- `WriteControl.writeMode` values: `EDIT`, `SUGGEST` ("Apply all updates as suggestions"), unspecified means EDIT. Source: https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/batchUpdate (last updated 2026-09-30).
- `InsertCommentRequest` fields: `content` (plain text, at most 2048 UTF-8 code units), optional `assigneeEmailAddress`, and `range`, "the Range in the document that is tied to this comment". So comments anchor to text. Source: https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/request (read 2026-10-08).
- Suggest mode rejects AddDocumentTab, CreateNamedRange, DeleteFooter, DeleteHeader, DeleteNamedRange, DeleteTab, UpdateDocumentTabProperties and UpdateTableColumnProperties. Format and header or footer settings cannot be suggested. Source: https://developers.google.com/workspace/docs/api/how-tos/suggestions (last updated 2026-09-30).
- 2026-10-01, developer preview: Google's Docs MCP server can read comments (`commentsIncluded`) and create and reply to comments through its `update_doc` tool. Source: release notes above.
- Implication: a text replace in a Google Doc is a `DeleteContentRange` plus `InsertText` at document indexes inside one SUGGEST batch. Apply edits from the end of the document backwards so earlier indexes stay valid.
- This needs OAuth and the Docs API, so it is not stdlib-and-zero-setup. It is an optional route for users who have Google credentials or the Google Docs MCP server.

### Drive API comments (old route)

- Drive `comments.create` takes an `anchor`, but "Google Workspace editor apps (such as Docs, Sheets, and Slides) don't render comments created with the Drive API anchored to content; they treat these comments as unanchored comments." The page now says to use the Docs API instead. Source: https://developers.google.com/workspace/drive/api/guides/manage-comments (last updated 2026-09-10).

### Claude.ai Google Drive connector

Observed from the connector's tool schemas in this session on 2026-10-08:
- Tools: search_files, read_file_content, download_file_content, get_file_metadata, get_file_permissions, list_recent_files, create_file, copy_file, update_file, share_file, trash_file.
- `create_file` uploads text or base64 content and converts supported types to Google types by default (`disableConversionToGoogleType` turns that off).
- `update_file` changes only title and parent folder. It cannot change content.
- No tool creates comments or suggestions.
So from claude.ai the route is: build the .docx, upload it with `create_file` (contentMimeType `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, base64), and let Drive convert it.

### Word import turns tracked changes into suggestions

- "Any tracked changes in Microsoft Office become suggestions in Google Docs editors. Any suggestions in Google Docs editors become tracked changes in Microsoft Office." Source: https://support.google.com/docs/answer/6033474 (read 2026-10-08).
- Word comments also come across as Google Docs comments on conversion (long-standing; BetterCloud guide, https://www.bettercloud.com/monitor/the-academy/import-tracked-changes-from-microsoft-word-into-google-docs/, read 2026-10-08). Not yet tested with an editwright file.
- Suggestions made on import keep the Word author name as text, not a Google account. Untested; check on first real run.
- The result is a new Google Doc next to the writer's original. It cannot add suggestions to the writer's existing Doc. Only the Docs API SUGGEST route can do that.

## 3. Markdown

### CriticMarkup

Syntax, per MultiMarkdown 6 docs (https://fletcher.github.io/MultiMarkdown-6/syntax/critic.html, read 2026-10-08):
- Insertion `{++text++}`
- Deletion `{--text--}`
- Substitution `{~~old~>new~~}`
- Highlight `{==text==}`
- Comment `{>>comment<<}`

A comment on a passage is usually written as a highlight followed by a comment: `{==jumped==}{>>Tense check.<<}`.

Tool support:
- MultiMarkdown 6: renders markup as highlights by default; `-a` accepts all changes, `-r` rejects all. Comments and highlights are dropped under accept or reject. Source: MMD6 page above.
- Obsidian: the Commentator plugin (Fevol/obsidian-criticmarkup) gives a Word-like suggestion mode, accept and reject, a comment gutter and a vault-wide view. Others in the community list: Track Changes, Review & Critic, Review Comments, Relay Comments. Sources: https://forum.obsidian.md/t/beta-plugin-commentator-suggestions-and-comments-with-criticmarkup/66013, https://community.obsidian.md/plugins/track-changes (read 2026-10-08).
- pandoc has no built-in CriticMarkup reader in the 3.12 manual I read. A Lua filter or a small converter is needed. Converting CriticMarkup to pandoc's insertion and deletion spans (below) is a few regex lines, and that gives a markdown to tracked-changes .docx route.
- Plain viewers (GitHub, VS Code preview) show the braces as literal text. The file stays readable, which is the point of the format.

### pandoc and tracked changes

- Reader: `--track-changes=accept|reject|all` applies only to the docx reader. `all` emits "spans with insertion, deletion, comment-start, and comment-end classes" with author and time, and `paragraph-insertion` or `paragraph-deletion` spans before affected paragraph breaks. Source: https://pandoc.org/MANUAL.html (read 2026-10-08).
- Writer: the docx writer turns those spans back into `w:ins`, `w:del`, `w:commentRangeStart`, `w:commentRangeEnd` and `w:commentReference`, with `author` and `date` attributes. Source: OpenXML.hs above. Tested with pandoc 3.12:

```markdown
The [quick]{.deletion author="editwright" date="2026-10-08T00:00:00Z"}[slow]{.insertion author="editwright" date="2026-10-08T00:00:00Z"} fox [Tense check.]{.comment-start id="0" author="editwright" date="2026-10-08T00:00:00Z"}jumped[]{.comment-end id="0"} over.
```

- Note the comment span semantics: the text inside `comment-start` is the comment body; the anchored text sits between the start and end spans.
- Limit: pandoc rebuilds the document from markdown, so a writer's original Word styling, headers and layout are lost. Use pandoc only when the source is markdown, not to annotate an existing .docx.
- Known round-trip bugs: a comment on text inside an unaccepted insertion is dropped on read, and JSON to docx can produce empty comments. Source: https://github.com/jgm/pandoc/issues/9833 (read 2026-10-08).

## 4. Recommendation

### Defaults (no install, stdlib only)

1. Suggestion list in markdown. One entry per suggestion: id, location (chapter, paragraph, quoted context), original, proposed, reason, category, confidence. Works everywhere, diffs well in git, and is what the writer accepts or rejects from.
2. CriticMarkup copy of the manuscript. The full text with `{~~old~>new~~}` and `{==span==}{>>reason<<}` inline. Readable raw, live in Obsidian with Commentator, and accept-all or reject-all with MultiMarkdown. editwright can also do accept and reject itself with a few regexes, so the writer needs no tool.

### Optional richer formats

3. Tracked-changes .docx, stdlib writer. For a .docx source, write a copy of the writer's own file with `w:ins`, `w:del` and comments.xml, keeping their styles. For a markdown source, either emit pandoc spans and call pandoc when installed, or write a minimal .docx from a stored template. Start with comments.xml only (no commentsExtended) and add the w15 parts only if Word drops threading or resolve state the writer needs.
4. Google Doc with suggestions, two routes:
   - Zero credentials: upload the tracked-changes .docx to Drive (by hand, or the claude.ai connector's `create_file`) and let Drive convert it. Tracked changes become suggestions. Gives a new Doc.
   - With Google credentials or the Docs MCP server: Docs API `batchUpdate` with `writeMode: SUGGEST` plus `InsertCommentRequest` straight into the writer's existing Doc. Best result, most setup. GA only since 2026-09-30, so recheck before building.

### Risks

- Word acceptance is untested. pandoc and LibreOffice accept the stdlib output; Word is stricter about namespaces and ids. Test in desktop Word and Word for the web before release. Keep a fixture set of real manuscripts (styled runs, footnotes, tables, existing tracked changes, existing comments).
- Run splitting is the main code cost and the main bug source. Suggestions that cross field, hyperlink, footnote or content-control boundaries should fall back to a comment ("suggest: X") instead of a tracked change.
- Documents that already contain tracked changes or comments need careful id handling and must not have their existing revisions touched.
- Google conversion detail (author names, comment anchors, styles) is untested for editwright output.
- The Google Docs API suggestion and comment features are three weeks past GA. Behaviour and limits may still move. Recheck the release notes on each refresh.
- CriticMarkup breaks if the manuscript itself contains `{++`, `{--`, `{~~`, `{==` or `{>>`. Escape or refuse such passages.
- A redline with hundreds of suggestions overwhelms writers in any format. Keep the markdown list as the source of truth and let formats be views of it.
