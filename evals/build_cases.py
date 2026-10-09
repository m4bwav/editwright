"""Write the eval case folders for `claude plugin eval`. Run from the repository root after changing ew.py:

    python evals/build_cases.py

The story is invented. Bash cases (action-*, outcome-*) get a fixture.sh that writes the story, a
.editwright.json pointing the works store at ./editwright-works, and for the apply cases a ready job
made by the current ew.py (so the job format always matches the script)."""

import base64
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EW = ROOT / "skills" / "editwright" / "scripts" / "ew.py"
EVALS = ROOT / "evals"

STORY = """The Lighthouse Keeper's Daughter

Ines climbed the stairs of the lighthouse every night at nine. She counted them as she went, one hundred and twelve, and she never lost count, not once in eleven years.

Tonight she saw that the lamp room door was open. She felt a cold draft come down the stairwell and she felt her heart beat faster. Her father always shut that door. He shut it the way he shut everything, carefully and completely and with a small nod, as if the door had agreed to something.

"Papa?" she called up quietly. Nobody answered. The wind answered, the way it always did, with nothing useful to say.

At the top she found the lamp burning and the logbook open on the desk. The last entry was in her father's hand, dated tomorrow. Ines read it twice. Ships sighted: none. Weather: clearing. Keeper: absent.

Down below, on the rocks, Tomas was waiting for her. He knew what the entry meant before she did. He had always known teh things about the light that nobody told him.

She closed the logbook and sat down in her father's chair, and for the first time in eleven years she did not count anything at all.
"""

AI_PHRASE = "luminous cobalt shimmer"
SUGGESTIONS = [
    {"level": "proof", "category": "typo", "para": 6, "quote": "teh", "change": {"replace": "the"}, "problem": "Typo."},
    {"level": "line", "category": "adverb", "para": 4, "quote": " quietly", "change": {"replace": ""},
     "problem": "'Called up' already carries the distance; the adverb thins the line.", "severity": 1},
    {"level": "developmental", "category": "pov-slip", "para": 6, "quote": "He knew what the entry meant before she did.",
     "problem": "The story is close on Ines; this line jumps into Tomas's head.",
     "why": "A single slip breaks the closeness the opening built.", "options": ["Keep it in Ines's view: what she sees of him.", "Make the shift deliberate with a scene break."], "severity": 3},
    {"level": "line", "category": "image", "para": 5, "quote": "At the top she found the lamp burning",
     "change": {"replace": "At the top the lamp threw a %s" % AI_PHRASE}, "problem": "The lamp is plain at the story's key moment."},
    {"level": "line", "category": "filter-word", "para": 3, "quote": "She felt a cold draft come down the stairwell",
     "change": {"replace": "A cold draft came down the stairwell"}, "problem": "Filter verb distances the reader."},
]
JOB = "20261008-1-full"


