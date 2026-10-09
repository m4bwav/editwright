#!/usr/bin/env python3
"""editwright CLI: the mechanical, checkable half of editing a manuscript.

Standard library only, Python 3.9 or newer, UTF-8 in and out. The model does the judgment
(what is wrong and why); this script does everything that is counting or bookkeeping:
intake and hashing, word-safe cleanup with its log, paragraph numbers, chunks, counts,
the suggestion file, the provenance ledger, apply with its changelog, and the check that
the author's source never changed.

Run `ew.py -h` or `ew.py <command> -h`. Exit codes: 0 ok, 1 a check failed or a request
was refused, 2 usage error.
"""

import argparse
import collections
import datetime
import hashlib
import html
import json
import math
import os
import re
import shutil
import statistics
import sys
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

VERSION = "0.1.1"

# Default limits on AI-written words that apply may bring in while human-authored mode is on.
# Reasons: ai-docs/decisions (word thresholds). Fiction, poetry and scripts: none at all.
# Nonfiction: a small allowance for connective fixes, capped in absolute words.
THRESHOLDS = {
    "fiction": {"words": 0, "percent": 0.0},
    "short-story": {"words": 0, "percent": 0.0},
    "novel": {"words": 0, "percent": 0.0},
    "poetry": {"words": 0, "percent": 0.0},
    "script": {"words": 0, "percent": 0.0},
    "nonfiction": {"words": 50, "percent": 1.0},
    "other": {"words": 0, "percent": 0.0},
}
GENRES = sorted(THRESHOLDS)
LEVELS = ["developmental", "assessment", "line", "copy", "proof", "fact"]
TEXT_EXTS = {".md", ".markdown", ".txt", ".text", ".fountain", ".rst"}

WORD_RE = re.compile(r"[^\W_]+(?:['’\-][^\W_]+)*", re.UNICODE)
INVISIBLE = dict.fromkeys(map(ord, "­​‌‍⁠﻿"), None)
SCENE_BREAK_RE = re.compile(r"^\s*(?:\*\s*){3,}$|^\s*(?:#\s*){1,3}$|^\s*(?:~\s*){3,}$|^\s*(?:-\s*){3,}$|^\s*(?:•\s*){3,}$")
CHAPTER_RE = re.compile(r"^(?:chapter|part|book|prologue|epilogue|interlude|act|scene)\b[\w .:—–'’-]{0,60}$", re.I)

STOP = set("""a about above after again against all am an and any are as at be because been before being below
between both but by can could did do does doing down during each few for from further had has have having he her
here hers herself him himself his how i if in into is it its itself just me more most my myself no nor not now of off
on once only or other our ours ourselves out over own same she should so some such than that the their theirs them
themselves then there these they this those through to too under until up very was we were what when where which while
who whom why will with would you your yours yourself yourselves said says say like one two back get got go went
""".split())
FILTER_WORDS = ["saw", "see", "sees", "seeing", "heard", "hear", "hears", "felt", "feel", "feels", "noticed", "notice",
                "realized", "realised", "realize", "seemed", "seem", "seems", "watched", "watch", "wondered", "wonder",
                "thought", "knew", "decided", "looked", "smelled", "tasted", "observed"]
CRUTCH_WORDS = ["very", "really", "just", "suddenly", "quite", "rather", "somehow", "almost", "nearly", "simply",
                "actually", "basically", "literally", "that", "then", "began", "started"]
LY_EXCEPT = set("""only family early reply apply supply july italy fly holy ugly belly jelly bully lily rely ally
silly hilly chilly daily lonely lovely friendly likely ugly costly elderly curly surly folly melancholy""".split())
TAG_VERBS = set("""said says asked asks replied whispered shouted yelled muttered murmured snapped hissed growled
exclaimed cried called answered added continued sighed laughed breathed barked snarled gasped""".split())


# ---------------------------------------------------------------- basics

def now_iso():
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def today():
    return os.environ.get("EW_TODAY") or datetime.date.today().isoformat()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read_text(p):
    return Path(p).read_text(encoding="utf-8")


