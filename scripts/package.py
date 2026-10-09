"""Build dist/editwright.zip for claude.ai and Claude Desktop (Customize > Skills > Upload skill).
Run from the repository root: python scripts/package.py"""
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "editwright"
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def main():
    head = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---")[1]
    keys = set(re.findall(r"^([a-z-]+):", head, re.M))
    if keys - ALLOWED:
        sys.exit("SKILL.md frontmatter has keys claude.ai rejects: %s" % sorted(keys - ALLOWED))
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    target = out / "editwright.zip"
    files = sorted(p for p in SKILL.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, "editwright/" + f.relative_to(SKILL).as_posix())
    with zipfile.ZipFile(target) as z:
        names = z.namelist()
    if {n.split("/")[0] for n in names} != {"editwright"} or "editwright/SKILL.md" not in names:
        sys.exit("zip check failed")
    print("wrote %s: %d files, %d KB" % (target, len(names), target.stat().st_size // 1024))


if __name__ == "__main__":
    main()
