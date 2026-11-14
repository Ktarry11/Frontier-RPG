#!/usr/bin/env python3
"""Every text file the code reads or writes names its encoding: UTF-8. Idempotent.

    python3 tools/fix_text_encoding.py [--check]

WHY. Python on Windows opens text files as cp1252 unless told otherwise. The data files are UTF-8
(names like Adrian with an accent, Jovanovic with one), so a read with no encoding either turns
those names into rubbish or, when it meets a byte cp1252 has no character for, stops the game.
Kyle, 13 Nov 2026, on his own machine: "UnicodeDecodeError: 'charmap' codec can't decode byte
0x81" from tools/recruit_sites.py, on the first line of starting the game. Linux and Mac default
to UTF-8, which is why nothing here ever caught it.

Rewrites `.read_text()` / `.write_text(x)` and bare `open(...)` calls that are text mode with no
encoding. Binary opens, and anything that already names an encoding, are left alone.
--check changes nothing and exits 1 if anything would change (tools/qa_text_encoding.py).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"fix_text_encoding.py"}


def _balanced(src, start):
    """Index just past the ')' matching the '(' at `start`."""
    depth, i, quote = 0, start, None
    while i < len(src):
        ch = src[i]
        if quote:
            if ch == "\\":
                i += 1
            elif src.startswith(quote, i):
                i += len(quote) - 1
                quote = None
        elif src.startswith(('"""', "'''"), i):
            quote = src[i:i + 3]
            i += 2
        elif ch in "\"'":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def fix(src):
    out, pos, n = [], 0, 0
    pat = re.compile(r"\.read_text\(\)|\.write_text\(|(?<![\w.])open\(")
    for m in pat.finditer(src):
        if m.start() < pos:
            continue
        if m.group(0) == ".read_text()":
            out.append(src[pos:m.start()] + '.read_text(encoding="utf-8")')
            pos = m.end()
            n += 1
            continue
        lp = m.end() - 1
        end = _balanced(src, lp)
        if end < 0:
            continue
        args = src[lp + 1:end - 1]
        if "encoding" in args or not args.strip():
            continue
        if m.group(0) != ".write_text(":
            mode = re.search(r"""[,\s](?:mode\s*=\s*)?(['"])([rwaxbt+]+)\1\s*(?:,|$)""", args)
            if mode and "b" in mode.group(2):
                continue
        out.append(src[pos:end - 1] + ', encoding="utf-8")')
        pos = end
        n += 1
    out.append(src[pos:])
    return "".join(out), n


def main():
    check = "--check" in sys.argv
    total, files = 0, []
    for path in sorted(ROOT.rglob("*.py")):
        if path.name in SKIP or "__pycache__" in path.parts or ".git" in path.parts:
            continue
        src = path.read_text(encoding="utf-8")
        new, n = fix(src)
        if n:
            total += n
            files.append((path.relative_to(ROOT), n))
            if not check:
                path.write_text(new, encoding="utf-8")
    for f, n in files[:40]:
        print(f"  {n:3d}  {f}")
    print(f"{total} text reads and writes {'would be' if check else 'were'} given an encoding, in {len(files)} files")
    return 1 if (check and total) else 0


if __name__ == "__main__":
    sys.exit(main())