def write_text(p, s):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def load_json(p, default=None):
    p = Path(p)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def save_json(p, data):
    write_text(p, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "untitled"


def words(s):
    return WORD_RE.findall(s.translate(INVISIBLE))


def norm_word(w):
    return w.casefold().replace("’", "'")


def word_key(s):
    return [norm_word(w) for w in words(s)]


def fail(msg, code=1):
    print("editwright: " + msg, file=sys.stderr)
    raise SystemExit(code)


# ---------------------------------------------------------------- works store and jobs

def config_path():
    return Path(os.environ.get("EDITWRIGHT_CONFIG") or Path.home() / ".editwright.json")


def works_root(arg=None):
    """--works, then $EDITWRIGHT_WORKS, then 'works' in ./.editwright.json or the user config, then ~/editwright-works.
    A relative 'works' in ./.editwright.json is taken from the current folder."""
    if arg:
        return Path(arg).expanduser()
    if os.environ.get("EDITWRIGHT_WORKS"):
        return Path(os.environ["EDITWRIGHT_WORKS"]).expanduser()
    for cfg_file in (Path.cwd() / ".editwright.json", config_path()):
        cfg = load_json(cfg_file, {}) or {}
        if cfg.get("works"):
            w = Path(cfg["works"]).expanduser()
            return w if w.is_absolute() else (cfg_file.parent / w)
    return Path.home() / "editwright-works"


def resolve_job(ref, works=None):
    """A job folder from a path, '<work>/<job>', or '<work>' (its latest job)."""
    candidates = [Path(ref).expanduser(), works_root(works) / ref]
    for c in candidates:
        if (c / "job.json").exists():
            return c.resolve()
        if (c / "jobs").is_dir():
            jobs = sorted(d for d in (c / "jobs").iterdir() if (d / "job.json").exists())
            if jobs:
                return jobs[-1].resolve()
    fail("no job found for %r (looked in %s)" % (ref, ", ".join(str(c) for c in candidates)))


def load_job(jdir):
    return load_json(Path(jdir) / "job.json")


def save_job(jdir, job):
    save_json(Path(jdir) / "job.json", job)


def append_note(jdir, line):
    p = Path(jdir) / "notes.md"
    old = read_text(p) if p.exists() else "# Job notes\n\n"
    write_text(p, old + "- %s %s\n" % (now_iso(), line))


# ---------------------------------------------------------------- reading sources

def decode_bytes(b):
    for enc in ("utf-8-sig", "utf-16"):
        if enc == "utf-16" and not (b[:2] in (b"\xff\xfe", b"\xfe\xff")):
            continue
        try:
            return b.decode(enc), enc
        except UnicodeDecodeError:
            pass
    try:
        return b.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return b.decode("cp1252", errors="replace"), "cp1252"


W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def docx_text(path):
    """Paragraph text of a .docx (body only; tracked insertions kept, deletions dropped)."""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    out = []
    for p in root.iter(W_NS + "p"):
        style = p.find("%spPr/%spStyle" % (W_NS, W_NS))
        level = 0
        if style is not None:
            m = re.match(r"(?i)heading\s*(\d)|title", style.get(W_NS + "val", ""))
            if m:
                level = int(m.group(1)) if m.group(1) else 1
        buf = []
        for el in p.iter():
            if el.tag == W_NS + "t":
                buf.append(el.text or "")
            elif el.tag == W_NS + "tab":
                buf.append("\t")
            elif el.tag in (W_NS + "br", W_NS + "cr"):
                buf.append("\n")
        text = "".join(buf)
        if level and text.strip():
            text = "#" * min(level, 6) + " " + text.strip()
        out.append(text)
    return "\n\n".join(out) + "\n", "docx"


def source_text(path, text_from=None):
    path = Path(path)
    if text_from:
        t, enc = decode_bytes(Path(text_from).read_bytes())
        return t, "text from %s (%s)" % (Path(text_from).name, enc)
    ext = path.suffix.lower()
    if ext == ".docx":
        t, how = docx_text(path)
        return t, "docx paragraphs (built-in reader)"
    if ext in TEXT_EXTS or ext == "":
        t, enc = decode_bytes(path.read_bytes())
        return t, "text (%s)" % enc
    fail("cannot read %s files directly; extract the text first (readwright: rw.py read FILE --out text.md) "
         "and pass it with --text" % ext)


# ---------------------------------------------------------------- cleanup (never changes a word)

def smart_quotes(s):
    out = []
    for i, ch in enumerate(s):
        prev = s[i - 1] if i else " "
        nxt = s[i + 1] if i + 1 < len(s) else " "
        if ch == '"':
            out.append("“" if (prev.isspace() or prev in "([{—–-/") and not nxt.isspace() else "”")
        elif ch == "'":
            if prev.isalnum() or prev in ".,!?”":
                out.append("’")
            elif re.match(r"(?:tis|twas|em|cause|til|n|round|bout|\d\d)\b", s[i + 1:i + 6], re.I):
                out.append("’")
            elif prev.isspace() or prev in "([{—–“-" or i == 0:
                out.append("‘")
            else:
                out.append("’")
        else:
            out.append(ch)
    return "".join(out)


def straight_quotes(s):
    return s.translate({0x201c: '"', 0x201d: '"', 0x2018: "'", 0x2019: "'"})


class CleanLog:
    def __init__(self):
        self.rows = collections.OrderedDict()

    def add(self, rule, count, example=""):
        if count:
            r = self.rows.setdefault(rule, [0, []])
            r[0] += count
            if example and len(r[1]) < 3:
                r[1].append(example)

    def markdown(self, meta):
        lines = ["# Cleanup log", "",
                 "Mechanical cleanup from the source snapshot to clean.md. No word was added, removed or changed: "
                 "the word sequence check passed (%s words)." % meta["words"], "",
                 "Source read as: %s." % meta["read_as"], "",
                 "| Rule | Changes | Examples |", "|---|---|---|"]
        if not self.rows:
            lines.append("| (none) | 0 | |")
        for rule, (n, ex) in self.rows.items():
            lines.append("| %s | %d | %s |" % (rule, n, "; ".join(e.replace("|", "\\|") for e in ex)))
        return "\n".join(lines) + "\n"


def dominant_quotes(s):
    curly = sum(s.count(c) for c in "“”‘’")
    straight = s.count('"') + len(re.findall(r"(?<![A-Za-z])'|'(?![A-Za-z])", s))
    return "curly" if curly >= straight else "straight"


def cleanup(text, quotes="auto", dashes="auto", keep_lines=False, headings=True):
    log = CleanLog()
    t = text
    n = t.count("\r")
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    log.add("line endings to LF", n)
    inv = sum(t.count(chr(c)) for c in INVISIBLE)
    t = t.translate(INVISIBLE)
    log.add("invisible characters removed (soft hyphen, zero-width, BOM)", inv)
    nf = unicodedata.normalize("NFC", t)
    log.add("Unicode NFC normalisation", sum(1 for a, b in zip(t, nf) if a != b) + abs(len(t) - len(nf)))
    t = nf
    for ch, name in ((" ", "no-break space"), (" ", "thin space"), (" ", "narrow no-break space"), ("\t", "tab")):
        c = t.count(ch)
        t = t.replace(ch, " ")
        log.add("%s to space" % name, c)
    # Google Docs and some exporters escape markdown punctuation.
    esc = re.findall(r"\\([\\`*_{}\[\]()#+\-.!>~|])", t)
    t = re.sub(r"\\([\\`*_{}\[\]()#+\-.!>~|])", r"\1", t)
    log.add("markdown escapes removed (\\* \\_ \\- ...)", len(esc))
    lines = t.split("\n")
    stripped = [ln.rstrip(" ") for ln in lines]
    log.add("trailing spaces removed", sum(1 for a, b in zip(lines, stripped) if a != b))
    lead = [re.sub(r"^ +", "", ln) for ln in stripped]
    log.add("leading indents removed", sum(1 for a, b in zip(stripped, lead) if a != b))
    lines = lead
    # paragraph structure
    has_blank = any(not ln.strip() for ln in lines[1:-1])
    if not has_blank and not keep_lines:
        nonempty = [ln for ln in lines if ln.strip()]
        log.add("single line breaks made paragraph breaks (no blank lines in source)", max(len(nonempty) - 1, 0))
        t = "\n\n".join(nonempty)
    else:
        blocks = re.split(r"\n\s*\n", "\n".join(lines))
        out = []
        joined = split = 0
        for b in blocks:
            bl = [x for x in b.split("\n") if x.strip()]
            if not bl:
                continue
            if keep_lines or len(bl) == 1 or any(re.match(r"^\s*(?:[-*+]\s|\d+[.)]\s|#|>|\|)", x) for x in bl):
                out.append("\n".join(bl))
                continue
            # Hard-wrapped prose breaks lines mid-sentence; lines that each end a sentence are paragraphs.
            mid = sum(1 for x in bl[:-1] if not re.search(r"[.!?…:;\"'”’)\]*_]\s*$", x))
            if mid * 2 >= len(bl) - 1:
                joined += len(bl) - 1
                out.append(" ".join(x.strip() for x in bl))
            else:
                split += len(bl) - 1
                out.extend(x.strip() for x in bl)
        log.add("hard-wrapped lines joined inside paragraphs", joined)
        log.add("single line breaks after a finished sentence made paragraph breaks", split)
        t = "\n\n".join(out)
    spaces = len(re.findall(r"(?<=\S)  +(?=\S)", t))
    t = re.sub(r"(?<=\S)  +(?=\S)", " ", t)
    log.add("runs of spaces inside lines made single", spaces)
    # scene breaks and headings
    paras = t.split("\n\n")
    sb = hd = 0
    for i, p in enumerate(paras):
        if SCENE_BREAK_RE.match(p) and p.strip() != "* * *":
            paras[i] = "* * *"
            sb += 1
        elif headings and "\n" not in p and not p.startswith("#") and CHAPTER_RE.match(p.strip()) and len(words(p)) <= 8:
            paras[i] = "## " + p.strip()
            hd += 1
    log.add("scene breaks made * * *", sb)
    log.add("chapter and part lines marked as headings (##)", hd, "; ".join(p for p in paras if p.startswith("## "))[:80])
    t = "\n\n".join(paras)
    # quotes
    mode = dominant_quotes(t) if quotes == "auto" else quotes
    if mode == "curly":
        nt = smart_quotes(t)
        log.add("straight quotes made curly (the source's dominant style)" if quotes == "auto" else "straight quotes made curly",
                sum(1 for a, b in zip(t, nt) if a != b))
        t = nt
    elif mode == "straight":
        nt = straight_quotes(t)
        log.add("curly quotes made straight", sum(1 for a, b in zip(t, nt) if a != b))
        t = nt
    # dashes
    em = t.count("—")
    dd = len(re.findall(r"(?<=\w)\s?--\s?(?=\w)", t))
    dmode = dashes
    if dashes == "auto":
        dmode = "em" if dd and em >= 0 else "keep"
    if dmode == "em":
        t2 = re.sub(r"(?<=\w)\s?--\s?(?=\w)|(?<=\w)--(?=[\s”\"'’]|$)", "—", t)
        log.add("double hyphens made em dashes", dd)
        t = t2
    elif dmode == "double":
        log.add("em dashes made double hyphens", em)
        t = t.replace("—", "--")
    ell = len(re.findall(r"(?<!\.)\.\s\.\s\.(?!\s\.)", t))
    t = re.sub(r"(?<!\.)\.\s\.\s\.(?!\s\.)", "...", t)
    log.add("spaced ellipses . . . closed up", ell)
    t = t.strip("\n") + "\n"
    return t, log


def check_words_same(a, b):
    ka, kb = word_key(a), word_key(b)
    if ka == kb:
        return None
    sm = __import__("difflib").SequenceMatcher(None, ka, kb, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != "equal":
            return "word %d: %r became %r" % (i1, " ".join(ka[i1:i2][:8]), " ".join(kb[j1:j2][:8]))
    return "word count %d became %d" % (len(ka), len(kb))


# ---------------------------------------------------------------- paragraphs and locations

def paragraphs(text):
    """Paragraphs of a clean text: blocks separated by blank lines, numbered from 1."""
    return [p for p in re.split(r"\n\s*\n", text.strip("\n")) if p.strip()]


def para_offsets(text):
    """(start, end) character offsets of each paragraph in text."""
    out = []
    for m in re.finditer(r"(?:[^\n]|\n(?!\s*\n))+", text):
        if m.group(0).strip():
            out.append((m.start(), m.end()))
    return out


def find_quote(text, para, quote, occurrence=1):
    """Absolute (start, end) of quote inside paragraph para (1-based); para 0 or None searches the whole text."""
    offs = para_offsets(text)
    if para:
        if para < 1 or para > len(offs):
            raise ValueError("paragraph P%d does not exist (the text has %d)" % (para, len(offs)))
        lo, hi = offs[para - 1]
    else:
        lo, hi = 0, len(text)
    hay = text[lo:hi]
    idx, start = -1, 0
    hits = []
    while True:
        idx = hay.find(quote, start)
        if idx < 0:
            break
        hits.append(idx)
        start = idx + 1
    if not hits:
        raise ValueError("quote not found in %s: %r" % ("P%d" % para if para else "the text", quote[:80]))
    if not para and len(hits) > 1 and not occurrence:
        raise ValueError("quote appears %d times; give para or occurrence: %r" % (len(hits), quote[:80]))
    occurrence = occurrence or 1
    if occurrence > len(hits):
        raise ValueError("occurrence %d asked, quote appears %d times: %r" % (occurrence, len(hits), quote[:80]))
    s = lo + hits[occurrence - 1]
    return s, s + len(quote)


def para_of_offset(text, off):
    for i, (a, b) in enumerate(para_offsets(text), 1):
        if a <= off <= b:
            return i
    return 0


# ---------------------------------------------------------------- provenance of a change

def osa(a, b):
    """Optimal string alignment distance (Levenshtein plus adjacent transpositions)."""
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[-1][-1]


# Irregular forms of one word: changing between them is a tense or agreement fix of the author's own word.
IRREGULAR = [g.split() for g in """be is am are was were been being|have has had having|do does did done doing
|say says said saying|go goes went gone going|ride rides rode ridden riding|see sees saw seen seeing
|come comes came coming|take takes took taken taking|give gives gave given giving|get gets got gotten getting
|make makes made making|know knows knew known knowing|think thinks thought thinking|run runs ran running
|shine shines shone shined shining|lie lies lay lain lying|lay lays laid laying|bring brings brought
|buy buys bought|catch catches caught|teach teaches taught|feel feels felt|find finds found|hold holds held
|keep keeps kept|leave leaves left|lose loses lost|mean means meant|meet meets met|pay pays paid|sell sells sold
|send sends sent|sit sits sat|speak speaks spoke spoken|stand stands stood|tell tells told|win wins won
|write writes wrote written|begin begins began begun|break breaks broke broken|choose chooses chose chosen
|drive drives drove driven|eat eats ate eaten|fall falls fell fallen|fly flies flew flown|forget forgot forgotten
|grow grows grew grown|hide hides hid hidden|rise rises rose risen|sing sings sang sung|swim swims swam swum
|throw throws threw thrown|wear wears wore worn|wake wakes woke woken|draw draws drew drawn|drink drinks drank drunk
|ring rings rang rung|shake shakes shook shaken|steal steals stole stolen|strike strikes struck|spin spins spun
|dig digs dug|hang hangs hung|feed feeds fed|lead leads led|fight fights fought|seek seeks sought|sleep sleeps slept
|sweep sweeps swept|weep weeps wept|bend bends bent|build builds built|spend spends spent|light lights lit
|slide slides slid|bite bites bit bitten|hit hits|cut cuts|put puts|set sets|let lets|shut shuts|this these
|that those|it its it's|they them their they're|you your you're|who whom whose|a an""".split("|")]
# Words commonly typed for one another (homophones and near misses); swapping between them fixes a slip.
CONFUSED = [g.split() for g in """road rode rowed|there their they're|to too two|then than|lose loose|affect effect
|accept except|passed past|whose who's|brake break|peak peek pique|site sight cite|rain reign rein|here hear
|threw through thru|waist waste|weather whether|which witch|principal principle|stationary stationery
|complement compliment|breath breathe|already all|altogether together|advice advise|desert dessert|wander wonder
|quiet quite|were where we're|your you're|its it's|of off|lead led|board bored|course coarse|hole whole
|right write rite|knew new|know no|piece peace|plain plane|sole soul|tail tale|wait weight|week weak|wood would
|bare bear|buy by bye|dear deer|fair fare|flour flower|for four fore|hair hare|heal heel|hour our|made maid
|mail male|meat meet|one won|pair pear|pole poll|pray prey|red read|role roll|sail sale|scene seen|sew so sow
|some sum|son sun|stair stare|steal steel|tied tide|toe tow|vain vein|way weigh|wear ware where""".split("|")]
IRREGULAR_GROUP = {w: i for i, g in enumerate(IRREGULAR) for w in g}
CONFUSED_GROUPS = {}
for _i, _g in enumerate(CONFUSED):
    for _w in _g:
        CONFUSED_GROUPS.setdefault(_w, set()).add(_i)


def is_correction(new, old):
    """A spelling fix or inflection of the author's own word: two forms of one irregular word, or the
    same first letter (or its first two letters swapped) with at most one edit for short words and two
    for longer ones."""
    if new in IRREGULAR_GROUP and IRREGULAR_GROUP.get(old) == IRREGULAR_GROUP[new]:
        return True
    if CONFUSED_GROUPS.get(new, set()) & CONFUSED_GROUPS.get(old, set()):
        return True
    if new[:1] != old[:1] and new[:2] != old[1::-1]:
        return False
    limit = 1 if max(len(new), len(old)) <= 4 else 2
    return osa(new, old) <= limit


def nearby_words(text, para):
    """The author's own content words in paragraph para and the paragraphs on either side of it."""
    paras = paragraphs(text)
    if not para:
        return set()
    near = paras[max(para - 2, 0):para + 1]
    return {w for w in word_key(" ".join(near)) if w not in STOP and len(w) > 3}


def provenance(find, replace, nearby=None):
    """Classify the words of a replacement: reused from the span it replaces, a spelling or inflection
    correction of a removed word, a word the author wrote nearby put in place of a removed word, or new
    (AI-written). Punctuation is not counted."""
    old = [norm_word(w) for w in words(find)]
    new = [norm_word(w) for w in words(replace)]
    pool = collections.Counter(old)
    unmatched = []
    reused = 0
    for w in new:
        if pool[w] > 0:
            pool[w] -= 1
            reused += 1
        else:
            unmatched.append(w)
    removed = list(pool.elements())
    corrected, added, own = [], [], []
    for w in unmatched:
        hit = next((r for r in removed if is_correction(w, r)), None)
        if hit is not None:
            removed.remove(hit)
            corrected.append("%s>%s" % (hit, w))
        elif nearby and removed and w in nearby:
            # One-for-one swap to a word the author already wrote beside this passage (blanks > planks).
            hit = removed.pop(0)
            corrected.append("%s>%s (the author's word nearby)" % (hit, w))
            own.append(w)
        else:
            added.append(w)
    if added:
        kind = "new-words"
    elif corrected:
        kind = "correction"
    elif removed:
        kind = "cut"
    elif old != new:
        kind = "reorder"
    else:
        kind = "punctuation"
    return {"reused": reused, "corrected": corrected, "removed": removed, "new_words": added,
            "new_word_count": len(added), "kind": kind}


# ---------------------------------------------------------------- intake

def remove_tree(path):
    """rmtree that also removes the read-only snapshot (Windows refuses to delete read-only files)."""
    def again(func, p, _exc):
        os.chmod(p, 0o666)
        func(p)
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=again)
    else:
        shutil.rmtree(path, onerror=again)


def cmd_intake(a):
    src = Path(a.source).expanduser().resolve()
    if not src.is_file():
        fail("source not found: %s" % src)
    works = works_root(a.works)
    work_slug = slugify(a.work or src.stem)
    wdir = works / work_slug
    stamp = datetime.date.today().strftime("%Y%m%d")
    n = 1
    while True:
        jdir = wdir / "jobs" / ("%s-%d-%s" % (stamp, n, a.level))
        if not jdir.exists():
            break
        n += 1
    src_hash = sha256_file(src)
    raw, read_as = source_text(src, a.text)  # refuse unreadable sources before anything is written
    jdir.mkdir(parents=True)
    snap = jdir / ("source" + src.suffix.lower())
    shutil.copy2(src, snap)
    if sha256_file(snap) != src_hash:
        fail("snapshot hash differs from the source; stopping")
    try:
        os.chmod(snap, 0o444)
    except OSError:
        pass
    clean, log = cleanup(raw, quotes=a.quotes, dashes=a.dashes,
                         keep_lines=a.keep_lines or a.genre in ("script", "poetry"), headings=not a.no_headings)
    diff = check_words_same(raw, clean)
    if diff:
        remove_tree(jdir)
        fail("cleanup changed a word (%s); nothing written. Report this as a bug." % diff)
    write_text(jdir / "source-text.md", raw if raw.endswith("\n") else raw + "\n")
    write_text(jdir / "clean.md", clean)
    nwords = len(words(clean))
    write_text(jdir / "cleanup-log.md", log.markdown({"words": nwords, "read_as": read_as}))
    th = dict(THRESHOLDS.get(a.genre, THRESHOLDS["other"]))
    job = {
        "editwright": VERSION,
        "work": work_slug,
        "title": a.title or src.stem,
        "author": a.author or "",
        "author_slug": slugify(a.author) if a.author else "",
        "genre": a.genre,
        "level": a.level,
        "style_guide": a.style or ("chicago" if a.genre != "script" else "screenplay"),
        "created": now_iso(),
        "source": {"path": str(src), "sha256": src_hash, "size": src.stat().st_size,
                   "mtime": src.stat().st_mtime, "ref": a.source_ref or "", "snapshot": snap.name,
                   "text_from": str(Path(a.text).resolve()) if a.text else ""},
        "text": {"words": nwords, "paragraphs": len(paragraphs(clean)), "clean_sha256": sha256_text(clean),
                 "read_as": read_as},
        "mode": "human-authored",
        "override": None,
        "threshold": th,
        "accepted": [],
        "rejected": [],
        "applied": [],
    }
    save_job(jdir, job)
    wj = wdir / "work.json"
    w = load_json(wj, {}) or {}
    w.update({"slug": work_slug, "title": job["title"], "author": job["author"], "genre": a.genre})
    w.setdefault("created", now_iso())
    save_json(wj, w)
    for name, head in (("style-sheet.md", "# Style sheet: %s\n\nSpellings, capitalisation, numbers, hyphenation and "
                                          "punctuation choices the author made, one per line with a paragraph "
                                          "reference. Built during the copy pass; never applied to the source.\n"),
                       ("story-bible.md", "# Story bible: %s\n\nCharacters (name, age, look, voice, relationships), "
                                          "places, timeline, objects and facts the text has fixed, each with the "
                                          "paragraph that fixed it.\n")):
        if not (wdir / name).exists():
            write_text(wdir / name, head % job["title"])
    append_note(jdir, "intake of %s (sha256 %s), %d words, genre %s, level %s, human-authored mode on" %
                (src.name, src_hash[:16], nwords, a.genre, a.level))
    print("job: %s" % jdir)
    print("source sha256: %s (snapshot %s, read-only)" % (src_hash, snap.name))
    print("clean.md: %d words, %d paragraphs; cleanup rules applied: %d (cleanup-log.md); word check passed" %
          (nwords, job["text"]["paragraphs"], len(log.rows)))
    print("mode: human-authored; AI-word limit for %s: %d words / %.1f%%" % (a.genre, th["words"], th["percent"]))
    if job["author_slug"]:
        ap = works / "authors" / (job["author_slug"] + ".md")
        print("author preferences: %s%s" % (ap, "" if ap.exists() else " (none yet)"))
    return 0


# ---------------------------------------------------------------- check

def cmd_check(a):
    jdir = resolve_job(a.job, a.works)
    job = load_job(jdir)
    ok = True
    s = job["source"]
    src = Path(s["path"])
    if s.get("ref", "").startswith(("gdoc:", "http")) and not a.against:
        print("note: the source is %s; pass --against a fresh export to check it" % s["ref"])
    if src.exists():
        h = sha256_file(src)
        same = h == s["sha256"]
        ok &= same
        print("%s source %s: %s" % ("OK  " if same else "FAIL", src, "unchanged" if same else "CHANGED (sha256 %s)" % h))
    else:
        print("note: source path %s is gone; checking the snapshot only" % src)
    snap = jdir / s["snapshot"]
    same = snap.exists() and sha256_file(snap) == s["sha256"]
    ok &= same
    print("%s snapshot %s: %s" % ("OK  " if same else "FAIL", snap.name, "matches" if same else "CHANGED or missing"))
    if a.against:
        fresh = Path(a.against)
        h = sha256_file(fresh)
        if h == s["sha256"]:
            print("OK   %s: byte-identical to the intake snapshot" % fresh.name)
        else:
            t1, _ = source_text(snap)
            t2, _ = decode_bytes(fresh.read_bytes())
            d = check_words_same(t1, t2)
            ok &= d is None
            print("%s %s: %s" % ("OK  " if d is None else "FAIL", fresh.name,
                                  "same words as the snapshot (bytes differ)" if d is None else "the words changed: " + d))
    clean = jdir / "clean.md"
    if clean.exists():
        raw = read_text(jdir / "source-text.md")
        d = check_words_same(raw, read_text(clean))
        ok &= d is None
        print("%s clean.md: %s" % ("OK  " if d is None else "FAIL", "same words as the source" if d is None else d))
    append_note(jdir, "check: %s" % ("passed" if ok else "FAILED"))
    result = "%s %s %s %s\n" % ("PASSED" if ok else "FAILED", now_iso(), job["work"], jdir.name)
    write_text(jdir.parent.parent.parent / "last-check.txt", result)
    print("check: %s" % ("PASSED" if ok else "FAILED: the author's source changed; the run fails"))
    return 0 if ok else 1


# ---------------------------------------------------------------- show and chunk

def cmd_show(a):
    jdir = resolve_job(a.job, a.works)
    paras = paragraphs(read_text(jdir / (a.file or "clean.md")))
    lo, hi = 1, len(paras)
    if a.para:
        m = re.match(r"^(\d+)(?:-(\d+))?$", a.para)
        if not m:
            fail("--para takes N or N-M", 2)
        lo = int(m.group(1))
        hi = int(m.group(2) or lo)
    out = []
    for i in range(max(lo, 1), min(hi, len(paras)) + 1):
        out.append("[P%d] %s" % (i, paras[i - 1]))
    text = "\n\n".join(out)
    if len(text) > a.max_chars:
        text = text[:a.max_chars] + "\n[... cut at %d characters; ask for a smaller --para range]" % a.max_chars
    print(text)
    return 0


def cmd_chunk(a):
    jdir = resolve_job(a.job, a.works)
    paras = paragraphs(read_text(jdir / "clean.md"))
    chunks, cur, cur_w, start = [], [], 0, 1
    for i, p in enumerate(paras, 1):
        w = len(words(p))
        boundary = p.startswith("#") or p == "* * *"
        if cur and (cur_w + w > a.max_words or (boundary and p.startswith("#") and cur_w >= a.min_words)):
            chunks.append((start, i - 1, cur_w))
            cur, cur_w, start = [], 0, i
        cur.append(p)
        cur_w += w
    if cur:
        chunks.append((start, len(paras), cur_w))
    cdir = jdir / "chunks"
    if cdir.exists():
        shutil.rmtree(cdir)
    lines = ["# Chunks", "", "Each chunk holds whole paragraphs; paragraph numbers match clean.md. Summarise each chunk "
             "into the story bible before moving on.", "", "| Chunk | Paragraphs | Words | First line |", "|---|---|---|---|"]
    for n, (lo, hi, w) in enumerate(chunks, 1):
        body = "\n\n".join("[P%d] %s" % (i, paras[i - 1]) for i in range(lo, hi + 1))
        write_text(cdir / ("%03d.md" % n), body + "\n")
        first = paras[lo - 1][:60].replace("|", "/")
        lines.append("| [%03d](%03d.md) | P%d-P%d | %d | %s |" % (n, n, lo, hi, w, first))
    write_text(cdir / "INDEX.md", "\n".join(lines) + "\n")
    print("%d chunks in %s (max %d words each); index chunks/INDEX.md" % (len(chunks), cdir, a.max_words))
    return 0


# ---------------------------------------------------------------- stats

SENT_RE = re.compile(r"[^.!?…]+(?:[.!?…]+[\"'”’)\]]*|$)")


def sentences(p):
    p = re.sub(r"\b(Mr|Mrs|Ms|Dr|St|Jr|Sr|Prof|vs|etc|e\.g|i\.e)\.", lambda m: m.group(0).replace(".", "\x00"), p)
    out = [s.replace("\x00", ".").strip() for s in SENT_RE.findall(p)]
    return [s for s in out if words(s)]


def text_stats(text, top=12):
    paras = paragraphs(text)
    body = [p for p in paras if not p.startswith("#") and p != "* * *"]
    all_words = []
    sents = []
    for i, p in enumerate(paras, 1):
        if p.startswith("#") or p == "* * *":
            continue
        for s in sentences(p):
            sents.append((i, s, len(words(s))))
        all_words.extend((i, w) for w in words(p))
    n = len(all_words) or 1
    lens = [x[2] for x in sents] or [0]
    buckets = collections.OrderedDict((k, 0) for k in ("1-5", "6-10", "11-20", "21-30", "31-40", "41+"))
    for L in lens:
        k = "1-5" if L <= 5 else "6-10" if L <= 10 else "11-20" if L <= 20 else "21-30" if L <= 30 else "31-40" if L <= 40 else "41+"
        buckets[k] += 1
    lw = [(i, norm_word(w)) for i, w in all_words]
    freq = collections.Counter(w for _, w in lw if w not in STOP and len(w) > 3)
    # repeats inside a 60-word window
    near = collections.Counter()
    near_where = {}
    last = {}
    for pos, (i, w) in enumerate(lw):
        if w in STOP or len(w) < 4:
            continue
        if w in last and pos - last[w] <= 60:
            near[w] += 1
            near_where.setdefault(w, set()).add(i)
        last[w] = pos
    ly = [(i, w) for i, w in lw if w.endswith("ly") and len(w) > 4 and w not in LY_EXCEPT]
    filt = [(i, w) for i, w in lw if w in FILTER_WORDS]
    crutch = collections.Counter(w for _, w in lw if w in CRUTCH_WORDS)
    dialogue_chars = sum(len(m) for m in re.findall(r"“[^”]*”|\"[^\"\n]*\"", "\n".join(body)))
    tags = collections.Counter()
    for m in re.finditer(r"[”\"]\s*,?\s*(?:[A-Z][a-z]+|he|she|they|I|we)\s+([a-z]+)\b|[”\"],?\s+([a-z]+)\s+(?:[A-Z][a-z]+|he|she|they)", "\n".join(body)):
        v = m.group(1) or m.group(2)
        if v and (v in TAG_VERBS or v.endswith("ed")):
            tags[v] += 1
    starts = collections.Counter()
    prev = None
    for i, s, _ in sents:
        w0 = norm_word(words(s)[0])
        if w0 == prev:
            starts[w0] += 1
        prev = w0
    ing = len(re.findall(r"\b(?:was|were)\s+\w+ing\b", text, re.I))
    started = len(re.findall(r"\b(?:began|begun|begins|started|starts)\s+to\b", text, re.I))
    longest = sorted(sents, key=lambda x: -x[2])[:5]
    per_k = lambda c: round(1000.0 * c / n, 1)
    return {
        "words": len(all_words), "paragraphs": len(paras), "sentences": len(sents),
        "sentence_length": {"mean": round(statistics.mean(lens), 1), "median": statistics.median(lens),
                            "stdev": round(statistics.pstdev(lens), 1), "min": min(lens), "max": max(lens),
                            "histogram": buckets},
        "longest_sentences": [{"para": i, "words": L, "start": s[:90]} for i, s, L in longest],
        "paragraph_words": {"mean": round(statistics.mean([len(words(p)) for p in body] or [0]), 1),
                            "max": max([len(words(p)) for p in body] or [0])},
        "dialogue_share_percent": round(100.0 * dialogue_chars / max(len("\n".join(body)), 1), 1),
        "top_words": freq.most_common(top),
        "close_repeats": [{"word": w, "count": c, "paras": sorted(near_where[w])[:8]} for w, c in near.most_common(top)],
        "ly_adverbs": {"per_1000": per_k(len(ly)), "count": len(ly),
                       "top": collections.Counter(w for _, w in ly).most_common(top)},
        "filter_words": {"per_1000": per_k(len(filt)), "count": len(filt),
                         "top": collections.Counter(w for _, w in filt).most_common(top),
                         "paras": sorted({i for i, _ in filt})[:20]},
        "crutch_words": dict(crutch.most_common(top)),
        "was_ing": ing, "began_started_to": started,
        "dialogue_tags": dict(tags.most_common(top)),
        "same_first_word_in_a_row": dict(starts.most_common(6)),
    }


def cmd_stats(a):
    p = Path(a.target)
    if p.is_file():
        text = read_text(p)
        jdir = None
    else:
        jdir = resolve_job(a.target, a.works)
        text = read_text(jdir / "clean.md")
    st = text_stats(text)
    if jdir:
        save_json(jdir / "stats.json", st)
    if a.json:
        print(json.dumps(st, indent=2, ensure_ascii=False))
        return 0
    sl = st["sentence_length"]
    print("words %d, paragraphs %d, sentences %d" % (st["words"], st["paragraphs"], st["sentences"]))
    print("sentence length: mean %s, median %s, sd %s, range %s-%s; histogram %s" %
          (sl["mean"], sl["median"], sl["stdev"], sl["min"], sl["max"],
           ", ".join("%s:%d" % kv for kv in sl["histogram"].items())))
    print("longest: " + "; ".join("P%d (%d w) %s..." % (x["para"], x["words"], x["start"][:40]) for x in st["longest_sentences"][:3]))
    print("dialogue share: %s%% of characters" % st["dialogue_share_percent"])
    print("-ly adverbs: %s per 1000 (%s)" % (st["ly_adverbs"]["per_1000"], ", ".join("%s %d" % kv for kv in st["ly_adverbs"]["top"][:8])))
    print("filter words: %s per 1000 (%s) in P%s" % (st["filter_words"]["per_1000"], ", ".join("%s %d" % kv for kv in st["filter_words"]["top"][:8]),
                                                    ",".join(map(str, st["filter_words"]["paras"][:12]))))
    print("crutch words: " + ", ".join("%s %d" % kv for kv in st["crutch_words"].items()))
    print("close repeats (60-word window): " + "; ".join("%s x%d P%s" % (r["word"], r["count"], ",".join(map(str, r["paras"][:5]))) for r in st["close_repeats"][:8]))
    print("top words: " + ", ".join("%s %d" % kv for kv in st["top_words"]))
    print("was/were + -ing: %d; began/started to: %d; dialogue tags: %s; same first word twice running: %s" %
          (st["was_ing"], st["began_started_to"], st["dialogue_tags"] or "none", st["same_first_word_in_a_row"] or "none"))
    print("(counts only; whether any of it is a problem is the editor's call, in context)")
    return 0


# ---------------------------------------------------------------- suggestions

def load_suggestions(jdir):
    return load_json(Path(jdir) / "suggestions.json", {"suggestions": []})


def next_id(existing):
    nums = [int(re.sub(r"\D", "", s["id"]) or 0) for s in existing]
    return "S-%03d" % ((max(nums) if nums else 0) + 1)


def validate_suggestion(s, text, genre):
    for k in ("level", "category", "problem"):
        if not s.get(k):
            raise ValueError("%s: missing %r" % (s.get("id", "?"), k))
    if s["level"] not in LEVELS:
        raise ValueError("%s: level must be one of %s" % (s.get("id", "?"), ", ".join(LEVELS)))
    quote = s.get("quote", "")
    if quote:
        start, end = find_quote(text, s.get("para"), quote, s.get("occurrence"))
        s["para"] = s.get("para") or para_of_offset(text, start)
        s["span"] = [start, end]
    elif s.get("change"):
        raise ValueError("%s: a change needs the exact quote it replaces" % s.get("id", "?"))
    ch = s.get("change")
    if ch is not None:
        if "replace" not in ch:
            raise ValueError("%s: change needs 'replace' (use \"\" for a cut)" % s.get("id", "?"))
        pv = provenance(quote, ch["replace"], nearby_words(text, s.get("para")))
        s["provenance"] = pv
        s["ai_words"] = pv["new_word_count"]
        s["marked_ai_text"] = pv["new_word_count"] > 0
    else:
        s["provenance"] = None
        s["ai_words"] = 0
        s["marked_ai_text"] = False
    s.setdefault("why", "")
    s.setdefault("options", [])
    s.setdefault("severity", 2)
    s["status"] = s.get("status", "open")
    return s


def cmd_suggest(a):
    jdir = resolve_job(a.job, a.works)
    job = load_job(jdir)
    text = read_text(jdir / "clean.md")
    data = load_suggestions(jdir)
    if a.replace_all:
        data = {"suggestions": []}
    incoming = load_json(a.file)
    if isinstance(incoming, dict):
        incoming = incoming.get("suggestions", [])
    def key(s):
        return (s.get("level"), s.get("category"), s.get("para"), s.get("quote"), json.dumps(s.get("change"), sort_keys=True))

    seen = {key(x) for x in data["suggestions"]}
    errors, added, dupes = [], [], 0
    for n, s in enumerate(incoming, 1):
        s = dict(s)
        if key(s) in seen:
            dupes += 1  # resubmitting a file after fixing its refused items adds only the fixed ones
            continue
        if not s.get("id") or any(x["id"] == s["id"] for x in data["suggestions"] + added):
            s["id"] = next_id(data["suggestions"] + added)
        try:
            added.append(validate_suggestion(s, text, job["genre"]))
            seen.add(key(s))
        except ValueError as e:
            errors.append("item %d: %s" % (n, e))
    data["suggestions"].extend(added)
    data["suggestions"].sort(key=lambda s: (LEVELS.index(s["level"]), s.get("span", [10 ** 9])[0]))
    save_json(jdir / "suggestions.json", data)
    marked = [s["id"] for s in added if s["marked_ai_text"]]
    print("added %d suggestion(s), %d in total; %d carry AI-written words%s" %
          (len(added), len(data["suggestions"]), len(marked), (" (%s)" % ", ".join(marked)) if marked else ""))
    if marked and job["mode"] == "human-authored" and job["threshold"]["words"] == 0:
        print("note: human-authored mode with a 0-word limit; apply will refuse these unless the author supplies "
              "the words (--author-text) or the job is overridden")
    if dupes:
        print("skipped %d already in suggestions.json" % dupes)
    write_views(jdir)
    if errors:
        print("refused %d suggestion(s) (the others were saved); fix these and run suggest again with the same file:" % len(errors))
        for e in errors:
            print("  - " + e)
        print("quotes must match `ew.py show` exactly, curly quotes and apostrophes included")
        return 1
    return 0


def critic(find, replace):
    if not replace:
        return "{--%s--}" % find
    if not find:
        return "{++%s++}" % replace
    return "{~~%s~>%s~~}" % (find, replace)


def write_views(jdir):
    job = load_job(jdir)
    text = read_text(Path(jdir) / "clean.md")
    data = load_suggestions(jdir)
    sugs = data["suggestions"]
    lines = ["# Suggestions: %s" % job["title"], "",
             "Level of edit: %s. Genre: %s. Mode: %s. Paragraph numbers (P) match clean.md." %
             (job["level"], job["genre"], job["mode"]),
             "Nothing here has been applied. Tell the editor which IDs you accept; queries need your own words.", ""]
    for lvl in LEVELS:
        group = [s for s in sugs if s["level"] == lvl]
        if not group:
            continue
        lines += ["## %s (%d)" % (lvl.capitalize(), len(group)), ""]
        for s in group:
            lines.append("### %s · %s · P%s · severity %s%s" % (s["id"], s["category"], s.get("para") or "-", s["severity"],
                                                                 " · AI words: %d" % s["ai_words"] if s["ai_words"] else ""))
            if s.get("quote"):
                lines.append("> %s" % s["quote"].replace("\n", " "))
            lines.append("")
            lines.append("- Problem: %s" % s["problem"])
            if s.get("why"):
                lines.append("- Why it matters: %s" % s["why"])
            for j, o in enumerate(s.get("options", []), 1):
                lines.append("- Option %d: %s" % (j, o))
            if s.get("change") is not None:
                pv = s["provenance"]
                lines.append("- Proposed change: %s" % critic(s["quote"], s["change"]["replace"]))
                lines.append("- Words: %s" % describe_pv(pv))
            else:
                lines.append("- Query: the fix is yours to write.")
            lines.append("")
    write_text(Path(jdir) / "suggestions.md", "\n".join(lines))
    # review.md: clean text with every proposed change and query inline in CriticMarkup
    marks = []
    offs = para_offsets(text)
    changes = [s for s in sugs if s.get("span") and s.get("change") is not None]
    for s in sugs:
        if not s.get("span"):
            continue
        a_, b_ = s["span"]
        if s.get("change") is not None:
            marks.append((a_, b_, critic(text[a_:b_], s["change"]["replace"]) + "{>>%s<<}" % s["id"]))
        elif any(c["span"][0] < b_ and a_ < c["span"][1] for c in changes):
            end = offs[s["para"] - 1][1] if s.get("para") else b_
            marks.append((end, end, "{>>%s: %s (on \"%s\")<<}" % (s["id"], s["problem"], text[a_:b_][:60])))
        else:
            marks.append((a_, b_, "{==%s==}{>>%s: %s<<}" % (text[a_:b_], s["id"], s["problem"])))
    marks.sort(key=lambda m: (m[0], m[1]))
    out, pos = [], 0
    for a_, b_, rep in marks:
        if a_ < pos:
            continue  # overlapping marks: the first one wins in this view
        out.append(text[pos:a_])
        out.append(rep)
        pos = b_
    out.append(text[pos:])
    write_text(Path(jdir) / "review.md", "".join(out))
    write_ledger(jdir)


def describe_pv(pv):
    if pv is None:
        return "none"
    parts = []
    if pv["kind"] == "cut":
        parts.append("a cut, no new words")
        if pv["removed"]:
            parts.append("removed %s" % ", ".join(pv["removed"]))
    elif pv["kind"] in ("reorder", "punctuation"):
        parts.append("%s only, no new words" % pv["kind"])
    if pv["corrected"]:
        parts.append("corrected %s" % ", ".join(pv["corrected"]))
    if pv["removed"] and pv["kind"] != "cut":
        parts.append("removed %s" % ", ".join(pv["removed"]))
    if pv["new_words"]:
        parts.append("AI-written: %s (%d)" % (" ".join(pv["new_words"]), pv["new_word_count"]))
    return "; ".join(parts) or "no new words"


def ledger_numbers(job, sugs, ids):
    total = job["text"]["words"] or 1
    chosen = [s for s in sugs if s["id"] in ids]
    ai = sum(s["ai_words"] for s in chosen if not s.get("author_text"))
    return ai, round(100.0 * ai / total, 2)


def write_ledger(jdir):
    job = load_job(jdir)
    sugs = load_suggestions(jdir)["suggestions"]
    rows = []
    for s in sugs:
        if s.get("change") is None:
            continue
        pv = s["provenance"]
        rows.append({"id": s["id"], "kind": pv["kind"], "ai_words": s["ai_words"], "new_words": pv["new_words"],
                     "corrected": pv["corrected"], "removed": len(pv["removed"]), "reused": pv["reused"],
                     "applied": s["id"] in job.get("applied", [])})
    all_ai, all_pct = ledger_numbers(job, sugs, [r["id"] for r in rows])
    app_ai = sum(x.get("ai_words", 0) for x in job.get("applied_detail", []))
    app_pct = round(100.0 * app_ai / max(job["text"]["words"], 1), 2)
    led = {"work": job["work"], "words_in_piece": job["text"]["words"], "mode": job["mode"],
           "threshold": job["threshold"], "if_all_changes_were_applied": {"ai_words": all_ai, "percent": all_pct},
           "applied": {"ids": job.get("applied", []), "ai_words": app_ai, "percent": app_pct,
                       "author_written_ids": [x["id"] for x in job.get("applied_detail", []) if x.get("author_text")]},
           "rows": rows}
    save_json(Path(jdir) / "provenance.json", led)
    md = ["# Provenance ledger: %s" % job["title"], "",
          "Counts the words each proposed change would bring in that the author did not write. Reused words, cuts, "
          "reorders, punctuation and spelling or inflection corrections of the author's own words count as the "
          "author's. Words the author typed (`--author-text`) count as the author's.", "",
          "- Piece: %d words. Mode: %s. Limit: %d words or %.1f%%, whichever is lower." %
          (job["text"]["words"], job["mode"], job["threshold"]["words"], job["threshold"]["percent"]),
          "- If every proposed change were applied: %d AI-written words (%.2f%%)." % (all_ai, all_pct),
          "- Applied so far: %d AI-written words (%.2f%%) from %d change(s)." % (app_ai, app_pct, len(job.get("applied", []))),
          "", "| ID | Kind | AI-written words | Corrected | Removed | Applied |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append("| %s | %s | %d %s | %s | %d | %s |" % (r["id"], r["kind"], r["ai_words"],
                                                       ("(" + " ".join(r["new_words"]) + ")") if r["new_words"] else "",
                                                       ", ".join(r["corrected"]) or "", r["removed"], "yes" if r["applied"] else ""))
    write_text(Path(jdir) / "provenance-ledger.md", "\n".join(md) + "\n")
    return led


