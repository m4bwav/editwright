---
title: AI text provenance, watermarks, detectors, copyright and publisher rules
date: 2026-10-08
kind: note
summary: Read before deciding how editwright marks, limits or explains AI-written words in a manuscript, or when an author asks whether AI editing will watermark their text or cost them human authorship.
tags: [research, provenance, watermark, copyright, ai-policy]
---

# AI text provenance, watermarks, detectors, copyright and publisher rules

Read this when you design editwright's suggestion flow, set its AI-word thresholds, or answer an author who worries that AI editing leaves a watermark or costs them human-authored standing.

All facts were checked on 2026-10-08 unless a line says otherwise. "Unverified" means the claim comes from a secondary source only, or the primary page could not be read.

## Headline correction

The brief assumed Claude does not watermark text. That is no longer true.

- Anthropic announced on 2026-08-14 that Claude text carries a watermark. It is "a version of the SynthID-Text approach published by Google DeepMind." Source: https://www.anthropic.com/news/claude-text-watermark (checked 2026-10-08).
- Supported models include Claude Fable 5.1, Mythos 5.1, Opus 5.5, Sonnet 5.5 and Haiku 5.5, across the API, Claude apps, Claude Code, Cowork and Claude Tag. Older models get it during the EU transition. Source: https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content (checked 2026-10-08).
- So the author's worry is partly right. Words Claude writes now carry a statistical mark. The model running editwright (Opus 5.5 in this session) is on the list.

The mark lives in Claude's word choices. It does not live in the author's words. That is the fact editwright is built on.

## 1. Text watermarking

### How these watermarks work

- SynthID Text changes how the model samples the next token. A secret key and the preceding few tokens drive a pseudorandom "g-function". Google calls the sampling step tournament sampling. Detection scores how well a text's word choices agree with the keyed function. Source: https://ai.google.dev/responsible/docs/safeguards/synthid (checked 2026-10-08).
- No characters are added. Nothing is visible. The signal is spread across many word choices, so it needs length.
- Google open-sourced SynthID Text in October 2024 through Hugging Face Transformers (v4.46+). The open library only detects text marked with your own keys. Sources: https://www.technologyreview.com/2024/10/23/1106105/google-deepmind-is-making-its-ai-text-watermark-open-source (checked 2026-10-08); the Transformers version number is from a secondary summary and is unverified.

### Google (Gemini)

- Gemini app text has carried SynthID marks since May 2024. Source for the date: secondary summaries; unverified against a Google primary page.
- Google's own limits: robust to "cropping pieces of text, modifying a few words, or mild paraphrasing". Confidence "can be greatly reduced when an AI-generated text is thoroughly rewritten, or translated to another language." Weaker on factual answers. Source: https://ai.google.dev/responsible/docs/safeguards/synthid (checked 2026-10-08).
- SynthID Detector portal was announced 2025-05-20. It checks images, audio, video and text from Google models. Access started as a waitlist for journalists, media and researchers. Over 10 billion items had been marked by then. Source: https://blog.google/technology/ai/google-synthid-ai-content-detector/ (checked 2026-10-08).
- Academic work shows paraphrase, back-translation and copy-paste dilution degrade SynthID Text, and one paper describes a "layer inflation" attack. Sources: https://arxiv.org/html/2508.20228v1 and https://arxiv.org/abs/2603.03410v2 (checked 2026-10-08).
- Light edits of human text by Gemini: Google publishes no specific statement. By the mechanism, only tokens Gemini sampled can carry signal. A light proofread leaves few such tokens. This is inference, not a Google claim.

### Anthropic (Claude)

