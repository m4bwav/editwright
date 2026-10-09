---
title: Scripts, nonfiction and long manuscripts
date: 2026-10-08
kind: note
summary: Read this when editwright must edit a screenplay or stage play, write script coverage, check a nonfiction argument or its facts, pick a style guide, or plan passes over a book-length manuscript that will not fit (or should not sit whole) in context.
tags: [research, screenplay, nonfiction, long-form]
---

# Scripts, nonfiction and long manuscripts

Research for editwright, 2026-10-08. Editwright diagnoses and suggests. It never rewrites the author's voice.
Every claim has a source and the date it was checked. "Checked" means fetched or read in search results on 2026-10-08 unless another date is given.
Where only a secondary source was reachable, the line says so.

Related: the sibling skill `D:/m4bwa/Claude/Projects/Ai/cinewright/plugins/cinewright-craft/skills/cinewright-script/SKILL.md`.

## 1. Scripts

### 1.1 What cinewright-script already covers (link to it, do not copy)

Source: `cinewright/plugins/cinewright-craft/skills/cinewright-script/` (SKILL.md and references/, read 2026-10-08; its screenplay-format entry was last checked 2026-10-04).

- Purpose: write a short film, ad or music video script for AI video. Output is `brief.md` and `script.md`, then shot cards.
- `logline-and-beats`: one-sentence logline, act proportions, beats per length, one visible change per beat.
- `scene-turns`: each scene turns a value from positive to negative or back. Goal, opposition, turn in one shot.
- `screenplay-format`: Fountain-style plain text. Slugline (`INT.`/`EXT.`/`INT./EXT.`, place, hyphen, time). Action in present tense, three lines or fewer per paragraph. Character cue in caps. Short parentheticals. Character introduced in caps with age and one detail. Important sound in caps once. No camera directions. Vocabulary: transition, V.O., O.S., CONT'D. Number: one page (12-point Courier, about 55 lines) is about one minute; a 30-60 s film is half a page to a page. Sources it cites: Christopher Riley, The Hollywood Standard, 3rd ed. 2021, and fountain.io.
- `dialogue-for-generated-voices`: 2.5 words a second at most, one speaker per shot, pronunciation respellings. This is specific to AI voice. It is not a rule for human-performed scripts.
- Tooling: `cine.py continuity diff` checks script lines against shot cards and the scene bible.

What cinewright lacks for an editor: Fountain's full markup, stage play format, coverage (logline, synopsis, comments, grid, verdict), reader rubrics and scoring, and the list of things readers complain about. Those go in editwright.

### 1.2 Division of labour