def cmd_render(a):
    jdir = resolve_job(a.job, a.works)
    write_views(jdir)
    print("wrote suggestions.md, review.md, provenance-ledger.md and provenance.json in %s" % jdir)
    return 0


def cmd_ledger(a):
    jdir = resolve_job(a.job, a.works)
    job = load_job(jdir)
    sugs = load_suggestions(jdir)["suggestions"]
    led = write_ledger(jdir)
    if a.accept:
        ids = parse_ids(a.accept)
        unknown = [i for i in ids if i not in {x["id"] for x in sugs}]
        if unknown:
            print("refused: %s not in suggestions.json" % ", ".join(unknown))
            return 1
        ai, pct = ledger_numbers(job, sugs, ids)
        verdict = within_limit(job, ai, pct)
        print("accepting %s would bring in %d AI-written words (%.2f%%): %s" % (", ".join(ids), ai, pct, verdict[1]))
        return 0 if verdict[0] else 1
    print("piece %d words; all proposed changes: %d AI-written words (%.2f%%); applied: %d (%.2f%%)" %
          (led["words_in_piece"], led["if_all_changes_were_applied"]["ai_words"], led["if_all_changes_were_applied"]["percent"],
           led["applied"]["ai_words"], led["applied"]["percent"]))
    print("ledger: %s" % (jdir / "provenance-ledger.md"))
    return 0