- Announced 2026-08-14, updated 2026-09-01. Based on SynthID-Text. No hidden characters, no extra tokens, no quality change claimed. Source: https://www.anthropic.com/news/claude-text-watermark (checked 2026-10-08).
- On proofreading: "When Claude proofreads text written by a person, what it gives back has generally only been lightly edited; because nearly all the words are the person's, there's very little (if anything) for the watermark to attach to." Same source.
- On robustness: "Light editing probably won't remove the watermark completely; a complete rewrite where every word is replaced will." Same source.
- Where output is forced (no choice of word), no mark is applied. Same source.
- The support page adds that output "can carry a Claude mark even if the underlying ideas, text, or data originated from another source", for example translation. Source: https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content (checked 2026-10-08).
- The mark carries no user identity. Same two sources.
- Detection is a private-preview API for eligible organizations named in EU law (regulators, law enforcement, media, fact-checkers, researchers, educators, civil society). The public Claude Content Checker checks files only; it says "The tool does not check text." Source: https://claude.com/check-files (checked 2026-10-08).
- No opt-out is described on either Anthropic page.

### OpenAI (ChatGPT, Codex, API)

- In 2024 OpenAI reportedly built a text watermark and held it back. That history is from press reports and is unverified here.
- On 2026-10-05 OpenAI announced "textGrain", a statistical word-choice watermark. ChatGPT and Codex text gets it for EU users over the following weeks. API customers anywhere can opt in for some models; it is off by default in the API. ChatGPT outside the EU is unchanged. Sources: https://openai.com/index/eu-text-provenance/ (returned 403; content taken from the official repost at https://community.openai.com/t/openais-approach-to-eu-text-provenance-rules/1403521, checked 2026-10-08).
- OpenAI says the mark cannot identify the user, measure human contribution, or prove ownership, and that its absence does not prove human authorship. Same community source.
- Reported robustness from OpenAI's evaluation: about 95% detection on untouched 400-token English passages, 66% after 10% of words are swapped for synonyms, 17% after 25%. Source: https://letsdatascience.com/blog/openai-watermarks-chatgpt-codex-in-eu-rewrite-erases-mark (checked 2026-10-08). Unverified against OpenAI's paper at https://cdn.openai.com/pdf/e9508624-d767-41b6-a26d-e34ca798ada6/textgrain-entropy-calibrated-watermarking-for-language-model-text.pdf.
- Detector access starts with approved researchers and expert organizations. Source: community repost above.

### Meta, Microsoft, Mistral, others

- Meta, Microsoft, Mistral, Google, OpenAI and Anthropic are among about 190 first signatories of the EU Code of Practice on Transparency of AI-Generated Content (list published 2026-07-31). Source: https://digital-strategy.ec.europa.eu/en/news/strong-backing-code-practice-transparency-ai-generated-content (checked via search snippet 2026-10-08; page not fetched in full).
- Signing implies each must mark text output for the EU. I did not find each company's text-watermark launch page. Treat their text marking status as unverified.
- vLLM reportedly integrated a similar watermark in September 2026. Unverified, from the letsdatascience source above.

### C2PA and text

- C2PA (Content Credentials) is mostly for files. Claude attaches signed C2PA metadata to generated images and similar files, not to plain text. Source: Anthropic support page above.
- The C2PA spec has a method for "Embedding Manifests into Unstructured Text" using non-rendering Unicode variation selectors. The spec says to use it only when no other method works. Source: https://docs.rs/c2pa-unstructured-text (checked 2026-10-08; this is an implementation's description of the spec, the spec itself was not read).
- Practical effect: invisible characters are easy to strip and are what editors call "hidden characters". The big model vendors chose word-choice watermarks instead.

### EU AI Act Article 50

