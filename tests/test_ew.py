"""Tests for skills/editwright/scripts/ew.py. Run from the repository root: python tests/test_ew.py

Fixtures are invented text written at test time. Never commit a real manuscript."""

import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("ew", ROOT / "skills" / "editwright" / "scripts" / "ew.py")
ew = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ew)

STORY = (
    "CHAPTER ONE\n\n"
    "Mara saw the door open slowly.  She felt the cold air on her face -- it was very cold.\n"
    "She walked to the window. She walked to the door. \"Who's there?\" she whispered quietly.\n\n"
    "* * *\n\n"
    "The man said \"Nobody,\" and he was smiling. She realized teh man was her brother.\n"
)

SUGGESTIONS = [
    {"level": "proof", "category": "typo", "para": 5, "quote": "teh", "change": {"replace": "the"}, "problem": "Typo."},
    {"level": "line", "category": "filter-word", "para": 2, "quote": "Mara saw the door open",
     "change": {"replace": "The door opened"}, "problem": "Filter verb.", "options": ["Cut 'Mara saw'"]},
    {"level": "line", "category": "adverb", "para": 3, "quote": " quietly", "change": {"replace": ""},
     "problem": "Whispered already says it."},
    {"level": "developmental", "category": "stakes", "para": 5, "quote": "She realized teh man was her brother.",
     "problem": "The reveal has no setup.", "options": ["Plant him earlier"]},
    {"level": "line", "category": "verb", "para": 3, "quote": "She walked to the window.",
     "change": {"replace": "She drifted toward the window."}, "problem": "Flat verb."},
]


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = ew.main(list(argv))
        except SystemExit as e:
            code = e.code
    return code, out.getvalue() + err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.works = str(self.tmp / "works")
        self.src = self.tmp / "story.txt"
        self.src.write_text(STORY, encoding="utf-8")
        self.hash = ew.sha256_file(self.src)

    def tearDown(self):
        for p in self.tmp.rglob("*"):
            try:
                os.chmod(p, 0o666)
            except OSError:
                pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ew(self, *argv):
        return run("--works", self.works, *argv)

    def intake(self, genre="short-story", author="Test Author"):
        code, out = self.ew("intake", str(self.src), "--genre", genre, "--author", author, "--title", "The Door")
        self.assertEqual(code, 0, out)
        self.job = ew.resolve_job("story", self.works)
        return out

    def suggest(self, items=SUGGESTIONS):
        f = self.tmp / "s.json"
        f.write_text(json.dumps(items), encoding="utf-8")
        return self.ew("suggest", "story", str(f))


class TestCleanup(unittest.TestCase):
    def test_never_changes_a_word(self):
        samples = [STORY, "He said 'hi'.\r\nShe said \"bye\".\r\n", "word­break and​zero  width",
                   "Line one of a long hard\nwrapped paragraph that\ncontinues here.\n\nNext.", "\\*escaped\\* \\- text"]
        for s in samples:
            clean, _ = ew.cleanup(s)
            self.assertIsNone(ew.check_words_same(s, clean), s)

    def test_hard_wrap_joined_but_sentence_lines_kept(self):
        clean, _ = ew.cleanup("A sentence that wraps\nin the middle and\nends here.\n\nOne line.\nTwo line.\n")
        self.assertEqual(ew.paragraphs(clean), ["A sentence that wraps in the middle and ends here.", "One line.", "Two line."])

    def test_quotes_follow_dominant_style(self):
        clean, _ = ew.cleanup("“Hi,” she said. “It’s me.” He said \"no\".\n")
        self.assertNotIn('"', clean)
        clean, _ = ew.cleanup('"Hi," she said. "No," he said. “ok”\n')
        self.assertNotIn("“", clean)

    def test_scene_breaks_and_headings(self):
        clean, log = ew.cleanup("Chapter 2\n\ntext.\n\n***\n\nmore.\n")
        self.assertEqual(ew.paragraphs(clean), ["## Chapter 2", "text.", "* * *", "more."])

    def test_dashes(self):
        clean, _ = ew.cleanup("cold -- very cold\n")
        self.assertIn("cold—very", clean)