# ---------------------------------------------------------------- apply

def parse_ids(s):
    ids = []
    for part in re.split(r"[,\s]+", s.strip()):
        if not part:
            continue
        m = re.match(r"^S-?(\d+)$", part, re.I) or re.match(r"^(\d+)$", part)
        if not m:
            fail("not a suggestion ID: %r (IDs look like S-007)" % part, 2)
        ids.append("S-%03d" % int(m.group(1)))
    return ids


def echoed_words(s, author_text):
    """Words in the author's text that they did not have before but that this suggestion offered
    (its change or options). Copying a suggestion's wording does not make it the author's."""
    offered = set(word_key(" ".join([(s.get("change") or {}).get("replace", "")] + list(s.get("options", [])))))
    offered -= set(word_key(s.get("quote", "")))
    new = provenance(s.get("quote", ""), author_text)["new_words"]
    # Common words count too when they sit in a run of three or more words copied from the suggestion.
    offered_seq = word_key(" ".join([(s.get("change") or {}).get("replace", "")] + list(s.get("options", []))))
    grams = {tuple(offered_seq[i:i + 3]) for i in range(len(offered_seq) - 2)}
    mine = word_key(author_text)
    copied = set()
    for i in range(len(mine) - 2):
        if tuple(mine[i:i + 3]) in grams:
            copied.update(range(i, i + 3))
    copied_words = collections.Counter(mine[i] for i in copied)
    out = []
    for w in new:
        if w in offered and (w not in STOP or copied_words[w] > 0):
            out.append(w)
            if copied_words[w]:
                copied_words[w] -= 1
    return out