- Article 50(2): providers of generative systems must mark output "in a machine-readable format and detectable as artificially generated". It does not apply "to the extent the AI systems perform an assistive function for standard editing or do not substantially alter the input data provided by the deployer or the semantics thereof." Source: https://artificialintelligenceact.eu/article/50/ (checked 2026-10-08).
- Article 50(4): deployers who publish AI-generated text "on matters of public interest" must disclose it, unless the text "has undergone a process of human review or editorial control" and someone holds editorial responsibility. Fiction and memoir are generally not "matters of public interest". Same source; the fiction reading is my interpretation.
- Application date: 2026-08-02. Source: https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content (checked 2026-10-08).
- Transition: systems placed on the market before 2026-08-02 have until 2026-12-02 for the 50(2) marking duty, under the Digital Omnibus. Source: https://www.garrigues.com/en_GB/garrigues-digital/ai-digital-omnibus-regulation-has-been-published-redefining-deadlines-and (search snippet, checked 2026-10-08; unverified against the Official Journal).
- Code of Practice on Transparency of AI-Generated Content: drafts in late 2025 and 2026-03-05, final on 2026-06-10. It is voluntary but the Commission and AI Board call it adequate to show compliance. It combines signed metadata and imperceptible watermarks. Sources: https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content and the signatories page above (checked 2026-10-08).
- Note the gap: the Act exempts "standard editing", yet Anthropic marks every token Claude samples. In practice a light edit carries little mark because few words are Claude's.

### California SB 942 (AI Transparency Act)

- AB 853 (signed 2025-10-13) delayed SB 942's operative date to 2026-08-02. Large-platform duties start 2027-01-01. Sources: https://www.troutmanprivacy.com/2025/10/california-ai-transparency-act-amendments-signed-into-law/ and https://infobytes.orrick.com/2025-10-17/california-delays-its-ai-transparency-act-and-passes-new-content-laws/ (search snippets, checked 2026-10-08).
- Scope: SB 942 covers image, video and audio content. Its latent-disclosure and detection-tool duties do not cover text. This is from my reading of the bill text before the cutoff; unverified today.

## 2. AI detectors

Detectors guess from style. Watermark checks read a keyed signal. They are different tools.

### Reliability evidence

- Liang et al. (Stanford), "GPT detectors are biased against non-native English writers", Patterns 2023. Seven detectors, 91 TOEFL essays by non-native writers. Average false positive rate 61.22%. All seven flagged 18 essays (19.78%). At least one flagged 89 (97.80%). US 8th-grade essays were near-perfectly classed as human. Source: https://arxiv.org/abs/2304.02819 (PDF read 2026-10-08).
- The same paper found a simple "elevate the language" self-edit prompt dropped detection of ChatGPT essays from 100% to 13%. Same source.
- Russell, Karpinska and Iyyer (2025): people who use ChatGPT often, voting in groups of five, misclassed 1 of 300 articles. They beat most commercial and open detectors, even against paraphrase and "humanizers". Pangram was the strong automated exception in that paper (unverified detail; abstract does not name it). Source: https://arxiv.org/abs/2501.15654 (checked 2026-10-08).
- EditLens (Pangram Labs, UMD, UMass; ICLR 2026) measures how much AI editing a text has. It separates human, AI-edited and AI-generated text (ternary F1 90.4%). In its Grammarly case study, "Fix any mistakes" was the lightest edit; "Summarize this" and "Make it more detailed" were the heaviest. Source: https://arxiv.org/abs/2510.03154 and https://arxiv.org/html/2510.03154v1 (checked 2026-10-08).
- Turnitin says it targets under 1% document false positives and now hides scores in the 1 to 19% band behind an asterisk. Independent tests report much higher rates. Sources: https://highereddive.com/news/turnitin-false-positives-AI-detector/652356 and https://www.popularai.org/p/these-turnitin-false-positives-in (search snippets, checked 2026-10-08; independent numbers unverified).
- Vendor league tables (GPTZero, Pangram, Originality.ai, Copyleaks) disagree and are mostly vendor-run. Example claims: Pangram about 1 in 10,000 false positives; Originality.ai flagged 19 of 495 human passages in one test. Source: https://www.casrai.org/guides/most-accurate-ai-detector (checked 2026-10-08). Treat all such numbers as unverified.

### Does light AI editing trigger detectors?

