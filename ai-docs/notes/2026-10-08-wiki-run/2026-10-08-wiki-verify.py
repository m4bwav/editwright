"""Verification program for the editwright wiki (editwright 0.1.0, tag v0.1.0).

Runs every command the wiki shows against the released ew.py, in a fresh /tmp/demo folder,
with an invented story and essay and a works store inside that folder (--works works).
HOME is pointed into the demo folder too, so no real works store or config is read.

Usage (Linux or WSL): python3 wiki-verify.py <released skills/editwright/scripts/ew.py> [<release checkout>]
Each case prints "=== label", then "$ command", the merged stdout and stderr, then "$ echo $?" and the exit code.
"""
import os
import shutil
import subprocess
import sys

DEMO = "/tmp/demo"

STORY = """# The Salt Road

Nell had walked the salt road every morning for nine years. She knew
where the ruts ran deep and where the gulls waited for scraps.

"You're late," said her brother when she reached the gate.

"The tide was high," Nell said. "I had to go round by the old mill."

She saw the cart standing empty by the well. Nobody had unloaded teh barrels, and the mule was gone.

***

By noon the village was talking. Some said the mule had wandered off, as mules do. Others said a stranger
had come in the night and taken it.

Nell walks to the well again and looked at the cart. The axle was cracked. Someone had driven it hard, very hard, and
then left it.

She realized the stranger was her cousin.
"""

ESSAY = """# Reading a tide table

A tide table lists the times of high and low water for one place. Each row gives a date, a time and a height. The height is measured from a fixed level called chart datum, which is close to the lowest tide of the year.

Tides do not keep the same clock as the sun. High water comes about fifty minutes later each day, because the moon rises later each day. Two high tides a day is the common pattern on the Atlantic coast, but some places get only one.

A table is a prediction, not a promise. Wind and air pressure can push the water higher or hold it back. A strong onshore wind can raise the sea by a foot or more. Read the table, then look at the water.
"""

SUGGESTIONS = """[
  {
    "level": "proof",
    "category": "typo",
    "para": 5,
    "quote": "teh",
    "change": {"replace": "the"},
    "problem": "Typo."
  },
  {
    "level": "line",
    "category": "repetition",
    "para": 8,
    "quote": "very hard, ",
    "change": {"replace": ""},
    "problem": "The repeat softens the sentence instead of stressing it.",
    "why": "The cracked axle already shows how hard the cart was driven.",
    "options": ["Cut the repeat.", "Keep it if Nell's voice leans on repeats elsewhere."],
    "severity": 1
  },
  {
    "level": "copy",
    "category": "tense",
    "para": 8,
    "quote": "walks",
    "change": {"replace": "walked"},
    "problem": "Tense slip: the story is told in the past tense."
  },
  {
    "level": "line",
    "category": "rhythm",
    "para": 7,
    "quote": "as mules do",
    "change": {"replace": "the way mules will"},
    "problem": "The aside is flat.",
    "severity": 1
  },
  {
    "level": "developmental",
    "category": "stakes",
    "para": 9,
    "quote": "She realized the stranger was her cousin.",
    "problem": "The reveal has no setup, so it reads as coincidence.",
    "why": "Readers accept a surprise they could have seen coming.",
    "options": ["Plant the cousin earlier in the story.", "Move the reveal so the reader learns it with Nell."],
    "severity": 3
  },
  {
    "level": "copy",
    "category": "punctuation",
    "para": 8,
    "quote": "hard, very",
    "change": {"replace": "hard. Very"},
    "problem": "A full stop would give the repeat its own beat."
  }
]
"""

BAD = """[
  {
    "level": "line",
    "category": "filter-word",
    "quote": "She saw the cart standing empty by the barn.",
    "problem": "Filter verb."
  }
]
"""