def within_limit(job, ai, pct):
    if job["mode"] != "human-authored":
        return True, "allowed (human-authored mode overridden for this job: %s)" % (job.get("override") or {}).get("reason", "")
    th = job["threshold"]
    if ai <= th["words"] and pct <= th["percent"] + 1e-9:
        return True, "within the limit (%d words / %.1f%%)" % (th["words"], th["percent"])
    return False, "over the limit (%d words / %.1f%% for %s in human-authored mode)" % (th["words"], th["percent"], job["genre"])


def cmd_apply(a):
    jdir = resolve_job(a.job, a.works)
    job = load_job(jdir)
    data = load_suggestions(jdir)
    by_id = {s["id"]: s for s in data["suggestions"]}
    if not a.accept:
        fail("name the accepted IDs with --accept (the author's choice; there is no 'all')", 2)
    ids = parse_ids(a.accept)
    unknown = [i for i in ids if i not in by_id]
    if unknown:
        print("refused: %s not in suggestions.json; nothing applied" % ", ".join(unknown))
        return 1
    author_text = {}
    for item in a.author_text or []:
        if "=" not in item:
            fail("--author-text takes ID=TEXT", 2)
        k, v = item.split("=", 1)
        author_text[parse_ids(k)[0]] = v
    if a.author_file:
        for k, v in (load_json(a.author_file) or {}).items():
            author_text[parse_ids(k)[0]] = v
    stray = [i for i in author_text if i not in ids]
    if stray:
        print("refused: author text given for %s, which is not accepted; nothing applied" % ", ".join(stray))
        return 1
    text = read_text(jdir / "clean.md")
    if sha256_text(text) != job["text"]["clean_sha256"]:
        print("refused: clean.md changed since intake; re-run intake")
        return 1
    plan, problems = [], []
    for i in ids:
        s = by_id[i]
        if i in author_text:
            rep = author_text[i]
            if not s.get("span"):
                problems.append("%s has no quoted span to replace" % i)
                continue
        elif s.get("change") is not None:
            rep = s["change"]["replace"]
        else:
            problems.append("%s is a query with no proposed change; the author supplies the words (--author-text %s=\"...\")" % (i, i))
            continue
        a_, b_ = find_quote(text, s.get("para"), s["quote"], s.get("occurrence"))
        echo = echoed_words(s, rep) if i in author_text else []
        plan.append({"id": i, "start": a_, "end": b_, "old": text[a_:b_], "new": rep, "author_text": i in author_text,
                     "ai_words": len(echo) if i in author_text else s["ai_words"], "echoed": echo})
    if problems:
        print("refused; nothing applied:")
        for p in problems:
            print("  - " + p)
        return 1
    plan.sort(key=lambda x: x["start"])
    for x, y in zip(plan, plan[1:]):
        if y["start"] < x["end"]:
            print("refused: %s and %s change overlapping text; accept one of them" % (x["id"], y["id"]))
            return 1
    ai = sum(x["ai_words"] for x in plan)
    pct = round(100.0 * ai / max(job["text"]["words"], 1), 2)
    ok, why = within_limit(job, ai, pct)
    if not ok:
        over = [x["id"] for x in plan if x["ai_words"]]
        print("refused: these changes bring in %d AI-written words (%.2f%%), %s. Carrying AI words: %s. "
              "Ask the author to write those words (--author-text) or to drop them; nothing applied." %
              (ai, pct, why, ", ".join(over)))
        return 1
    out = text
    for x in reversed(plan):
        out = out[:x["start"]] + x["new"] + out[x["end"]:]
    n = 2
    target = jdir / ("edited.md" if not (jdir / "edited.md").exists() else "edited-%d.md" % n)
    while target.exists():
        n += 1
        target = jdir / ("edited-%d.md" % n)
    write_text(target, out)
    if a.docx:
        write_docx(target.with_suffix(".docx"), paragraphs(out), job["title"])
    cl = ["# Changelog: %s" % target.name, "",
          "From clean.md (sha256 %s). Only the IDs the author accepted were applied. AI-written words: %s." %
          (job["text"]["clean_sha256"][:16], why), "",
          "| ID | Para | Before | After | Words | Who wrote the new words |", "|---|---|---|---|---|---|"]
    for x in plan:
        s = by_id[x["id"]]
        pv = provenance(x["old"], x["new"], nearby_words(text, s.get("para")))
        words_note = ("the author wrote %d new word(s)%s" % (pv["new_word_count"], "; %d echo the suggestion" % len(x["echoed"]) if x["echoed"] else "")
                      if x["author_text"] else describe_pv(pv))
        cl.append("| %s | P%s | %s | %s | %s | %s |" % (x["id"], s.get("para"), x["old"].replace("|", "/")[:120],
                                                     (x["new"] or "(cut)").replace("|", "/")[:120], words_note,
                                                     ("author; echoes editwright's wording: %s" % " ".join(x["echoed"]) if x["echoed"] else "author")
                                                     if x["author_text"] else ("editwright (AI)" if x["ai_words"] else "nobody: author's own words")))
    write_text(target.with_name(target.stem + "-changelog.md"), "\n".join(cl) + "\n")
    # Each apply builds a fresh file from clean.md; "applied" describes the newest edited file.
    job["applied"] = sorted(ids)
    job["applied_file"] = target.name
    job["applied_detail"] = [{"id": x["id"], "ai_words": x["ai_words"], "author_text": x["author_text"], "file": target.name}
                             for x in sorted(plan, key=lambda x: x["id"])]
    job["accepted"] = sorted(set(job.get("accepted", [])) | set(ids))
    save_job(jdir, job)
    for s in data["suggestions"]:
        if s.get("status") == "applied":
            s["status"] = "open"
    for x in plan:
        by_id[x["id"]]["status"] = "applied"
        if x["author_text"]:
            by_id[x["id"]]["author_text"] = x["new"]
    save_json(jdir / "suggestions.json", data)
    write_views(jdir)
    append_note(jdir, "apply %s -> %s (%d AI-written words)" % (", ".join(ids), target.name, sum(x["ai_words"] for x in plan)))
    print("applied %d change(s) to a copy: %s (changelog %s)" % (len(plan), target, target.stem + "-changelog.md"))
    print("AI-written words in this file: %d (%.2f%%); %s" % (ai, pct, why))
    print("the source was not touched; run `ew.py check` to confirm")
    return 0