- Turnitin's community answer: in initial tests, Grammarly-type grammar fixes on human text were mostly not flagged. ChatGPT text run through Grammarly still was. Source: https://turnitin.forumbee.com/t/g9hcsxv/ai-detection-and-grammarly?pg=2 (checked 2026-10-08; forum, unverified).
- Newer detectors look for AI editing on purpose. Substack added Pangram scanning for readers on 2026-07-21/22. It labels posts over 100 words as human-written, AI-assisted or AI-generated. Writers can scan drafts, add a "How I make this" note, and dispute results. Source: https://techcrunch.com/2026/07/22/substacks-new-tool-tells-you-whos-been-writing-their-newsletters-with-ai/ (checked 2026-10-08).
- The US Copyright Office has begun sending examination letters saying "some of the text in this work may have been generated by artificial intelligence" to authors who say they wrote alone. Both reported authors answered "solely for proofreading" and were registered within days. Source: https://www.authormedia.com/the-us-copyright-office-is-flagging-human-written-books-as-ai/ (week ending 2026-09-11, checked 2026-10-08). Unverified against a Copyright Office statement.

### Takeaway for editwright

- If the author types every change himself, the final words are his. A watermark has almost nothing to attach to. Anthropic says so directly.
- Style detectors are a separate risk. They can flag pure human prose, most of all from non-native or very plain writers. No tool can promise a clean score.
- Accepting AI phrasing word for word is the risk case. EditLens-style detectors can see it, and Claude's mark rides on any run of words Claude sampled.
- So: suggest the problem and the reason; let the author write the fix. Where a suggestion must show wording, keep it short and count any accepted verbatim words as AI words.

## 3. Copyright

### United States

- Registration guidance (2023-03-16, 88 Fed. Reg. 16,190): applicants must disclose AI-generated material that is "more than de minimis" and describe the human part. Source: https://www.copyright.gov/ai/ (checked 2026-10-08).
- Part 2 report, Copyrightability (2025-01-29): "The use of AI to assist in the process of creation or the inclusion of AI-generated material in a larger human-generated work does not bar copyrightability." Prompts alone are not enough. Human selection, arrangement or modification of AI output can be protected. Source: https://copyright.gov/newsnet/2025/1060.html (checked 2026-10-08).
- Part 3 (training) exists only as a pre-publication version from 2025-05-09. Source: https://www.copyright.gov/ai/ (checked 2026-10-08).
- Thaler v. Perlmutter: the D.C. Circuit held in March 2025 that a work needs a human author. The Supreme Court denied certiorari on 2026-03-02 (No. 25-449). Sources: https://www.scotusblog.com/cases/case-files/thaler-v-perlmutter and https://www.bakerbotts.com/thought-leadership/publications/2026/march/supreme-court-denies-petition-on-copyright-authorship-by-ai (checked 2026-10-08).
- Allen v. Perlmutter (D. Colo., filed 2024-09-26) tests a Midjourney image with heavy prompting. No ruling found as of today. Source: https://dockets.justia.com/docket/colorado/codce/1:2024cv02665/237436 (checked 2026-10-08).
- The Register testified on 2026-05-12 that over 7,000 claims with disclaimed AI material had been registered. Source: search snippet citing https://www.copyright.gov/laws/hearings/ (unverified; the PDF could not be parsed).
- Spellcheck and grammar suggestions: the Office's own follow-up form (as reported) treats "solely for proofreading to correct the spelling, punctuation, and/or grammar" as needing no AI disclaimer. Source: Author Media article above (unverified).

### UK and EU, briefly

- UK: section 9(3) CDPA protects "computer-generated works" with no human author. The government's 2026 report under the Data (Use and Access) Act gave a provisional view that it should be repealed; no final decision. AI-assisted works with real human creativity stay protected. Source: https://www.hsfkramer.com/notes/ip/2026-03/uk-government-report-on-copyright-and-ai-concludes-more-evidence-is-needed-although-s9-3-cdpa-could-go (checked 2026-10-08).
- EU: originality means "the author's own intellectual creation" (CJEU case law such as Infopaq). Pure AI output is widely read as unprotected. No EU statute on this. From memory of the case law; unverified today.

## 4. Publisher, magazine, contest and platform policies