| Job | Owner |
|---|---|
| Write a new script, break a story into beats, shot cards, AI-voice line length | cinewright-script |
| Read an existing script and write notes or coverage | editwright |
| Proofread format (sluglines, cues, parentheticals, transitions, page count) | editwright |
| Flag a line that a reader would call on-the-nose, or a scene with no turn | editwright (suggest only; cite cinewright's scene-turns idea by link) |
| Rewrite dialogue | Neither by default. Editwright quotes the line, names the problem, offers at most one example fix marked as an example. |

### 1.3 Fountain markup (the plain-text format both plugins can read)

Source: https://fountain.io/syntax, spec version 1.1 dated 2014-03-14 (checked 2026-10-08).

- Scene heading: line starts with `INT`, `EXT`, `EST`, `INT./EXT`, `INT/EXT` or `I/E`, any case. Force one with a leading `.`. Optional scene numbers `#1#`, `#1A#`.
- Character: whole line uppercase, blank line before, none after. Extensions in parentheses: `MOM (O.S.)`. Force with `@`: `@McCLANE`.
- Dialogue follows a character or parenthetical. Parenthetical is wrapped in `( )`.
- Dual dialogue: caret after the second character, `STEEL ^`.
- Lyrics: line starts with `~`.
- Transition: uppercase line ending `TO:` with blank lines around it. Force with `>`.
- Centered text: `>THE END<`.
- Emphasis: `*italic*`, `**bold**`, `***bold italic***`, `_underline_`. Escape with `\`.
- Title page: `Key: value` lines at the top. Page break: `===`.
- Sections `#`, `##` and synopses `= ...` are for navigation and do not print.
- Notes `[[ ... ]]` and boneyard `/* ... */` do not print.
- Golden rule, quoted: "make it look like a screenplay."

Editwright use: write notes inside the script as `[[note: ...]]` so they never print, and never touch the text outside them. Use `/* */` only if the author asks to park cut text.

### 1.4 Screenplay format checks an editor runs

Sources: cinewright screenplay-format (Riley 2021, fountain.io); Brian O'Malley, "20 Little Things That Make Script Readers Hate Your Screenplay", Script Magazine, 2018-02-28, https://scriptmag.com/features/20-little-things-make-script-readers-hate-screenplay (checked 2026-10-08).

Mechanical (safe to flag every time):
- Page numbers present. `FADE IN:` at the left margin, not the right.
- Every slugline has INT/EXT, place and time, and fits on one line.
- Character cues consistent: same spelling and the same name for the same person throughout. Flag a major character labelled MAN or WOMAN after the name is known.
- Character names not in all caps inside dialogue (caps are for the cue and the first introduction).
- Parentheticals short and rare. Long ones are action in disguise.
- Action paragraphs short. Large blocks of description are a named complaint.
- No `!!!` or `???`.
- Transitions used sparingly. Camera directions mostly absent in a spec script.
- Page count against the target. One page is about one minute (see cinewright). Flag a feature far outside the usual length as a note, not an error.

Judgement (flag with a reason, let the writer decide):
- Overuse of "we see". Speaking to the reader in action lines.
- Excess wardrobe description. Quoting other films.
- Many flashbacks in the first ten pages.
- Descriptions that reduce a character to looks, age or nationality. O'Malley lists several of these as top irritants (items 14 to 20).

### 1.5 Stage play format (US)

The publisher's own guide was not reachable. Concord Theatricals (which owns Samuel French) offers a "Samuel French Formatting Guide" from its submissions page, and it is not taking unsolicited submissions (search summary of https://www.samuelfrench.com/resources/submissions, which redirects to https://concordtheatricals.com/resources/submissions; fetch was blocked, 2026-10-08). The Dramatists Guild publishes a suggested traditional format, also not fetched. Treat the rules below as the common convention, confirmed only by secondary templates and handouts (search results, 2026-10-08), and tell the user to check the target theatre's or contest's own rules.

- Character name in caps, centered, above the speech. Caps again when the name appears in a stage direction.
- Stage directions indented from the dialogue, in parentheses and often italics, with blank lines around them.
- Act and scene headings centered.
- 12-point Courier or Times. Many contests ask for act-scene-page numbering (for example 1-2-14). Unverified as a universal rule.
- Stage directions show action, not thoughts or backstory ("never stray into superfluous novelistic text", per the template summaries).
- There is no page-equals-minute rule for plays. Do not apply the screenplay timing rule to a play.

Fountain can carry a stage play loosely, but the output will look like a screenplay. Editwright should edit a play in the format it arrives in.

### 1.6 Script coverage

Sources: GL Coverage, "What is script coverage" (2024-07-04) https://glcoverage.com/2024/07/04/what-is-script-coverage and "Formatting and writing studio script coverage" (2024-09-04) https://glcoverage.com/2024/09/04/formatting-and-writing-studio-script-coverage/ ; Duke alumni coverage template https://alumni.duke.edu/sites/default/files/public/deman-transfer/2019/04/Coverage-Template3.pdf (all from search results, 2026-10-08).

A coverage report has five parts:
1. Header: title, writer, form, genre, page count, setting, period, draft date.
2. Logline: one or two sentences with the protagonist, the conflict and the tone.
3. Synopsis: one to two pages of the plot, in present tense, neutral.
4. Grid: each category rated (commonly Excellent / Good / Fair / Poor, or numbers). Common categories: premise or concept, structure or plot, characterization, dialogue, pacing, marketability or commercial potential.
5. Comments, then a verdict for script and for writer: Pass, Consider, or Recommend. Recommend is rare.

Editwright rubric (one row per category, each row cites pages):

| Category | Questions to answer |
|---|---|
| Premise | Is the hook clear in the logline? Is it fresh? |
| Structure | Where are the inciting incident, the act breaks, the midpoint, the climax (page numbers)? Does the main conflict start too late? |
| Character | Does the protagonist want something and change? Are minor characters distinct? |
| Dialogue | Does each voice differ? Is it on the nose? Does it sound written rather than spoken? |
| Pacing | Where does momentum drop? Are beats repeated? |
| Marketability | Genre, budget signals, comparable titles. Mark as opinion. |

The Black List scores. Source: secondary only, since blcklst.com returned 403 on 2026-10-08. Review My Script, "Decoding the Black List" https://reviewmyscript.com/decoding-the-black-list-a-screenwriters-guide/ (search result, 2026-10-08) says readers score Premise, Plot, Character, Dialogue and Setting from 1 to 10, plus an Overall score that is a separate judgement, not an average. An 8 or higher is treated as excellent and can be featured in the site's industry emails. Evaluations were about $75 for a feature or one-hour pilot and about $50 for a half-hour pilot (same source; verify on the site before quoting a price). The Black List's fiction service adds Originality, Prose, Themes and Pace (search summary of https://www.pw.org/content/the_black_list_seeks_next_great_novel). An older FiveThirtyEight analysis of Black List data found comedies scored lower and niche dramas higher, with setting able to offset weaker character or dialogue (https://fivethirtyeight.com/features/how-data-can-help-you-write-a-better-screenplay, search result).

Editwright rule: if the user asks for "Black List style" scores, use those six headings with 1 to 10, give the Overall separately, and say that this is an imitation, not a Black List evaluation.

### 1.7 What readers and executives complain about

Sources: O'Malley 2018 (above); Creative Screenwriting, "Top complaints from creative executives about screenplays" https://www.creativescreenwriting.com/cswcms/top-complaints-from-creative-executives-about-screenplays-what-script-readers-really-want-and-how-writers-can-give-it-to-them/ and Corey Mandell, "10 most common reasons why scripts are rejected" https://www.creativescreenwriting.com/cswcms/10-most-common-reasons-why-scripts-are-rejected/ (search results, 2026-10-08).

- Generic voice: a copy of an existing show, with no emotional stake.
- Dialogue that comes from the writer, not the character, and sounds written.
- A strong opening that loses momentum, then repeats its best beat.
- Main conflict that starts too late after world-building.
- Many small format irritants that add up (section 1.4).

## 2. Nonfiction

### 2.1 Argument structure

Toulmin. Source: Purdue OWL, "Toulmin Argument" https://owl.purdue.edu/owl/general_writing/academic_writing/historical_perspectives_on_argumentation/toulmin_argument.html (search result, 2026-10-08).
- Claim: what the author wants to prove.
- Grounds (data): the reasons and evidence.
- Warrant: the assumption, stated or implied, that links grounds to claim.
- Backing (support for the warrant), qualifier (limits of the claim) and rebuttal (opposing views) are optional but make an argument nuanced.

"They Say / I Say". Gerald Graff and Cathy Birkenstein, 6th ed., W. W. Norton, 2024, ISBN 9781324070030 (library catalogue records via search, 2026-10-08). Core idea: name the view you respond to, then your own, using templates. The 6th edition adds a chapter "In My Experience" and guidance on using generative AI responsibly (same search results).

The Craft of Research. Booth, Colomb and Williams; 5th ed. revised by Joseph Bizup and William T. FitzGerald, University of Chicago Press, 2024-06-25, ISBN 9780226826677 (bookseller and catalogue records via search, 2026-10-08). Its argument model is claim, reasons, evidence, acknowledgment and response, and warrant. The 5th edition adds a chapter on presentations, basic rules for generative AI, and an expanded ethics chapter.

Editwright argument check (diagnose only):
1. Write the claim of the piece in one sentence. If you cannot, that is the first note.
2. For each section: its claim, its grounds, the warrant. Flag missing warrants, and grounds that support a different claim.
3. Flag claims stronger than their evidence and suggest a qualifier. Do not supply the qualifier's wording beyond an example.
4. Check that the "they say" is stated fairly before it is answered. Flag a straw man.
5. Note the strongest objection the text ignores.

### 2.2 Fact-checking practice

Source: Brooke Borel, The Chicago Guide to Fact-Checking, 2nd ed., University of Chicago Press, 2023 (NASW member article https://www.nasw.org/member_article/brooke-borel-chicago-guide-fact-checking-second-edition and publisher-derived catalogue text, search results 2026-10-08).
- Built from interviews with more than 200 writers, editors and checkers (New Yorker, Popular Science, This American Life, Vogue and others).
- Magazine model: an independent checker re-verifies the finished piece.
- Newspaper model: the reporter is responsible for verification, with editors spot-checking.
- Hybrid: magazine model for long, complex or legally sensitive pieces; newspaper model for breaking news and short items.
- What gets checked: names, titles, dates, numbers, quotations, and descriptions or interpretations of data.
- New in the 2nd edition: audio and video, polling data, and sensitive subjects such as trauma and abuse.

Generative tools are unreliable as checkers. The Tow Center at Columbia Journalism Review found eight generative search tools gave incorrect answers on more than 60% of news-citation queries (March 2025; reported in search results 2026-10-08; article https://www.cjr.org/tow_center/we-compared-eight-ai-search-engines-theyre-all-bad-at-citing-news.php, not fetched).

How editwright handles facts:
- Never assert that a fact is true or false from model memory. Mark it.
- Extract checkable claims into a table: `# | location | claim (quoted) | type (name, number, date, quote, place, title, statistic, causal claim) | source given in text | risk (legal, high, normal) | status`.
- Status values: `unchecked`, `source given`, `source given, not matching`, `checked by user`, `checked against <URL, date>`.
- Only use `checked against` when the tool actually fetched a primary source in this session, and quote the line that supports it.
- Quotes: flag every direct quote for checking against the recording or document. Never "fix" a quote's wording.
- Numbers: check internal arithmetic (totals, percentages, units, before and after) yourself; that is not a fact claim.
- Legal risk first: claims about named living people, crimes, health and money.

### 2.3 Style guides and how to choose

| Guide | Current edition (as of 2026-10-08) | Use for | Source |
|---|---|---|---|
| Chicago Manual of Style | 18th, September 2024 | Books, trade and academic publishing, fiction too | Library guides via search, e.g. https://tamu.libguides.com/chicago |
| AP Stylebook | 58th edition, released 2026-08-01 | News, PR, corporate web copy | https://www.mastheadonline.com/news/2026/20260801889.shtml (fetched) |
| APA Publication Manual | 7th (2019); no 8th edition announced | Psychology, social sciences, education, nursing | https://www.apa.org/pubs/books/publication-manual-7th-edition-paperback and search results; no apastyle.apa.org announcement found |
| MLA Handbook | 9th (April 2021); no 10th announced | Literature, languages, humanities papers | https://en.wikipedia.org/wiki/MLA_Handbook and library guides (search) |

Chicago 18th notable changes (library guides, search 2026-10-08): every chapter reviewed for inclusive language and accessibility; scope widened to fiction and self-publishing; place of publication dropped from book citations; bibliography lists up to six authors, more than six becomes the first three plus et al.; guidance on citing AI output and on disclosing AI use.

AP changes: 57th edition (2024-2026 print) switched the primary dictionary to Merriam-Webster, added Artificial Intelligence and Criminal Justice chapters and a self-editing checklist, dropped hyphens after out-, post-, pre- and re- in most cases, and set bullet punctuation (no period after a fragment, period after a full sentence) (PRSA and AP via search, https://www.prsa.org/article/looking-at-the-latest-edition-of-the-ap-stylebook-ST-June24). 58th edition (2026-08-01): over 200 new or revised entries, revised AI chapter, new guidance on assassination, war and genocide, updated race-related language, and closed compounds such as healthcare and primetime (Masthead, fetched).

APA note: some search snippets and SEO pages claim an "APA 8th edition"; they are spam or wrong. Treat 7th as current until apastyle.apa.org says otherwise.

Choosing:
1. The publisher's or outlet's house style wins. Ask for it.
2. Otherwise by venue: news or web copy, AP. Book, Chicago. Course or journal paper, the discipline's guide (APA, MLA, Chicago notes for history).
3. Record the choice and every decision in a style sheet (spellings, capitalization, numbers, serial comma) at the start. Editwright checks consistency against the sheet; it does not impose a guide the author did not choose.
4. Editwright cannot quote these paid guides at length. Cite rule numbers only when the user supplies them or a free official page states them.

### 2.4 Developmental editing for nonfiction

Sources: Jane Friedman, "Book proposal" https://janefriedman.com/book-proposal/ and Writer's Digest, "The 8 Essential Elements of a Nonfiction Book Proposal" https://writersdigest.com/whats-new/the-8-essential-elements-of-a-nonfiction-book-proposal (search results 2026-10-08); writing-centre reverse outline handouts (2.5).

- A proposal is a business case: hook (title and short description), overview, target audience and market ("So what? Who cares?"), comparable titles, author bio and platform, marketing plan, chapter outline or table of contents, and one or more complete sample chapters. Platform often weighs more than prose quality for nonfiction.
- Reader promise: state, from the introduction, what the reader will know or be able to do by the end. Check each chapter delivers a piece of it, and the conclusion pays it off. Flag chapters that serve no part of the promise.
- Chapter structure check: one job per chapter, stated in a sentence; an opening that sets up the question; evidence; a close that answers it and hands off to the next chapter. Flag repeated material across chapters.
- Order: big structure first (promise, chapter order, missing chapters), then chapter arguments, then line edits. Do not line-edit a chapter that may be cut.

### 2.5 Reverse outline

Sources: University of Virginia Writing Center https://writingcenter.virginia.edu/reverse-outlining-organization-strategy ; Caltech, "Revising with Reverse Outlines" https://writing.caltech.edu/documents/29881/Revising_with_Reverse_Outlines.pdf (search results 2026-10-08).

Done after drafting. One line per paragraph with its main idea, or two lines: what it says and what it does (its function). The outline shows paragraphs with too many ideas, ideas left thin, and order problems. This is the per-chapter unit for long manuscripts in section 3.

## 3. Long manuscripts in an LLM context budget

### 3.1 Words to tokens (Claude, current tokenizer)

Source: Anthropic model page for Claude Opus 4.7, https://platform.claude.com/docs/en/models/opus-4-7/overview (fetched 2026-10-08). Quote: "1M tokens is roughly 555k words or 2.5M Unicode characters on the current tokenizer (introduced with Claude Opus 4.7); models before it fit about 750k words in 1M tokens." Current models (Opus 5.5, Sonnet 5.5, Haiku 5.5, Fable 5.1) all list a 1M context and 128K max output on the same page.

That gives about 1.8 tokens per word now, and about 1.33 on pre-4.7 models. The same page also says "200k tokens is roughly 150k words", which matches the old ratio, not the new one. Use 1.8 for planning and count real tokens before committing (the API's token counting endpoint, or the usage figures of a first call). Dialogue-heavy fiction, names and invented words push the ratio up.

| Manuscript | Tokens, current (x1.8) | Tokens, older (x1.33) |
|---|---|---|
| 80k words | ~144k | ~107k |
| 100k words | ~180k | ~133k |
| 120k words | ~216k | ~160k |
| 150k words | ~270k | ~200k |

So on a current Claude model a typical novel does not fit in a 200k window at all, and fits in a 1M window with room to spare.

### 3.2 What the research says about whole-book reading

- NoCha (Karpinska et al., EMNLP 2024, https://arxiv.org/abs/2406.16264 and https://aclanthology.org/2024.emnlp-main.948): 1,001 pairs of true and false claims about 67 recent English novels, written by readers. Humans do it easily. Best model then, GPT-4o, reached 55.8% pair accuracy; no open-weight model beat chance. Models did far better on claims needing one sentence than on claims needing global reasoning, gave wrong explanations even for right labels, and did worse on speculative fiction with heavy world-building. Leaderboard at https://novelchallenge.github.io/ was last updated 2025-07-18 (fetched 2026-10-08; table rows not readable by the fetch).
- FABLES (Kim et al., 2024, https://arxiv.org/abs/2404.01261): 3,158 claims from LLM summaries of 26 books, labelled by people who had read them. Claude 3 Opus was the most faithful. Most unfaithful claims were about events and character states and needed indirect reasoning to catch. Summaries omitted crucial narrative elements and over-weighted events late in the book. No LLM rater correlated strongly with humans at spotting unfaithful claims. Human labelling cost about $200 per book.
- BooookScore (Chang et al., ICLR 2024, https://arxiv.org/abs/2310.00785): two chunked methods. Hierarchical merging (summarise chunks, then merge upward) was more coherent. Incremental updating (keep one running summary) kept more detail but was less coherent.
- NovelQA (Wang et al., ICLR 2025, https://mlanthology.org/iclr/2025/wang2025iclr-novelqa): novels averaging over 200k tokens; models struggled with multi-hop, detail questions and the longest inputs.
- Too Long, Didn't Model (Hamilton, Hicke, Wilkens, Mimno, 2025-05-20, https://arxiv.org/abs/2505.14925): none of seven frontier models kept stable understanding of plot, story-world and elapsed time beyond 64k tokens.
- PRELUDE (Yu et al., 2025-08-13, https://arxiv.org/abs/2508.09848): judge whether a prequel is consistent with the book; 88% of items need evidence from several parts. In-context, RAG, fine-tuning and commercial deep-research tools all trail humans by over 15%, with a 30%+ gap in reasoning accuracy: right answers for wrong reasons.
- Context rot (Chroma, July 2025, https://trychroma.com/research/context-rot, search summary): 18 models including Claude 4, GPT-4.1 and Gemini 2.5 degraded non-uniformly as input grew, even on simple tasks; distractors made it worse.

These papers test older models. No 2026 result was found showing the problem is solved. Takeaways for editwright:
1. A 1M window lets the model see the whole book. It does not make global judgements reliable.
2. Global claims ("the subplot is dropped", "she knew this already in chapter 3") must be backed by quoted passages with chapter and paragraph locations, then re-checked against those passages.
3. Summaries drift on events and character states, and over-weight the ending. Build them per chapter, from the text, and keep them short and factual.
4. Self-grading is weak. Do not let the model rate its own summary as faithful.

### 3.3 Working memory files

Keep these as files beside the manuscript, not in chat:
- `style-sheet.md`: house style decisions (2.3).
- `chapter-cards/NN.md`, one per chapter, 300 to 500 tokens: reverse outline (one line per scene or section with its function), characters present, dated or timed events, facts asserted (names, ages, places, objects), open threads, the chapter's job against the reader promise or the plot. Each line cites a location (chapter, scene, paragraph).
- `bible.md` (fiction) or `claims.md` (nonfiction), merged from the cards, under about 20k tokens: characters with fixed traits and first mention; places; timeline; rules of the world; for nonfiction the claim table from 2.2 and the argument map from 2.1.
- `continuity-log.md`: each conflict found, with both locations quoted, status open or resolved by the author.
- `notes/`: the edit letter and per-chapter notes.

### 3.4 Recommended procedure

Pass 0, measure. Count words and tokens. Split at chapter headings (scene breaks inside long chapters). Target chunk size 4k to 10k words (about 7k to 18k tokens).

Pass 1, map. One call per chapter, chapter text plus the style sheet only. Output that chapter's card. Do not ask for opinions yet. This is hierarchical merging's first step and keeps detail local.

Pass 2, reduce. Merge cards into the bible or claims file and the book-level reverse outline (one line per chapter). Run consistency checks on the bible itself: the same fact with two values is a candidate continuity error. Each candidate goes to the log with both locations.

Pass 3, verify. For each candidate and each global note, load the cited passages (not the whole book) and confirm or drop it. Quote the lines. This is the guard against NoCha and PRELUDE style errors.

Pass 4, developmental read. With the book-level outline, the bible and the verified log, write the edit letter: promise or premise, structure, character arcs or argument chain, pacing, cuts and gaps. Cite chapters.

Pass 5, line and copy edit. Per chapter, with the style sheet, that chapter's card, the bible entries for characters and places in it, and the neighbouring chapters' cards. Suggestions only, as tracked-change style notes or `[[ ]]` notes in Fountain.

Budget for a 1M-context model (current tokenizer):
- The whole 150k-word book (~270k tokens) fits. Use it in one pass only for "find all mentions" style questions, and still verify by quoting.
- Per call in passes 1 and 5: instructions ~5k, style sheet ~2k, bible ~20k, chapter ~7k to 18k, neighbours ~2k, output reserve 8k to 16k. Total about 45k to 65k, well under the 64k region where TLDM saw drift.
- Pass 4: outline (~3k to 6k for 30 to 40 chapters) plus bible (~20k) plus log; under 50k. Add up to three full chapters if needed.
- Use prompt caching on the fixed prefix (instructions, style sheet, bible) across chapter calls; cache reads are a fraction of the base input price (same Anthropic page). Batch API halves cost when results are not needed at once.

Budget for a 200k-context model:
- Never load the whole book. A 100k-word novel is about 180k tokens and leaves no room to think or answer.
- Per call: instructions ~4k, style sheet ~2k, bible capped at ~15k, chapter up to ~18k, output reserve ~8k. Total about 50k. Keep at least half the window free.
- Global questions run only through the bible, the cards and targeted passage loads (pass 3). If the bible grows past 15k, split it (characters, places, timeline) and load only the parts a chapter touches.

Same procedure for nonfiction: cards carry each chapter's claim, grounds, warrant and the checkable facts; the reduce step builds the argument map and the claim table; the verify step quotes the passages; the developmental read tests the reader promise.

## Open questions

- Black List, Concord and Dramatists Guild pages were not reachable (403 or blocked). Re-check categories, prices and format rules before editwright ships text quoting them.
- Measure the real tokens-per-word ratio on a sample manuscript with the token counting endpoint; this environment had no API key on 2026-10-08.
- The NoCha leaderboard rows (current model scores) could not be read; check in a browser.