ESSAY_SUGGESTIONS = """[
  {
    "level": "line",
    "category": "clarity",
    "para": 3,
    "quote": "Two high tides a day is the common pattern",
    "change": {"replace": "Two high tides a day is the most common pattern"},
    "problem": "The comparison is missing."
  },
  {
    "level": "line",
    "category": "clarity",
    "para": 4,
    "quote": "Read the table, then look at the water.",
    "change": {"replace": "Read the table first, and then always go and look at the water."},
    "problem": "The close is abrupt."
  }
]
"""

# (label, command). The wiki shows these commands exactly as written here.
CASES = [
    ("version", "python3 ew.py --version"),
    ("intake", 'python3 ew.py --works works intake story.md --work the-salt-road --title "The Salt Road" --author "Test Author" --genre short-story --level full'),
    ("cleanup-log", "cat works/the-salt-road/jobs/*/cleanup-log.md"),
    ("show", "python3 ew.py --works works show the-salt-road"),
    ("show-range", "python3 ew.py --works works show the-salt-road --para 7-8"),
    ("stats", "python3 ew.py --works works stats the-salt-road"),
    ("stats-file", "python3 ew.py stats story.md"),
    ("suggest-bad", "python3 ew.py --works works suggest the-salt-road bad.json"),
    ("suggest", "python3 ew.py --works works suggest the-salt-road suggestions.json"),
    ("suggestions-md", "cat works/the-salt-road/jobs/*/suggestions.md"),
    ("review-md", "cat works/the-salt-road/jobs/*/review.md"),
    ("ledger-md", "cat works/the-salt-road/jobs/*/provenance-ledger.md"),
    ("ledger", "python3 ew.py --works works ledger the-salt-road"),
    ("ledger-accept-ok", "python3 ew.py --works works ledger the-salt-road --accept S-001,S-003"),
    ("ledger-accept-over", "python3 ew.py --works works ledger the-salt-road --accept S-004"),
    ("apply-none", "python3 ew.py --works works apply the-salt-road"),
    ("apply-unknown", "python3 ew.py --works works apply the-salt-road --accept S-009"),
    ("apply-query", "python3 ew.py --works works apply the-salt-road --accept S-005"),
    ("apply-overlap", "python3 ew.py --works works apply the-salt-road --accept S-002,S-006"),
    ("apply-ai", "python3 ew.py --works works apply the-salt-road --accept S-004"),
    ("apply-echo", 'python3 ew.py --works works apply the-salt-road --accept S-004 --author-text S-004="the way mules will"'),
    ("apply", 'python3 ew.py --works works apply the-salt-road --accept S-001,S-002,S-003,S-005 --author-text S-005="She knew then that the stranger was her cousin."'),
    ("edited-md", "cat works/the-salt-road/jobs/*/edited.md"),
    ("changelog-md", "cat works/the-salt-road/jobs/*/edited-changelog.md"),
    ("ledger-after", "python3 ew.py --works works ledger the-salt-road"),
    ("export", "python3 ew.py --works works export the-salt-road"),
    ("docx-parts", "python3 -c \"import zipfile, glob; print('\\n'.join(zipfile.ZipFile(glob.glob('works/the-salt-road/jobs/*/review.docx')[0]).namelist()))\""),
    ("docx-marks", "python3 -c \"import zipfile, glob, re; x = zipfile.ZipFile(glob.glob('works/the-salt-road/jobs/*/review.docx')[0]).read('word/document.xml').decode(); print(len(re.findall('<w:ins ', x)), 'insertions,', len(re.findall('<w:del ', x)), 'deletions')\""),
    ("feedback", 'python3 ew.py --works works feedback the-salt-road --accepted S-001,S-002,S-003,S-005 --rejected S-004,S-006 --note "Liked the cuts; leave the asides alone."'),
    ("author", 'python3 ew.py --works works author "Test Author"'),
    ("override-short", 'python3 ew.py --works works override the-salt-road --reason "go ahead"'),
    ("override", 'python3 ew.py --works works override the-salt-road --reason "rewrite it freely, this one is a practice piece"'),
    ("apply-overridden", "python3 ew.py --works works apply the-salt-road --accept S-004"),
    ("override-off", "python3 ew.py --works works override the-salt-road --off"),
    ("status", "python3 ew.py --works works status the-salt-road"),
    ("render", "python3 ew.py --works works render the-salt-road"),
    ("chunk", "python3 ew.py --works works chunk the-salt-road --max-words 60 --min-words 20"),
    ("chunk-index", "cat works/the-salt-road/jobs/*/chunks/INDEX.md"),
    ("check", "python3 ew.py --works works check the-salt-road"),
    ("check-against", "sed 's/$/\\r/' story.md > export.txt && python3 ew.py --works works check the-salt-road --against export.txt"),
    ("check-changed", "echo 'A new last line.' >> story.md && python3 ew.py --works works check the-salt-road"),
    ("apply-docx", "python3 ew.py --works works apply the-salt-road --accept S-001 --docx && ls works/the-salt-road/jobs/*/ | grep edited-3"),
    ("intake-essay", "python3 ew.py --works works intake essay.md --genre nonfiction --level line"),
    ("essay-suggest", "python3 ew.py --works works suggest essay essay-suggestions.json"),
    ("essay-ledger-1", "python3 ew.py --works works ledger essay --accept S-001"),
    ("essay-ledger-2", "python3 ew.py --works works ledger essay --accept S-001,S-002"),
    ("intake-pdf", "touch book.pdf && python3 ew.py --works works intake book.pdf"),
    ("intake-text", "touch essay.pdf && cp essay.md extracted.md && python3 ew.py --works works intake essay.pdf --text extracted.md --work essay-pdf --genre nonfiction"),
    ("provenance", "python3 -c \"import ew; print(ew.provenance('do not', 'don’t')); print(ew.provenance('hat', 'hot')); print(ew.provenance('the dog barked', 'the dog growled'))\""),
    ("no-job", "python3 ew.py --works works show no-such-work"),
    ("env-works", 'EDITWRIGHT_WORKS=works python3 ew.py author "Test Author" | head -1'),
    ("config-works", """mkdir -p cfg && cd cfg && echo '{"works": "../works"}' > .editwright.json && python3 ../ew.py author "Test Author" | head -1"""),
    ("default-works", 'python3 ew.py author "Test Author"'),
    ("store", "find works | sort"),
]