# ---------------------------------------------------------------- feedback, author preferences, override

def cmd_feedback(a):
    jdir = resolve_job(a.job, a.works)
    job = load_job(jdir)
    by_id = {s["id"]: s for s in load_suggestions(jdir)["suggestions"]}
    acc = parse_ids(a.accepted) if a.accepted else []
    rej = parse_ids(a.rejected) if a.rejected else []
    unknown = [i for i in acc + rej if i not in by_id]
    if unknown:
        fail("unknown IDs: %s" % ", ".join(unknown))
    job["accepted"] = sorted(set(job.get("accepted", [])) | set(acc))
    job["rejected"] = sorted(set(job.get("rejected", [])) | set(rej))
    save_job(jdir, job)
    if a.note:
        append_note(jdir, "author feedback: %s" % a.note)
    if not job.get("author_slug"):
        print("recorded on the job; no author set, so no preferences file was updated")
        return 0
    adir = works_root(a.works) / "authors"
    pj = adir / (job["author_slug"] + ".json")
    prefs = load_json(pj, {"author": job["author"], "categories": {}, "levels": {}, "jobs": []})
    for ids, key in ((acc, "accepted"), (rej, "rejected")):
        for i in ids:
            s = by_id[i]
            for bucket, name in (("categories", s["category"]), ("levels", s["level"])):
                c = prefs[bucket].setdefault(name, {"accepted": 0, "rejected": 0})
                c[key] += 1
    if jdir.name not in prefs["jobs"]:
        prefs["jobs"].append(jdir.name)
    save_json(pj, prefs)
    pm = adir / (job["author_slug"] + ".md")
    if not pm.exists():
        write_text(pm, "# Author preferences: %s\n\nRead before every pass. Tallies in %s.json; taste notes below, "
                       "one line each with the date and the job.\n\n## Takes\n\n## Turns down\n\n## Notes\n" %
                   (job["author"], job["author_slug"]))
    print("recorded %d accepted, %d rejected; preferences: %s" % (len(acc), len(rej), pj))
    print(author_summary(prefs))
    return 0


