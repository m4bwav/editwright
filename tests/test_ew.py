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
        self.assertFalse((self.job / "suggestions.json").exists())

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