def make_job_tarball():
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / "story.txt").write_text(STORY, encoding="utf-8", newline="\n")
        works = tmp / "editwright-works"
        run = lambda *a: subprocess.run([sys.executable, str(EW), "--works", str(works)] + list(a), cwd=tmp,
                                        check=True, capture_output=True, text=True, env={"EW_TODAY": "2026-10-08", **__import__("os").environ})
        run("intake", str(tmp / "story.txt"), "--work", "the-lighthouse", "--title", "The Lighthouse Keeper's Daughter",
            "--author", "Eval Author", "--genre", "short-story")
        job = next((works / "the-lighthouse" / "jobs").iterdir())
        job.rename(job.parent / JOB)
        (tmp / "s.json").write_text(json.dumps(SUGGESTIONS), encoding="utf-8")
        run("suggest", "the-lighthouse", str(tmp / "s.json"))
        jd = works / "the-lighthouse" / "jobs" / JOB
        for p in jd.rglob("*"):
            p.chmod(0o644)
        data = json.loads((jd / "job.json").read_text(encoding="utf-8"))
        data["source"]["path"] = "@@PWD@@/story.txt"
        data["source"]["mtime"] = 0
        (jd / "job.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as t:
            t.add(works, arcname="editwright-works")
        return base64.b64encode(buf.getvalue()).decode()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def fixture(with_job):
    lines = ["#!/usr/bin/env bash", "set -euo pipefail", "cat > story.txt <<'STORY_EOF'", STORY.rstrip("\n"), "STORY_EOF",
             "printf '{\"works\": \"editwright-works\"}\\n' > .editwright.json"]
    if with_job:
        lines += ["base64 -d > job.tgz <<'B64_EOF'", make_job_tarball(), "B64_EOF", "tar -xzf job.tgz && rm job.tgz",
                  "sed -i \"s#@@PWD@@#$PWD#\" editwright-works/the-lighthouse/jobs/%s/job.json" % JOB]
    return "\n".join(lines) + "\n"


SKILL_GRADER = "---\ntype: tool_used\ntool: Skill\ninput_match: '\"skill\"\\s*:\\s*\"(?:editwright:)?editwright\"'\n---\n"
NOT_SKILL = "---\ntype: tool_used\ntool: Skill\ninput_match: '\"skill\"\\s*:\\s*\"(?:editwright:)?editwright\"'\nmin: 0\nmax: 0\n---\n"
SOURCE_UNCHANGED = ("---\ntype: regex\nname: 'evidence: the source story is byte-for-byte as written (typo and adverb still there)'\n"
                    "target:\n  source: file\n  path: story.txt\npattern: 'known teh things[\\s\\S]*called up quietly|called up quietly[\\s\\S]*known teh things'\n---\n")


def tool(name, pattern, label, mn=None, mx=None):
    s = "---\ntype: tool_used\nname: '%s'\ntool: %s\ninput_match: '%s'\n" % (label, name, pattern)
    if mn is not None:
        s += "min: %d\nmax: %d\n" % (mn, mx)
    return s + "---\n"


def exists(path, yes, label):
    return "---\ntype: file_exists\nname: '%s'\npath: %s\nexists: %s\n---\n" % (label, path, "true" if yes else "false")


def regex_file(path, pattern, label, match=None):
    s = "---\ntype: regex\nname: '%s'\ntarget:\n  source: file\n  path: %s\npattern: '%s'\n" % (label, path, pattern)
    if match:
        s += "match: %s\n" % match
    return s + "---\n"


def regex_msg(pattern, label):
    return "---\ntype: regex\nname: '%s'\nflags: i\npattern: '%s'\n---\n" % (label, pattern)


def llm(criteria):
    return "---\ntype: llm\n---\n" + criteria + "\n"


JD = "editwright-works/the-lighthouse/jobs/%s" % JOB
CASES = {
    "trigger-1": ("Can you edit my short story? It's in ./drafts/lighthouse.md. I want to know what isn't working and get a proofread.", None, {"editwright": SKILL_GRADER}),
    "trigger-2": ("give me an editorial letter for chapter 3 of my novel, it's ~/novel/ch03.docx", None, {"editwright": SKILL_GRADER}),
    "trigger-3": ("proofread my essay before I send it to the magazine: ./essay.md", None, {"editwright": SKILL_GRADER}),
    "decoy-1": ("write me a short story about a lighthouse keeper who finds a message in a bottle", None, {"not-editwright": NOT_SKILL}),
    "decoy-2": ("humanize this, it reads like AI wrote it: \"In today's fast-paced world, leveraging synergies is crucial. Moreover, it is important to note that innovation drives growth.\"", None, {"not-editwright": NOT_SKILL}),
    "action-1": ("Line edit and proofread my short story ./story.txt. Give me your suggestions, but don't change anything yet.", False, {
        "editwright": SKILL_GRADER,
        "ran-intake": tool("Bash", "ew\\.py[\\s\\S]*\\bintake\\b", "evidence: ew.py intake ran"),
        "ran-suggest": tool("Bash", "ew\\.py[\\s\\S]*\\bsuggest\\b", "evidence: ew.py suggest ran"),
        "suggestions-file": exists("editwright-works/*/jobs/*/suggestions.json", True, "evidence: suggestion file written"),
        "ledger": exists("editwright-works/*/jobs/*/provenance-ledger.md", True, "evidence: provenance ledger written"),
        "nothing-applied": exists("editwright-works/*/jobs/*/edited*.md", False, "evidence: nothing applied without the author"),
        "check-passed": regex_file("editwright-works/last-check.txt", "^PASSED", "evidence: ew.py check passed"),
        "source-unchanged": SOURCE_UNCHANGED,
    }),
    "action-2": ("I read your suggestions for my lighthouse story. Apply S-004 please.", True, {
        "editwright": SKILL_GRADER,
        "ran-apply": tool("Bash", "ew\\.py[\\s\\S]*\\bapply\\b", "evidence: ew.py apply ran"),
        "no-edited-file": exists("editwright-works/*/jobs/*/edited*.md", False, "evidence: no edited file (S-004 brings in AI-written words)"),
        "told-why": regex_msg("limit|AI[- ]written|your own words|refus|human-authored", "reply explains the refusal"),
        "source-unchanged": SOURCE_UNCHANGED,
    }),
    "action-3": ("I read your suggestions for my lighthouse story. Apply S-001 and S-002, nothing else.", True, {
        "editwright": SKILL_GRADER,
        "ran-apply": tool("Bash", "ew\\.py[\\s\\S]*\\bapply\\b", "evidence: ew.py apply ran"),
        "both-applied": regex_file(JD + "/edited.md", "called up\\.\"?[\\s\\S]*known the things|known the things[\\s\\S]*called up\\.", "evidence: both accepted changes in edited.md"),
        "unaccepted-not-applied": regex_file(JD + "/edited.md", "%s|A cold draft came" % AI_PHRASE, "evidence: S-004 and S-005 (not accepted) absent", "not_contains"),
        "source-unchanged": SOURCE_UNCHANGED,
    }),
    "outcome-1": ("Here's a short story I wrote, ./story.txt. Edit it like a professional editor would and tell me what you'd change.", False, {
        "editwright": SKILL_GRADER,
        "source-unchanged": SOURCE_UNCHANGED,
        "nothing-applied": exists("editwright-works/*/jobs/*/edited*.md", False, "evidence: nothing applied without the author"),
        "diagnoses": llm("The final reply gives editorial feedback on the story: it names at least two concrete issues anchored to the text "
                         "(for example the typo 'teh', the point-of-view slip into Tomas's head in 'He knew what the entry meant before she did', "
                         "the repeated 'she felt', or the filter verbs 'saw'/'felt'), explains why they matter, and asks the author which suggestions "
                         "to accept. FAIL if the reply rewrites whole sentences or paragraphs of the story in new words, or presents a revised "
                         "version of the story."),
    }),
}


def main():
    for name, (prompt, job, graders) in CASES.items():
        d = EVALS / name
        if d.exists():
            shutil.rmtree(d)
        (d / "graders").mkdir(parents=True)
        (d / "prompt.md").write_text(prompt + "\n", encoding="utf-8", newline="\n")
        if job is not None:
            (d / "fixture.sh").write_text(fixture(job), encoding="utf-8", newline="\n")
            tags = ["bash"]
            (d / "case.yaml").write_text('schema_version: "1.1"\nname: %s\ntags: [%s]\ncontext:\n  scaffold_script: fixture.sh\n'
                                         % (name, ", ".join(tags)), encoding="utf-8", newline="\n")
        for g, body in graders.items():
            (d / "graders" / (g + ".md")).write_text(body, encoding="utf-8", newline="\n")
    print("wrote %d cases in %s" % (len(CASES), EVALS))


if __name__ == "__main__":
    main()
