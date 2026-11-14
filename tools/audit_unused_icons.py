#!/usr/bin/env python3
"""Find icon files nothing in the game can ever draw.

    PYTHONPATH=. python3 tools/audit_unused_icons.py
    PYTHONPATH=. python3 tools/audit_unused_icons.py --list
    PYTHONPATH=. python3 tools/audit_unused_icons.py --write-list <path>

THE COMPANION TO audit_icon_coverage.py, which answers the opposite
question. That tool asks "which ability or talent has no art"; this one
asks "which art belongs to no ability or talent".

WHY THE PILE EXISTS. Rebuilding a talent tree renames its nodes, and the
art is filed under the OLD talent_id. Nothing deletes the orphan, nothing
reports it, and the file sits there forever. Twenty-five of the twenty-
seven classic trees were rebuilt in this session alone, so most of what
this finds is expected rather than mysterious.

HOW A FILE IS CLAIMED. A file counts as USED if its stem matches any of:
  - an ability_id or a talent_id (the UI defaults icon_id to the id and
    the art is named to match - see audit_icon_coverage.py's docstring,
    which records the trap of treating `icon_id: null` as missing art)
  - an explicit icon_id anywhere in data/ (abilities, talents, items,
    recipes, bags, quests, vendors - anything)
  - any bare string in data/ or in the python under combat/, entities/,
    ui/ and tools/, because plenty of art is referenced by a literal
    filename in code rather than through data

THAT LAST RULE IS DELIBERATELY GREEDY. A false "unused" leads to deleting
art that something draws, and the failure is invisible until a player
opens the right screen. A false "used" costs a few kilobytes. So the tool
errs hard toward keeping, and its count is a FLOOR on what is dead, not a
precise figure.

NOTHING IS DELETED HERE, EVER. This tool only reports. Kyle asked for the
list to confirm before anything is removed, and deletion is a separate,
explicit step - the icons are real art, and some of it was hand-fetched.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICON_ROOT = ROOT / "assets/icons"

#: EVERY python file in the repo, not a hand-listed set of folders. The
#: first version of this tool listed ("combat", "entities", "ui", "tools",
#: ...) and MISSED gear_icons.py, which sits at the REPO ROOT and maps
#: hundreds of gear icons by name - so 615 live gear icons were reported as
#: unused and would have been deleted. core/ and world/ were missing too.
#: A hand-maintained list of source folders is exactly the kind of thing
#: that goes stale silently, and here the failure mode is deleting art.
SKIP_DIRS = {".git", "__pycache__", "assets", "node_modules", ".venv"}
TOKEN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_\-.]*")


def all_data_text():
    """Every byte of data/ plus the python that might name a file."""
    chunks = []
    for pattern in ("*.json", "*.py", "*.js", "*.md"):
        for p in ROOT.rglob(pattern):
            if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
                continue
            chunks.append(p.read_text(errors="ignore"))
    return "\n".join(chunks)


def referenced_tokens(text):
    """Every identifier-ish token, so a literal filename in code counts."""
    return set(TOKEN.findall(text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="print every unused file")
    ap.add_argument("--write-list", metavar="PATH",
                    help="write the unused paths, one per line, for review")
    args = ap.parse_args()

    if not ICON_ROOT.exists():
        print("no assets/icons"); return 1

    text = all_data_text()
    tokens = referenced_tokens(text)

    # NAMES BUILT AT RUNTIME. Two icon folders never have their filenames
    # written out anywhere, so an exact-token check reports almost all of
    # them as dead and deleting them would strip live art:
    #
    #   gear/         gear_icons.py holds a PREFIX TABLE and globs the
    #                 folder (_icons_for_prefixes), so an icon is reachable
    #                 if any prefix matches. 702 of 722 are reachable; the
    #                 first version of this tool called 614 of them unused.
    #   vendor_trash/ entities/vendor_trash.py builds f"{icon}{band}" and
    #                 f"{icon}_{element}", so every banded and elemental
    #                 variant is constructed, never spelled out.
    #
    # Both are handled by a PREFIX rule: a file is used if some referenced
    # token is a prefix of its stem. That is deliberately loose - it is the
    # safe direction, and these two folders are reported separately rather
    # than offered for deletion.
    try:
        sys.path.insert(0, str(ROOT))
        import gear_icons as _gi
        for table in (_gi.ARMOR_ICON_PREFIXES, _gi.WEAPON_ICON_PREFIXES):
            for v in table.values():
                tokens.update(v)
    except Exception as exc:                      # pragma: no cover
        print(f"  WARNING: could not read gear_icons.py prefixes ({exc}) - "
              f"gear icons may be reported as unused incorrectly")

    # Checked by walking the STEM's own prefixes against the token SET,
    # not by scanning every token per file. The first version did the
    # latter - 8576 files x ~400k tokens - and the process was OOM-killed.
    def runtime_reachable(stem):
        for cut in range(8, len(stem)):
            if stem[:cut] in tokens:
                return True
        return False

    files = sorted(p for p in ICON_ROOT.rglob("*") if p.is_file())
    unused = []
    for p in files:
        stem = p.stem
        if stem in tokens:
            continue
        # The prefix rule applies ONLY to the two folders that genuinely
        # build filenames at runtime. Applying it everywhere HID 241 real
        # orphans: every talent icon begins with its tree id (a token in
        # its own right), so "druid_feral_feral_mastery" looked reachable
        # from the bare token "druid_feral" even though that talent no
        # longer exists. Loose in the right place, exact everywhere else.
        if p.parent.name in ("gear", "vendor_trash") and runtime_reachable(stem):
            continue
        # also accept the full filename, and the path as written in data
        if p.name in tokens or p.name in text:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel in text or p.relative_to(ICON_ROOT).as_posix() in text:
            continue
        unused.append(p)

    by_dir = defaultdict(list)
    for p in unused:
        by_dir[p.parent.relative_to(ROOT).as_posix()].append(p)

    total_bytes = sum(p.stat().st_size for p in unused)
    print()
    print(f"  {len(files)} icon files on disk")
    print(f"  {len(unused)} referenced by NOTHING  "
          f"({total_bytes/1024/1024:.1f} MB)")
    print()
    for d in sorted(by_dir, key=lambda k: -len(by_dir[k])):
        group = by_dir[d]
        size = sum(p.stat().st_size for p in group) / 1024 / 1024
        print(f"      {len(group):5d}  {d}   ({size:.1f} MB)")
    print()

    if args.list:
        for p in unused:
            print("   ", p.relative_to(ROOT).as_posix())
        print()
    if args.write_list:
        out = Path(args.write_list)
        out.write_text("\n".join(p.relative_to(ROOT).as_posix() for p in unused) + "\n", encoding="utf-8")
        print(f"  wrote {len(unused)} paths to {out}")
        print()

    print("  Nothing was deleted. This tool only reports - review the list,")
    print("  then delete explicitly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