Key: S = spell and grammar check, E = AI editing suggestions the author acts on, G = AI-generated text.

### Book publishers

- Penguin Random House: copyright pages say "No part of this book may be used or reproduced in any manner for the purpose of training artificial intelligence technologies or systems." It protects the book from training, it says nothing about authors' own AI use. Source: https://authorsguild.org/news/ag-encouraged-by-penguin-random-house-ai-restrictions/ (checked 2026-10-08).
- PRH, Hachette and Macmillan have contract language promising not to license work for training without consent, often added only on request. Hachette reportedly asks authors to tell it about AI assistance "aside from minor editing and correcting". Source: https://janefriedman.com/publishers-begin-to-add-ai-language-to-contracts/ (search snippet, checked 2026-10-08; unverified).
- HarperCollins licensed some nonfiction backlist to an AI company in 2024, opt-in, reported at $5,000 per title split with the author. Source: https://www.publishersweekly.com/pw/print/20241125/96533-agents-authors-question-harpercollins-ai-deal.html (checked 2026-10-08 via snippet).
- No Big Five house has a public, house-wide rule on authors' AI use that I could find. Expect contract warranties of original authorship. Simon & Schuster: no public policy found.

### Authors Guild Human Authored certification

- Launched January 2025, later opened to all authors published in the US. Members free, others $10 per title. Source: https://authorsguild.org/human-authored/faq/ and https://authorsguild.org/news/human-authored-certification-expands-to-all-authors/ (checked 2026-10-08).
- Definition: the text was "fully authored by one or more human beings and not generated by GAI, except that a de minimis (e.g., very small or trifling) amount of text may be generated or modified by or with the use of GAI", for example through AI spell and grammar checkers or to create indices. Same FAQ.
- AI for research, brainstorming or outlining does not disqualify. S: yes. E: yes, if the author writes the text. G: only de minimis. No numeric limit is published.

### Society of Authors (UK)

- Publishes AI guidance on authors' own AI use and on publishers' use. Details could not be fetched (site blocked, Bookseller paywalled). Source: https://thebookseller.com/news/soa-urges-vigilance-in-new-ai-guidance-for-authors (checked 2026-10-08). Unverified.

### Amazon KDP

- "AI-generated": text, images or translations created by an AI tool, "even with substantial edits afterward". Must be disclosed.
- "AI-assisted": you created the content and used AI to "edit, refine, error-check, or otherwise improve" it, or to brainstorm. Disclosure optional.
- Source: https://kdp.amazon.com/en_US/help/topic/G200672390 (checked 2026-10-08). S: fine. E: fine, no disclosure. G: allowed with disclosure.

### SF and fantasy magazines

- Clarkesworld: will not accept work "translated, written, developed, or assisted by these tools"; may ban. Source: https://clarkesworldmagazine.com/submissions/ (checked 2026-10-08).
- Asimov's (and Analog, same publisher): "We will not consider any submissions written, developed, or assisted by these tools." Source: https://asimovs.com/contact-us/writers-guidelines/ (checked 2026-10-08).
- Uncanny: no submissions "written with artificial intelligence or similar technologies"; undisclosed use leads to a ban. Source: https://www.uncannymagazine.com/submissions/ (checked 2026-10-08).
- F&SF: editor Sheree Renee Thomas bans chatbot submitters permanently. Source: https://www.npr.org/2023/02/23/1159118948/sci-fi-magazine-stops-submissions-after-flood-of-ai-generated-stories (2023 quote; current guidelines not checked).
- "Assisted" in these rules is broad. None defines whether an AI grammar checker counts. Treat E as risky. G: banned.

### Awards and contests