def author_summary(prefs):
    rows = []
    for name, c in sorted(prefs.get("categories", {}).items(), key=lambda kv: -(kv[1]["accepted"] + kv[1]["rejected"])):
        tot = c["accepted"] + c["rejected"]
        rows.append("%s %d/%d taken" % (name, c["accepted"], tot))
    return "by category: " + ("; ".join(rows) if rows else "no history yet")


def cmd_author(a):
    adir = works_root(a.works) / "authors"
    slug = slugify(a.name)
    pj, pm = adir / (slug + ".json"), adir / (slug + ".md")
    if not pj.exists() and not pm.exists():
        print("no preferences yet for %s (%s)" % (a.name, adir))
        return 0
    if pj.exists():
        print(author_summary(load_json(pj)))
    if pm.exists():
        print(read_text(pm))
    return 0


def cmd_override(a):
    jdir = resolve_job(a.job, a.works)
    job = load_job(jdir)
    if a.off:
        job["mode"] = "human-authored"
        job["override"] = None
        save_job(jdir, job)
        append_note(jdir, "override removed; human-authored mode back on")
        print("human-authored mode back on for this job")
        return 0
    if not a.reason or len(a.reason.split()) < 3:
        fail("--reason must quote what the user said (for example \"rewrite it freely\")", 2)
    job["mode"] = "free"
    job["override"] = {"reason": a.reason, "date": now_iso()}
    save_job(jdir, job)
    append_note(jdir, "OVERRIDE: human-authored mode off for this job only. User said: %s" % a.reason)
    print("human-authored mode is off for this job only; recorded in notes.md. The ledger still counts AI-written words.")
    return 0


def cmd_status(a):
    jdir = resolve_job(a.job, a.works)
    job = load_job(jdir)
    sugs = load_suggestions(jdir)["suggestions"]
    files = [f for f in ("clean.md", "cleanup-log.md", "editorial-letter.md", "suggestions.json", "suggestions.md",
                         "review.md", "provenance-ledger.md", "edited.md") if (jdir / f).exists()]
    print("job %s: %s (%s, %s), %d words, mode %s" % (jdir.name, job["title"], job["genre"], job["level"],
                                                      job["text"]["words"], job["mode"]))
    c = collections.Counter(s["level"] for s in sugs)
    print("suggestions: %d (%s); applied %d; rejected %d" % (len(sugs), ", ".join("%s %d" % kv for kv in c.items()) or "none",
                                                             len(job.get("applied", [])), len(job.get("rejected", []))))
    print("files: " + ", ".join(files))
    print("folder: %s" % jdir)
    return 0


# ---------------------------------------------------------------- docx writer (stdlib)

def _r(text, deleted=False):
    tag = "w:delText" if deleted else "w:t"
    return '<w:r><%s xml:space="preserve">%s</%s></w:r>' % (tag, html.escape(text, quote=False), tag)


def _p(inner, style=None):
    ppr = '<w:pPr><w:pStyle w:val="%s"/></w:pPr>' % style if style else ""
    return "<w:p>%s%s</w:p>" % (ppr, inner)


DOCX_CT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
           '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
           '<Default Extension="xml" ContentType="application/xml"/>'
           '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
           '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
           '%s</Types>')
DOCX_COMMENTS_CT = '<Override PartName="/word/comments.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>'
DOCX_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
             '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
             '</Relationships>')
DOC_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
            '%s</Relationships>')
DOC_COMMENTS_REL = '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" Target="comments.xml"/>'
W_DECL = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
STYLES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:styles %s>'
          '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>'
          '<w:pPr><w:spacing w:after="160" w:line="360" w:lineRule="auto"/></w:pPr>'
          '<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/></w:rPr></w:style>'
          '%s</w:styles>') % (W_DECL, "".join(
              '<w:style w:type="paragraph" w:styleId="Heading%d"><w:name w:val="heading %d"/><w:basedOn w:val="Normal"/>'
              '<w:next w:val="Normal"/><w:pPr><w:keepNext/><w:outlineLvl w:val="%d"/></w:pPr><w:rPr><w:b/><w:sz w:val="%d"/></w:rPr></w:style>'
              % (i, i, i - 1, 36 - 4 * i) for i in range(1, 4)))


def _para_xml(p, inner=None):
    m = re.match(r"^(#{1,6})\s+(.*)$", p)
    if m:
        return _p(inner if inner is not None else _r(m.group(2)), "Heading%d" % min(len(m.group(1)), 3))
    if p == "* * *":
        return _p(_r("* * *"))
    return _p(inner if inner is not None else _r(p))


