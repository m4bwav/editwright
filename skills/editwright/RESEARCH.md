# Research: editwright

Findings that back [SKILL.md](SKILL.md). Changes they caused are logged in [CHANGELOG.md](CHANGELOG.md); procedural lessons live in [LEARNINGS.md](LEARNINGS.md); test runs and their evidence in [TESTS.md](TESTS.md); schedule and state in `evergreen.json`. Protocol: MAINTENANCE.md.

Topic: Professional editing practice (levels of edit, editorial letters, style sheets, fiction and nonfiction craft, script coverage), AI-text provenance rules (watermarks, detectors, copyright, publisher and contest policies) and manuscript-editing tools, for an agent that diagnoses and never rewrites the author. Tier `moderate`. Last refresh 2026-10-08; next due 2026-11-07.

## Current understanding

Full notes, every claim sourced and dated, are in the repository's `ai-docs/research/` (five notes of 2026-10-08); the distilled rules are in [kb/](kb/INDEX.md).

- Levels of edit are settled practice (CIEP, EFA, ACES, Chicago 18th of 2024): big to small, each level with hard scope limits; a copyedit does no substantial rewriting, a proof does no rephrasing. CIEP: an editor should not change the author's tone or style unless it fails the intended readers. EFA and CIEP disagree on where line editing and assessment sit. Confidence high.
- Fiction craft lenses (Gardner, Swain, Browne and King, Saunders, Le Guin, Maass, Story Grid, Truby, McKee) are current and respected; Cron's brain-science framing is criticised; Gardner's "continuous dream" is contested for metafiction. Confidence high for the questions, medium for status claims.
- Since 2026-08-14 Anthropic watermarks text that new Claude models write (a SynthID-Text variant); only words Claude chooses carry it, and a light proofread of human text leaves "very little (if anything)" to detect. Google SynthID Text and OpenAI textGrain (2026-10-05, EU) work alike. EU AI Act Art. 50 applies since 2026-08-02 with an editing exemption. Confidence high (primary pages fetched); detector access is limited to eligible organisations. Moving fast.
- The rules that matter to authors are about who wrote the words: KDP (AI-assisted editing needs no disclosure, AI-generated text does), Authors Guild Human Authored (de minimis AI), US Copyright Office (disclaim more than de minimis AI text), strict magazines and contests (Clarkesworld, Asimov's, Uncanny, Writers of the Future, Nebulas) ban AI-written text and some ban AI help of any kind. No policy publishes a percentage; editwright's 0 (fiction) and 1% capped at 50 words (nonfiction) are its own choice. Confidence medium; some policy pages could not be fetched.
- Tools: generators (Sudowrite, Novelcrafter, NovelAI, Squibler) rewrite; analysers (Marlowe, Fictionary, Plottr) diagnose. Grammarly Authorship labels spans but once laundered its own rewrites as human. The closest open plugin, APODICTIC, has a no-drafting firewall but no ledger. No tool combines diagnosis, an enforced no-rewrite rule and an author-owned ledger. Confidence medium.
- Delivery: a stdlib .docx with tracked changes and comments is feasible (read back by pandoc and LibreOffice; not yet opened in Word). python-docx 1.2.0 has comments but no tracked changes. The Google Docs API gained SUGGEST write mode and range comments on 2026-09-30; uploading a .docx converts tracked changes into suggestions. Confidence medium; Word and the Google conversion of editwright's output are untested.
- Long manuscripts: whole-book context does not make global judgements reliable (NoCha, FABLES and 2025 follow-ups); use chapter cards, a story bible and quoted evidence for every global note. Tokens per word on the newest tokenizer is unsettled (about 1.3 to 1.8).

## Open questions

- Does Word open editwright's review.docx without a repair prompt? Does Google Docs import it as suggestions? (untested 2026-10-08)
- Tokens per word on the current Claude tokenizer: measure with the token-counting API.
- Society of Authors, Medium, Simon & Schuster and NYC Midnight AI rules: pages unreachable or not found on 2026-10-08.
- Black List evaluation categories and US stage-play format pages were blocked; facts from secondary sources.
- Should editwright use the Docs API SUGGEST mode directly once it settles (it is weeks old)?

## Search plan

Four tracks; every refresh runs at least one query on each (scope each to the period since the last refresh; add the year). Protocol §4 explains the tracks and how tooling, practice and testing findings are judged.

Subject (the goal and the latest thinking on reaching it):

- `Claude text watermark OR SynthID text OR textGrain <year>`; `anthropic.com/news` watermark updates
- `"AI-assisted" "AI-generated" KDP OR "Authors Guild" OR "Copyright Office" policy <year>`
- `Clarkesworld OR Asimov's OR "Writers of the Future" AI policy submissions <year>`
- `Chicago Manual of Style 18th OR 19th edition update <year>`; `CIEP OR EFA levels of editing <year>`
- `AI detector false positive study <year>`; `EU AI Act Article 50 code of practice text marking <year>`

Tooling (skills, plugins, MCP servers, scripts, knowledge graphs built for this subject):

- `path:SKILL.md "manuscript editing"` on GitHub code search, sorted by recently updated; `npx skills find "manuscript editing"` and skills.sh for install counts
- `https://registry.modelcontextprotocol.io/v0/servers?search=manuscript editing`; fallback `"manuscript editing" mcp server site:glama.ai OR site:pulsemcp.com`
- `"manuscript editing" skill OR plugin OR "mcp server" <year> site:github.com`
- Most used: skills.sh weekly and 24-hour installs for `manuscript editing` (never all-time; exclude meta and installer skills); `anthropics/claude-plugins-official` and `claude-plugins-community` searched for `manuscript editing` (record the tier)
- Practitioner test on every candidate: commit in the last 90 days, issues answered, no bundled `*.test.*` or `conftest.py` from an unknown author, author has other work in the area, ships `evals/` or paired results; `path:SKILL.md "manuscript editing" evals OR benchmark`
- Provenance tiebreaker: which model and reasoning setting wrote each candidate (`evals.json` / frontmatter `model`, README or changelog credit, commit messages); prefer the latest frontier model at its highest reasoning setting, read over inferred
- Supersession sweep: `"manuscript editing" skill deprecated OR superseded OR archived <year>`; archive flag on every tool already listed here

Most discussed and the converged thinking (comment volume over points; what the most-used and most-discussed sources agree on becomes a claim in Current understanding):

- `hn.algolia.com/api/v1/search_by_date?query=manuscript editing` and `site:reddit.com/r/ClaudeAI OR r/ClaudeCode "manuscript editing" <month>`
- OpenAlex `works?search=manuscript editing agent&sort=cited_by_count:desc&filter=from_publication_date:<last check>`; the two most-cited through Semantic Scholar

Practice (how others use AI agents on this goal, and everything in between):

- `"how I use" OR "my workflow" "manuscript editing" "claude code" OR codex OR cursor <year>`
- `site:arxiv.org "manuscript editing" agent "case study" OR empirical OR telemetry <year>`
- `"manuscript editing" site:simonwillison.net OR site:latent.space OR site:anthropic.com/engineering <year>`; hn.algolia.com `"manuscript editing" agent` sorted by date

Testing (how work on this subject is verified, and how skills for it are tuned):

- `"manuscript editing" verify OR validate OR "smoke test" OR checker agent <year>` (what evidence shows the job was done)
- `path:SKILL.md "manuscript editing" test OR eval OR evals` on GitHub; `"manuscript editing" evals OR "eval suite" OR regression "agent skill" <year>`
- `site:arxiv.org "manuscript editing" agent evaluation OR benchmark <year>`; promptfoo, Inspect or DeepEval docs for assertion types that fit this subject

Best sources (primary first): CIEP, EFA and ACES pages; Chicago Manual of Style Online; anthropic.com/news and the policy pages of KDP, the Authors Guild, the US Copyright Office and each magazine; GitHub code search for SKILL.md files. Sources that proved noisy: SEO lists of AI writing tools, spam pages about an APA 8th edition, Reddit (blocked; use search snippets).

## Findings log

Newest first. One entry per material finding; a quiet refresh gets one entry saying so. `Track` is subject, tooling, practice, or testing.

### R-20261008-5 · 2026-10-08 · Delivery formats (testing track: how output is checked)
- Summary: stdlib tracked-change and comment .docx verified by reading back with pandoc and LibreOffice; pandoc can write tracked changes from spans; CriticMarkup for markdown; Google Docs API SUGGEST mode is new; the Drive connector can upload and convert but not comment.
- Track: testing
- Sources: ../../ai-docs/research/2026-10-08-delivery-formats.md
- Magnitude: n/a (initial)
- Applied: C-20261008-1 (review.docx export, kb/delivery.md)

### R-20261008-4 · 2026-10-08 · Scripts, nonfiction and long manuscripts
- Summary: cinewright-script covers writing; editwright covers notes, coverage and format proofreading. Toulmin, They Say / I Say, The Craft of Research, Borel's fact-checking guide; AP 58th (2026-08-01), APA 7, MLA 9, Chicago 18. Long-manuscript procedure with chapter cards and token budgets.
- Track: subject, practice
- Sources: ../../ai-docs/research/2026-10-08-scripts-nonfiction-books.md
- Magnitude: n/a (initial)
- Applied: C-20261008-1 (kb/scripts.md, kb/nonfiction.md, kb/long-manuscripts.md, `ew.py chunk`)

### R-20261008-3 · 2026-10-08 · Editing tools and public skills
- Summary: survey of ProWritingAid, Grammarly (Superhuman), Sudowrite, Novelcrafter, AutoCrit, Marlowe, Fictionary, Hemingway, Lex, Plottr and public skills (APODICTIC, gerunds, humanizer skills). Ideas taken: provenance that cannot be laundered, an enforced firewall, the KDP line, anchored comments, the genre contract first, countable line reports, short ranked lists.
- Track: tooling, practice
- Sources: ../../ai-docs/research/2026-10-08-tools-survey.md
- Magnitude: n/a (initial)
- Applied: C-20261008-1 (echo rule in apply, severity ranking, stats)

### R-20261008-2 · 2026-10-08 · AI-text provenance: watermarks, detectors, copyright, policies
- Summary: Claude text watermark since 2026-08-14 (only on words Claude chooses); SynthID, textGrain; EU Art. 50; detector false positives; KDP, Authors Guild, Copyright Office, strict magazines and contests. Defaults: 0 AI-written words in fiction, 1% capped at 50 words in nonfiction.
- Track: subject
- Sources: https://www.anthropic.com/news/claude-text-watermark (fetched 2026-10-08), ../../ai-docs/research/2026-10-08-ai-text-provenance.md
- Magnitude: n/a (initial)
- Applied: C-20261008-1 (THRESHOLDS in ew.py, kb/ai-text-rules.md)

### R-20261008-1 · 2026-10-08 · The craft of editing
- Summary: levels of edit and their limits (CIEP, EFA, ACES, Chicago 18), deliverables (letter, queries, style sheet, story bible), fiction and short-story craft lenses with status and criticism, full-manuscript method, checklists per level.
- Track: subject
- Sources: ../../ai-docs/research/2026-10-08-editing-craft.md
- Magnitude: n/a (initial)
- Applied: C-20261008-1 (SKILL.md passes, kb/levels.md, kb/deliverables.md, kb/fiction.md, kb/short-story.md, kb/line-copy-proof.md)