- Nebula (SFWA): after a reversal in December 2025, works "written, either wholly or partially" by LLMs are ineligible; works that "used LLMs at any point during the writing process" must disclose and are disqualified. Critics note this may catch LLM-backed spell and grammar checkers. Source: https://www.steampunk-explorer.com/news/sfwa-retreats-after-opening-nebula-awards-works-created-gen-ai (checked 2026-10-08; SFWA primary not fetched). Year of the December change is inferred; unverified.
- Hugo (WSFS): a 2025 generative-AI resolution was referred to committee (89-36). The 2026 business meeting summary shows no AI rule passed. Sources: https://file770.com/seattle-worldcon-2025-july-19-business-meeting-session/ and https://fromtheheartofeurope.eu/wsfs-business-meeting-2026/ (checked 2026-10-08).
- Writers of the Future: work "cannot be generated, in whole or in part, by Artificial Intelligence." Source: https://writersofthefuture.com/contest-rules-writers/ (checked 2026-10-08).
- NYC Midnight and most literary-magazine contests: not verified today. Many small magazines allow only "non-generative assistive technologies such as spellcheck" (example: TwoTwoOne.NYC, https://twotwoonenyc.submittable.com/submit, snippet).

### Platforms

- Medium: AI-generated writing cannot be paywalled in the Partner Program. Undisclosed AI writing gets network-only distribution. Stories with AI assistance must be labelled. Source: https://help.medium.com/hc/en-us/articles/22576852947223-Artificial-Intelligence-AI-content-policy (403 on fetch; from search snippet 2026-10-08, unverified wording). Whether grammar checkers count as "AI assistance" is not clear.
- Substack: no ban. Readers can run Pangram on posts (see section 2). Optional disclosure note. Source: TechCrunch link above.

## 5. What to tell the author

### Plain explanation

1. SynthID is Google's watermark, but Claude now uses a version of it too. Since August 2026, new Claude models mark the words they write. OpenAI marks ChatGPT text for EU users from October 2026.
2. The mark sits in which words the model picks. It adds no hidden characters and does not name you.
3. It only attaches to words the model chose. Words you type yourself carry no mark. Anthropic says a light proofread of your text leaves "very little (if anything)" to detect.
4. Only regulators, researchers and similar groups can run the text checkers today. Publishers and readers cannot.
5. The bigger practical risks are style detectors and rules, not watermarks. Detectors can flag plain human prose, and Substack now lets any reader scan a post.
6. The rules care about who wrote the words. KDP calls AI editing of your own text "AI-assisted", with no disclosure needed. Text an AI writes stays "AI-generated" even after heavy edits.
7. The Authors Guild's Human Authored mark allows only a "de minimis" amount of AI text, such as grammar-checker fixes.
8. Clarkesworld, Asimov's, Uncanny, Writers of the Future and the Nebulas go further. They reject any AI-written text, and some reject AI "assistance" of any kind.
9. US copyright protects what you write. AI-written passages must be disclaimed when they are more than trivial.
10. So editwright points at problems and explains them. You write every word. Your book stays yours under every rule above.

### Recommended default thresholds

Count "AI-written words" as words that came from a model and went into the manuscript unchanged. Words the author typed after reading a suggestion are the author's.

- Fiction: 0 AI-written words by default. Reasons: the SF and fantasy magazines, Writers of the Future and the Nebulas allow none, and some forbid AI help of any kind. The Human Authored "de minimis" allowance is undefined, so 0 is the only safe number. Mechanical fixes the author approves one at a time (spelling, punctuation, a missing word) can be allowed as a setting, since the Authors Guild and the Copyright Office's proofreading box both accept them. Warn the author that strict magazines may still count AI help.
- Nonfiction: a small allowance, defaulting to 1% of the manuscript's words, capped at 50 words per chapter, mechanical fixes only (spelling, grammar, punctuation, index and table-of-contents text). Reasons: KDP treats edit and error-check as "AI-assisted" with no disclosure. The Copyright Office needs a disclaimer only above de minimis. The Human Authored rule names grammar checkers and indices. The numbers are editwright's choice, not any policy's; no policy publishes a percentage.
- Both: log every accepted AI string with its location, so the author can answer a Copyright Office letter, a contract warranty or a detector dispute. Never paste model-written sentences into the manuscript without the author retyping or approving each word.

Related: none yet in this folder.