def _write_docx_parts(path, body_xml, comments_xml=None):
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:document %s><w:body>%s'
           '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
           'w:header="720" w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>') % (W_DECL, body_xml)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", DOCX_CT % (DOCX_COMMENTS_CT if comments_xml else ""))
        z.writestr("_rels/.rels", DOCX_RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS % (DOC_COMMENTS_REL if comments_xml else ""))
        z.writestr("word/document.xml", doc)
        z.writestr("word/styles.xml", STYLES)
        if comments_xml:
            z.writestr("word/comments.xml", comments_xml)
    ET.fromstring(doc.split("\n", 1)[1])  # well-formedness check
    if comments_xml:
        ET.fromstring(comments_xml.split("\n", 1)[1])


def write_docx(path, paras, title=""):
    _write_docx_parts(path, "".join(_para_xml(p) for p in paras))


def cmd_export(a):
    """review.docx: clean text with each proposed change as a Word tracked change (author 'editwright
    suggestion S-nnn') and each suggestion as a comment, for the author to accept or reject in Word or
    Google Docs. The source is not touched."""
    jdir = resolve_job(a.job, a.works)
    job = load_job(jdir)
    text = read_text(jdir / "clean.md")
    sugs = [s for s in load_suggestions(jdir)["suggestions"] if s.get("span")]
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    offs = para_offsets(text)
    body, comments, rid = [], [], [0]
    used, skipped = [], []
    changes = []
    for s in sorted((s for s in sugs if s.get("change") is not None), key=lambda s: s["span"][0]):
        if any(s["span"][0] < e and b < s["span"][1] for b, e in used):
            skipped.append(s["id"])
            continue
        used.append(tuple(s["span"]))
        changes.append(s)
    queries = [s for s in sugs if s.get("change") is None]

    def new_id():
        rid[0] += 1
        return rid[0]

    def add_comment(s):
        cid = len(comments)
        note = "%s (%s, %s): %s" % (s["id"], s["level"], s["category"], s["problem"])
        if s.get("quote") and s.get("change") is None:
            note += ' On: "%s"' % s["quote"][:120]
        if s.get("why"):
            note += " Why: " + s["why"]
        for j, o in enumerate(s.get("options", []), 1):
            note += " Option %d: %s" % (j, o)
        if s["ai_words"]:
            note += " [AI-written words: %d]" % s["ai_words"]
        comments.append('<w:comment w:id="%d" w:author="editwright" w:date="%s" w:initials="EW"><w:p>%s</w:p></w:comment>'
                        % (cid, date, _r(note)))
        return cid

    for pi, (lo, hi) in enumerate(offs, 1):
        ptxt = text[lo:hi]
        here = [s for s in changes if lo <= s["span"][0] and s["span"][1] <= hi]
        qs = [s for s in queries if lo <= s["span"][0] and s["span"][1] <= hi]
        m = re.match(r"^(#{1,6})\s+", ptxt)
        pos = lo + (m.end() if m else 0)
        qids = [add_comment(s) for s in qs]
        inner = ['<w:commentRangeStart w:id="%d"/>' % c for c in qids]
        for s in here:
            a_, b_ = s["span"]
            if a_ < pos:
                continue
            inner.append(_r(text[pos:a_]))
            cid = add_comment(s)
            auth = "editwright suggestion %s" % s["id"]
            inner.append('<w:commentRangeStart w:id="%d"/>' % cid)
            inner.append('<w:del w:id="%d" w:author="%s" w:date="%s">%s</w:del>' % (new_id(), auth, date, _r(text[a_:b_], True)))
            if s["change"]["replace"]:
                inner.append('<w:ins w:id="%d" w:author="%s" w:date="%s">%s</w:ins>' % (new_id(), auth, date, _r(s["change"]["replace"])))
            inner.append('<w:commentRangeEnd w:id="%d"/><w:r><w:commentReference w:id="%d"/></w:r>' % (cid, cid))
            pos = b_
        inner.append(_r(text[pos:hi]))
        inner += ['<w:commentRangeEnd w:id="%d"/><w:r><w:commentReference w:id="%d"/></w:r>' % (c, c) for c in qids]
        body.append(_para_xml(ptxt, "".join(inner)))
    cxml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:comments %s>%s</w:comments>' % (W_DECL, "".join(comments))
            if comments else None)
    target = jdir / (a.out or "review.docx")
    _write_docx_parts(target, "".join(body), cxml)
    print("wrote %s: %d tracked suggestion(s) and %d comment(s) on a copy of clean.md" % (target, len(changes), len(comments)))
    if skipped:
        print("left out (they overlap an earlier change; they are in suggestions.md): %s" % ", ".join(skipped))
    print("open it in Word, or upload it to Google Drive and open with Google Docs; accepting there is the author's act")
    return 0


# ---------------------------------------------------------------- main

def build_parser():
    ap = argparse.ArgumentParser(prog="ew.py", description="editwright: intake, cleanup, counts, suggestions, "
                                 "provenance and apply for manuscript editing. The source is never modified.")
    ap.add_argument("--version", action="version", version="editwright " + VERSION)
    ap.add_argument("--works", help="works store (default: $EDITWRIGHT_WORKS, ~/.editwright.json 'works', ~/editwright-works)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("intake", help="snapshot and hash the source, write clean.md and cleanup-log.md")
    p.add_argument("source", help="the author's file (read-only)")
    p.add_argument("--work", help="work slug (default: file name)")
    p.add_argument("--title")
    p.add_argument("--author")
    p.add_argument("--genre", choices=GENRES, default="fiction")
    p.add_argument("--level", choices=LEVELS + ["full"], default="full")
    p.add_argument("--style", help="style guide for the copy pass (chicago, ap, apa, mla, oxford, house)")
    p.add_argument("--text", help="text already extracted from the source (for PDF, EPUB, Google Docs exports)")
    p.add_argument("--source-ref", help="where the source lives when it is not a local file (gdoc:<id>, a URL)")
    p.add_argument("--quotes", choices=["auto", "curly", "straight", "keep"], default="auto")
    p.add_argument("--dashes", choices=["auto", "em", "double", "keep"], default="auto")
    p.add_argument("--keep-lines", action="store_true", help="keep single line breaks (verse, scripts)")
    p.add_argument("--no-headings", action="store_true", help="do not mark chapter lines as headings")
    p.set_defaults(func=cmd_intake)

    p = sub.add_parser("check", help="confirm the source and its snapshot are unchanged (exit 1 if not)")
    p.add_argument("job")
    p.add_argument("--against", help="a fresh export of a remote source (Google Doc) to compare")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("show", help="print numbered paragraphs of clean.md")
    p.add_argument("job")
    p.add_argument("--para", help="N or N-M")
    p.add_argument("--file", help="another text file in the job folder")
    p.add_argument("--max-chars", type=int, default=25000)
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("chunk", help="split clean.md into chunks of whole paragraphs for long manuscripts")
    p.add_argument("job")
    p.add_argument("--max-words", type=int, default=6000)
    p.add_argument("--min-words", type=int, default=1500)
    p.set_defaults(func=cmd_chunk)

    p = sub.add_parser("stats", help="counts: sentence lengths, repeats, adverbs, filter words, dialogue")
    p.add_argument("target", help="job or text file")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("suggest", help="validate and add suggestions from a JSON file")
    p.add_argument("job")
    p.add_argument("file", help="JSON list of suggestions (see references/suggestion-format.md)")
    p.add_argument("--replace-all", action="store_true", help="drop the existing suggestions first")
    p.set_defaults(func=cmd_suggest)

    p = sub.add_parser("render", help="rewrite suggestions.md, review.md and the provenance ledger")
    p.add_argument("job")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("ledger", help="provenance ledger; --accept checks a set against the limit")
    p.add_argument("job")
    p.add_argument("--accept")
    p.set_defaults(func=cmd_ledger)

    p = sub.add_parser("apply", help="apply the author's accepted IDs to a new file next to clean.md")
    p.add_argument("job")
    p.add_argument("--accept", required=False, help="comma-separated IDs the author accepted")
    p.add_argument("--author-text", action="append", help="ID=TEXT: words the author wrote for a query or in place of a proposal")
    p.add_argument("--author-file", help="JSON {ID: text} of words the author wrote")
    p.add_argument("--docx", action="store_true", help="also write the edited text as .docx")
    p.set_defaults(func=cmd_apply)

    p = sub.add_parser("export", help="review.docx with tracked changes and comments for Word or Google Docs")
    p.add_argument("job")
    p.add_argument("--out")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("feedback", help="record which IDs the author took and turned down; updates author preferences")
    p.add_argument("job")
    p.add_argument("--accepted")
    p.add_argument("--rejected")
    p.add_argument("--note")
    p.set_defaults(func=cmd_feedback)

    p = sub.add_parser("author", help="print an author's preferences")
    p.add_argument("name")
    p.set_defaults(func=cmd_author)

    p = sub.add_parser("override", help="turn human-authored mode off for one job, quoting the user")
    p.add_argument("job")
    p.add_argument("--reason")
    p.add_argument("--off", action="store_true", help="turn human-authored mode back on")
    p.set_defaults(func=cmd_override)

    p = sub.add_parser("status", help="summary of a job")
    p.add_argument("job")
    p.set_defaults(func=cmd_status)
    return ap


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", newline="\n")
        except (AttributeError, ValueError):
            pass
    a = build_parser().parse_args(argv)
    try:
        return a.func(a)
    except ValueError as e:
        print("editwright: %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