class TestProvenance(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(ew.provenance("teh", "the")["kind"], "correction")
        self.assertEqual(ew.provenance("she whispered quietly", "she whispered")["kind"], "cut")
        self.assertEqual(ew.provenance("quietly she went", "she went quietly")["kind"], "reorder")
        self.assertEqual(ew.provenance("Yes said she", "Yes, said she.")["kind"], "punctuation")
        p = ew.provenance("He went", "He sprinted away")
        self.assertEqual((p["kind"], p["new_word_count"]), ("new-words", 2))

    def test_irregular_forms_and_the_authors_word_nearby(self):
        # LEARNINGS L-001 corrections-of-own-words-counted-as-ai
        self.assertEqual(ew.provenance("Jane pauses and then says", "Jane paused and then said")["new_word_count"], 0)
        self.assertEqual(ew.provenance("They road on", "They rode on")["new_word_count"], 0)
        self.assertEqual(ew.provenance("are initializing", "were initializing")["new_word_count"], 0)
        nearby = {"planks", "bridge"}
        self.assertEqual(ew.provenance("light weight blanks", "light weight planks", nearby)["new_word_count"], 0)
        self.assertEqual(ew.provenance("light weight blanks", "light weight planks")["new_word_count"], 1)
        # a pure addition of a nearby word is still new: nothing was replaced
        self.assertEqual(ew.provenance("the bridge", "the long bridge", {"long"})["new_word_count"], 1)

    def test_echo_counts_copied_runs_of_common_words(self):
        s = {"quote": "He went home.", "options": ["something like: the way mules will go"]}
        self.assertEqual(ew.echoed_words(s, "He went home the way mules will."), ["the", "way", "mules", "will"])
        s = {"quote": "He went home.", "options": ["Use the past tense."]}
        self.assertEqual(ew.echoed_words(s, "He went to the shop."), [])

    def test_correction_needs_a_close_word(self):
        self.assertTrue(ew.is_correction("received", "recieved"))
        self.assertTrue(ew.is_correction("opened", "open"))
        self.assertFalse(ew.is_correction("dog", "cat"))
        self.assertFalse(ew.is_correction("talk", "walk"))


class TestJob(Base):
    def test_intake_snapshot_hash_and_files(self):
        out = self.intake()
        self.assertIn(self.hash, out)
        job = ew.load_job(self.job)
        self.assertEqual(job["source"]["sha256"], self.hash)
        self.assertEqual(ew.sha256_file(self.job / "source.txt"), self.hash)
        for f in ("clean.md", "cleanup-log.md", "job.json", "notes.md"):
            self.assertTrue((self.job / f).exists(), f)
        self.assertEqual(job["mode"], "human-authored")
        self.assertEqual(job["threshold"]["words"], 0)
        self.assertTrue((Path(self.works) / "story" / "style-sheet.md").exists())
        self.assertIn("backstory", (Path(self.works) / "story" / "story-bible.md").read_text(encoding="utf-8"))

    def test_check_passes_then_fails_when_source_changes(self):
        self.intake()
        self.assertEqual(self.ew("check", "story")[0], 0)
        self.src.write_text(STORY + "An added line.\n", encoding="utf-8")
        code, out = self.ew("check", "story")
        self.assertEqual(code, 1)
        self.assertIn("CHANGED", out)

    def test_check_against_fresh_export(self):
        self.intake()
        fresh = self.tmp / "fresh.txt"
        fresh.write_text(STORY.replace("\n", "\r\n"), encoding="utf-8")
        self.assertEqual(self.ew("check", "story", "--against", str(fresh))[0], 0)
        fresh.write_text(STORY.replace("brother", "sister"), encoding="utf-8")
        self.assertEqual(self.ew("check", "story", "--against", str(fresh))[0], 1)

    def test_suggest_rejects_bad_quotes(self):
        self.intake()
        code, out = self.suggest([{"level": "line", "category": "x", "para": 2, "quote": "not in text", "problem": "p"}])
        self.assertEqual(code, 1)
        self.assertIn("quote not found", out)
        data = json.loads((self.job / "suggestions.json").read_text(encoding="utf-8"))
        self.assertEqual(data["suggestions"], [])

    def test_suggest_saves_valid_items_and_resubmit_adds_only_fixed_ones(self):
        self.intake()
        bad = dict(SUGGESTIONS[1], quote="Mara saw the door opened")
        code, out = self.suggest([SUGGESTIONS[0], bad])
        self.assertEqual(code, 1)
        self.assertIn("item 2", out)
        code, out = self.suggest([SUGGESTIONS[0], SUGGESTIONS[1]])
        self.assertEqual(code, 0, out)
        self.assertIn("skipped 1", out)
        data = json.loads((self.job / "suggestions.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["suggestions"]), 2)

    def test_suggest_marks_ai_words(self):
        self.intake()
        code, out = self.suggest()
        self.assertEqual(code, 0, out)
        data = json.loads((self.job / "suggestions.json").read_text(encoding="utf-8"))
        marked = {s["id"]: s["ai_words"] for s in data["suggestions"] if s["marked_ai_text"]}
        self.assertEqual(marked, {"S-005": 2})
        for f in ("suggestions.md", "review.md", "provenance-ledger.md", "provenance.json"):
            self.assertTrue((self.job / f).exists(), f)
        self.assertIn("AI words: 2", (self.job / "suggestions.md").read_text(encoding="utf-8"))

    def test_apply_only_accepted_ids_into_a_new_file(self):
        self.intake()
        self.suggest()
        code, out = self.ew("apply", "story", "--accept", "S-001,S-003")
        self.assertEqual(code, 0, out)
        edited = (self.job / "edited.md").read_text(encoding="utf-8")
        self.assertIn("realized the man", edited)
        self.assertIn("she whispered.", edited)
        self.assertIn("Mara saw the door open", edited)  # S-002 not accepted, not applied
        changelog = (self.job / "edited-changelog.md").read_text(encoding="utf-8")
        self.assertIn("S-001", changelog)
        self.assertNotIn("S-002", changelog)
        self.assertEqual(ew.sha256_file(self.src), self.hash)
        self.assertEqual(self.ew("check", "story")[0], 0)

    def test_apply_refuses_when_the_source_changed(self):
        self.intake()
        self.suggest()
        self.src.write_text(STORY.replace("She realized teh man was her brother.", "She knew him at once."), encoding="utf-8")
        code, out = self.ew("apply", "story", "--accept", "S-001,S-003")
        self.assertEqual(code, 1, out)
        self.assertIn("source changed", out)
        self.assertIn("S-001: its quoted words are no longer in the source", out)
        self.assertIn("S-003: its quoted words are still in the source", out)
        self.assertFalse((self.job / "edited.md").exists())

    def test_apply_from_snapshot_says_so_in_the_changelog(self):
        self.intake()
        self.suggest()
        self.src.write_text(STORY + "\nA new last line.\n", encoding="utf-8")
        code, out = self.ew("apply", "story", "--accept", "S-001", "--from-snapshot")
        self.assertEqual(code, 0, out)
        self.assertIn("warning", out)
        self.assertNotIn("new last line", (self.job / "edited.md").read_text(encoding="utf-8"))
        self.assertIn("later edits are not in this file", (self.job / "edited-changelog.md").read_text(encoding="utf-8"))

    def test_apply_against_a_fresh_export(self):
        self.intake()
        self.suggest()
        fresh = self.tmp / "export.txt"
        fresh.write_text(STORY + "\nA new last line.\n", encoding="utf-8")
        self.assertEqual(self.ew("apply", "story", "--accept", "S-001", "--against", str(fresh))[0], 1)
        self.assertFalse((self.job / "edited.md").exists())

    def test_apply_allows_a_source_with_only_new_bytes(self):
        self.intake()
        self.suggest()
        (self.src).write_text(STORY + chr(10) * 2, encoding="utf-8")
        code, out = self.ew("apply", "story", "--accept", "S-001")
        self.assertEqual(code, 0, out)
        self.assertIn("words did not", out)

    def test_repeated_fix_listed_per_location_keeps_each_occurrence(self):
        self.src.write_text("A causal note and a causal look and a causal word.\n", encoding="utf-8")
        self.intake()
        items = [{"level": "copy", "category": "typo", "para": 1, "quote": "causal", "occurrence": n,
                  "change": {"replace": "casual"}, "problem": "Typo?"} for n in (1, 2, 3)]
        code, out = self.suggest(items)
        self.assertEqual(code, 0, out)
        ids = [s["id"] for s in ew.load_suggestions(self.job)["suggestions"]]
        self.assertEqual(len(ids), 3)
        code, out = self.ew("apply", "story", "--accept", ids[1])
        self.assertEqual(code, 0, out)
        self.assertEqual((self.job / "edited.md").read_text(encoding="utf-8").count("casual"), 1)

    def test_cleanup_reports_every_change_by_type(self):
        self.src.write_text('One -- two.\n\n\n\nThree went--\n\nFour  five.\n', encoding="utf-8")
        out = self.intake()
        log = (self.job / "cleanup-log.md").read_text(encoding="utf-8")
        self.assertIn("| extra blank lines removed | 1 |", log)
        self.assertIn("| double hyphens made em dashes | 2 |", log)
        self.assertIn("| runs of spaces inside lines made single | 1 |", log)
        self.assertIn("cleanup: double hyphens made em dashes: 2", out)
        self.assertIsNone(ew.check_words_same(self.src.read_text(encoding="utf-8"),
                                              (self.job / "clean.md").read_text(encoding="utf-8")))

    def test_apply_refuses_unknown_ids(self):
        self.intake()
        self.suggest()
        code, out = self.ew("apply", "story", "--accept", "S-001,S-042")
        self.assertEqual(code, 1)
        self.assertIn("S-042", out)
        self.assertFalse((self.job / "edited.md").exists())

    def test_apply_requires_explicit_ids(self):
        self.intake()
        self.suggest()
        self.assertNotEqual(self.ew("apply", "story")[0], 0)
        self.assertNotEqual(self.ew("apply", "story", "--accept", "all")[0], 0)

    def test_apply_refuses_ai_words_over_limit(self):
        self.intake()
        self.suggest()
        code, out = self.ew("apply", "story", "--accept", "S-001,S-005")
        self.assertEqual(code, 1)
        self.assertIn("over the limit", out)
        self.assertFalse((self.job / "edited.md").exists())

    def test_author_text_counts_as_author(self):
        self.intake()
        self.suggest()
        code, out = self.ew("apply", "story", "--accept", "S-005,S-004",
                            "--author-text", "S-005=She crossed to the window.",
                            "--author-text", "S-004=She knew him then: her brother.")
        self.assertEqual(code, 0, out)
        led = json.loads((self.job / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(led["applied"]["ai_words"], 0)
        self.assertEqual(sorted(led["applied"]["author_written_ids"]), ["S-004", "S-005"])

    def test_author_text_copying_the_suggestion_counts_as_ai(self):
        self.intake()
        self.suggest(SUGGESTIONS + [{"level": "line", "category": "verb", "para": 3, "quote": "She walked to the door.",
                                     "problem": "Flat.", "options": ["a verb with intent, such as stormed"]}])
        code, out = self.ew("apply", "story", "--accept", "S-006", "--author-text", "S-006=She stormed to the door.")
        self.assertEqual(code, 1, out)
        self.assertIn("over the limit", out)
        code, out = self.ew("apply", "story", "--accept", "S-006", "--author-text", "S-006=She marched to the door.")
        self.assertEqual(code, 0, out)

    def test_changelog_names_author_words_as_the_authors(self):
        self.intake()
        self.suggest()
        self.ew("apply", "story", "--accept", "S-004", "--author-text", "S-004=She knew him then: her brother.")
        log = (self.job / "edited-changelog.md").read_text(encoding="utf-8")
        row = [ln for ln in log.splitlines() if ln.startswith("| S-004")][0]
        self.assertIn("the author wrote", row)
        self.assertNotIn("AI-written", row)

    def test_refused_intake_leaves_nothing(self):
        pdf = self.tmp / "story.pdf"
        pdf.write_bytes(b"%PDF-1.4 not really")
        code, out = self.ew("intake", str(pdf), "--work", "pdfstory")
        self.assertNotEqual(code, 0)
        self.assertFalse((Path(self.works) / "pdfstory").exists())

    def test_query_without_author_text_refused(self):
        self.intake()
        self.suggest()
        code, out = self.ew("apply", "story", "--accept", "S-004")
        self.assertEqual(code, 1)
        self.assertIn("query", out)

    def test_nonfiction_allowance_and_override(self):
        self.intake(genre="nonfiction")
        self.suggest()
        self.assertEqual(self.ew("apply", "story", "--accept", "S-005")[0], 1)  # 2 words of 50 is 4%, over 1%
        self.assertNotEqual(self.ew("override", "story", "--reason", "ok")[0], 0)  # must quote the user
        self.assertEqual(self.ew("override", "story", "--reason", "user: rewrite it freely please")[0], 0)
        self.assertEqual(self.ew("apply", "story", "--accept", "S-005")[0], 0)
        notes = (self.job / "notes.md").read_text(encoding="utf-8")
        self.assertIn("OVERRIDE", notes)
        led = json.loads((self.job / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(led["applied"]["ai_words"], 2)

    def test_overlapping_changes_refused(self):
        self.intake()
        self.suggest(SUGGESTIONS + [{"level": "proof", "category": "x", "para": 5, "quote": "teh man",
                                     "change": {"replace": "the man"}, "problem": "p"}])
        code, out = self.ew("apply", "story", "--accept", "S-001,S-006")
        self.assertEqual(code, 1)
        self.assertIn("overlapping", out)

    def test_export_docx_has_tracked_changes_and_comments(self):
        self.intake()
        self.suggest()
        self.assertEqual(self.ew("export", "story")[0], 0)
        with zipfile.ZipFile(self.job / "review.docx") as z:
            doc = z.read("word/document.xml").decode("utf-8")
            com = z.read("word/comments.xml").decode("utf-8")
        self.assertIn("<w:ins ", doc)
        self.assertIn("<w:del ", doc)
        self.assertIn("S-004", com)
        self.assertEqual(com.count("<w:comment "), 5)

    def test_feedback_updates_author_preferences(self):
        self.intake()
        self.suggest()
        code, out = self.ew("feedback", "story", "--accepted", "S-001", "--rejected", "S-002,S-005")
        self.assertEqual(code, 0, out)
        prefs = json.loads((Path(self.works) / "authors" / "test-author.json").read_text(encoding="utf-8"))
        self.assertEqual(prefs["categories"]["typo"]["accepted"], 1)
        self.assertEqual(prefs["categories"]["filter-word"]["rejected"], 1)
        self.assertTrue((Path(self.works) / "authors" / "test-author.md").exists())

    def test_chunk_and_show(self):
        long = "\n\n".join("## Chapter %d\n\n%s" % (i, " ".join(["word"] * 900)) for i in range(1, 6))
        self.src.write_text(long, encoding="utf-8")
        self.intake(genre="novel")
        self.assertEqual(self.ew("chunk", "story", "--max-words", "2000", "--min-words", "500")[0], 0)
        self.assertTrue((self.job / "chunks" / "INDEX.md").exists())
        self.assertGreaterEqual(len(list((self.job / "chunks").glob("0*.md"))), 3)
        code, out = self.ew("show", "story", "--para", "1-1")
        self.assertIn("[P1] ## Chapter 1", out)

    def test_stats_counts(self):
        self.intake()
        st = ew.text_stats((self.job / "clean.md").read_text(encoding="utf-8"))
        self.assertEqual(st["filter_words"]["count"], 3)
        self.assertEqual(st["ly_adverbs"]["count"], 2)
        self.assertEqual(st["was_ing"], 1)

    def test_look_lists_fire_on_bad_text(self):
        long = " ".join(["word"] * 300)
        paras = ["# One", "Disappearing into my tent, I changed my shirt.", "She was angry and afraid!",
                 "As the door closed, he ran.", long, "# Two", "x " * 500, "# Three", "y " * 20]
        lk = ew.look_lists(paras)
        self.assertEqual(lk["ing_as_openers"]["paras"], [2, 4])
        self.assertEqual(lk["exclamations_in_narration"], [3])
        self.assertEqual(lk["named_emotions_in_narration"]["count"], 2)
        self.assertEqual(lk["paragraphs_over_half_page"], [5])
        self.assertEqual(lk["paragraphs_over_a_page"], [7])
        self.assertFalse(lk["chapter_words"]["all_same_length"])

    def test_look_lists_quiet_on_good_text(self):
        paras = ["# One", "Nothing moved, so she waited.", "“I am so angry!” he said.",
                 "He pulled off his gloves and turned.", "# Two", "a " * 18, "# Three", "b " * 19]
        lk = ew.look_lists(paras)
        self.assertEqual(lk["ing_as_openers"]["count"], 0)
        self.assertEqual(lk["exclamations_in_narration"], [])
        self.assertEqual(lk["named_emotions_in_narration"]["count"], 0)
        self.assertEqual(lk["paragraphs_over_half_page"] + lk["paragraphs_over_a_page"], [])
        self.assertTrue(lk["chapter_words"]["all_same_length"])
        self.assertEqual(ew.look_lists(["One paragraph."])["ing_as_openers"]["count"], 0)
        self.assertNotIn("chapter_words", ew.look_lists(["# A", "x", "# B", "y"]))

    def test_clarity_lists_fire_on_zombie_prose(self):
        paras = ["# Report",
                 "The committee made a decision about the implementation of the arrangement after consideration.",
                 "We will carry out an evaluation of the proposal.",
                 "She walked to the station and read the document."]
        cl = ew.clarity_lists(paras)
        self.assertEqual(cl["nominalisations"]["dense_paras"], [2])
        self.assertEqual(cl["light_verb_pairs"]["count"], 2)
        self.assertIn("made a decision", cl["light_verb_pairs"]["examples"])
        self.assertIn("carry out an evaluation", cl["light_verb_pairs"]["examples"])
        # station and document are on the exception list; "implementation" counted, heading skipped
        top = dict(cl["nominalisations"]["top"])
        self.assertNotIn("station", top)
        self.assertNotIn("document", top)
        self.assertEqual(top["implementation"], 1)

    def test_clarity_lists_quiet_on_plain_prose(self):
        paras = ["The committee decided to build it after thinking it over.",
                 "Give the chosen rule a name. Make reference images first.",
                 "See [the notes](ai-docs/decisions/implementation-and-consideration.md) and `evaluation()`.",
                 "STATEMENT OF THE CONSIDERATION AND DETERMINATION OF JURISDICTION",
                 "Smith said: \"the implementation of the arrangement after consideration\"."]
        cl = ew.clarity_lists(paras)
        self.assertEqual(cl["light_verb_pairs"]["count"], 0)
        self.assertEqual(cl["nominalisations"]["dense_paras"], [])
        # only "reference" in plain prose counts; links, code, the shouted caption and the quote do not
        self.assertEqual(cl["nominalisations"]["top"], [("reference", 1)])

    def test_structure_lists_maps_over_four(self):
        paras = ["The appeal raises five issues: standing, bias, merger, classes and mootness.",
                 "There are three reasons.", "Slope over the last eight points is shown.",
                 "## Six principles"]
        st = ew.structure_lists(paras)
        self.assertEqual(st["maps_over_four"], [{"para": 1, "text": "five issues"}])

    def test_stats_prints_clarity_and_structure(self):
        f = self.tmp / "memo.md"
        f.write_text("We made a decision on the termination of the agreement after negotiation.\n\n"
                     "The client faces six risks.\n", encoding="utf-8")
        code, out = self.ew("stats", str(f))
        self.assertEqual(code, 0, out)
        self.assertIn("light verb + noun 1 (made a decision)", out)
        self.assertIn("announced lists over four items P2 six risks", out)

    def test_bridges_fire_on_unlinked_openers_and_stay_quiet_on_linked(self):
        linked = ["The court read the contract narrowly.",
                  "That reading left the tenant without a remedy.",
                  "But the tenant had paid the deposit in full.",
                  "The deposit is the heart of the dispute."]
        br = ew.bridge_lists(linked)
        self.assertEqual((br["openers"], br["bridged"], br["no_bridge_paras"]), (3, 3, []))
        loose = ["The court read the contract narrowly.", "Rainfall in March was heavy.",
                 "## Next part", "Parking near the station costs more.", "Owls hunt at night."]
        br = ew.bridge_lists(loose)
        self.assertEqual((br["openers"], br["bridged"], br["percent"], br["no_bridge_paras"]), (2, 0, 0, [2, 5]))

    def test_stats_prints_bridges_and_show_firsts(self):
        f = self.tmp / "essay.md"
        f.write_text("Cats sleep a lot. They wake at dusk.\n\nRain fell on the town. Roads flooded.\n", encoding="utf-8")
        code, out = self.ew("stats", str(f))
        self.assertIn("bridged openers (nonfiction): 0 of 1 (0%), under a third; no link back in P2", out)
        self.intake()
        code, out = self.ew("show", "story", "--firsts", "--para", "2")
        self.assertEqual(code, 0, out)
        self.assertIn("[P2] Mara saw the door open slowly.", out)
        self.assertNotIn("cold air", out)

    def test_bracket_is_a_zero_word_cut_shown_in_brackets(self):
        self.intake()
        items = [{"level": "line", "category": "clutter", "para": 3, "quote": " quietly", "bracket": True,
                  "problem": "Whispered already says it."}]
        code, out = self.suggest(items)
        self.assertEqual(code, 0, out)
        s = ew.load_suggestions(self.job)["suggestions"][0]
        self.assertEqual((s["ai_words"], s["change"]), (0, {"replace": ""}))
        self.assertIn("she whispered[ quietly]{>>S-001", (self.job / "review.md").read_text(encoding="utf-8"))
        self.assertIn("Read it without the brackets", (self.job / "suggestions.md").read_text(encoding="utf-8"))
        code, out = self.ew("apply", "story", "--accept", "S-001")
        self.assertEqual(code, 0, out)
        self.assertIn("she whispered.", (self.job / "edited.md").read_text(encoding="utf-8"))
        bad = [{"level": "line", "category": "clutter", "para": 2, "quote": "slowly", "bracket": True,
                "change": {"replace": "fast"}, "problem": "x"}]
        code, out = self.suggest(bad)
        self.assertEqual(code, 1)
        self.assertIn("a bracket is a cut", out)

    def test_docx_source(self):
        d = self.tmp / "story.docx"
        ew.write_docx(d, ["## Chapter 1", "It was dark.", "She waited."])
        code, out = self.ew("intake", str(d), "--work", "docstory")
        self.assertEqual(code, 0, out)
        job = ew.resolve_job("docstory", self.works)
        self.assertEqual(ew.paragraphs((job / "clean.md").read_text(encoding="utf-8")),
                         ["## Chapter 1", "It was dark.", "She waited."])


if __name__ == "__main__":
    unittest.main(verbosity=1)