# Run in the release checkout when its path is given as the second argument.
REPO_CASES = [
    ("repo-tests", "python3 tests/test_ew.py"),
    ("repo-budget", "python3 scripts/budget.py"),
    ("repo-package", "python3 scripts/package.py"),
]


def main():
    ew = sys.argv[1]
    shutil.rmtree(DEMO, ignore_errors=True)
    os.makedirs(DEMO + "/home")
    for name, text in (("story.md", STORY), ("essay.md", ESSAY), ("suggestions.json", SUGGESTIONS), ("bad.json", BAD),
                       ("essay-suggestions.json", ESSAY_SUGGESTIONS)):
        with open(os.path.join(DEMO, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    shutil.copy(ew, DEMO + "/ew.py")
    env = {k: v for k, v in os.environ.items() if not k.startswith("EDITWRIGHT")}
    env["HOME"] = DEMO + "/home"
    print("=== installed")
    print(subprocess.run(["python3", "--version"], capture_output=True, text=True).stdout.strip())
    for label, cmd in CASES:
        r = subprocess.run(["bash", "-c", cmd + " 2>&1"], cwd=DEMO, env=env, capture_output=True, text=True, encoding="utf-8")
        print("=== " + label)
        print("$ " + cmd)
        print(r.stdout.rstrip("\n"))
        print("$ echo $?")
        print(r.returncode)
    if len(sys.argv) > 2:
        for label, cmd in REPO_CASES:
            r = subprocess.run(["bash", "-c", cmd + " 2>&1"], cwd=sys.argv[2], capture_output=True, text=True, encoding="utf-8")
            print("=== " + label)
            print("$ " + cmd)
            print(r.stdout.rstrip(chr(10)))
            print("$ echo $?")
            print(r.returncode)


if __name__ == "__main__":
    main()
