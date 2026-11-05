#!/usr/bin/env python3
"""Shared reader for the Conquest of Azeroth reference data.

    from tools.coa_reference import classes, nodes_for

The reference lives in data/reference/coa/ - one JSON per class, pulled from
Ascension's own live CoA Builder (the same data allthingscoa.com presents),
plus _classes-meta.js mapping each class to its spec tabs.

WHY A SHARED READER. Three separate tools already needed to dedupe these
nodes and resolve tabIds to spec names, and the dedupe is not obvious: every
node appears TWICE, byte-identical, which silently doubled the first talent
count this project produced from this data. One reader means one dedupe and
one tab mapping, rather than three copies that agree until they do not.

NOT the OCR data. data/reference/coa_abilities.json came from the screenshot
pipeline and is lossy; nothing here reads it.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF_DIR = ROOT / "data/reference/coa"
META = REF_DIR / "_classes-meta.js"

#: Every CoA class shares one extra tree on this tab, on top of its specs.
#: Our data model has no equivalent - each of our classes has spec trees only -
#: which is a real part of why our trees carry 69-103 talents against CoA's
#: 117-168.
SHARED_CLASS_TAB = 87


def classes():
    """[{name, slug, classTab, specs:[{name, role, tab}]}] from the meta file.

    Parsed with regex rather than a JS engine: the file is a hand-maintained
    literal with trailing commas and unquoted keys, so json.loads will not
    take it, and pulling in a JS parser for 148 lines is not worth it.
    """
    text = META.read_text()
    out = []
    class_re = re.compile(
        r'\{\s*name:\s*"([^"]+)",\s*slug:\s*"([^"]+)",\s*classTab:\s*(\d+)'
        r'.*?specs:\s*\[(.*?)\]\s*\}', re.S)
    spec_re = re.compile(r'\{\s*name:\s*"([^"]+)",\s*role:\s*"([^"]+)",\s*tab:\s*(\d+)')
    for name, slug, class_tab, spec_blob in class_re.findall(text):
        specs = [{"name": sn, "role": sr, "tab": int(st)}
                 for sn, sr, st in spec_re.findall(spec_blob)]
        out.append({"name": name, "slug": slug,
                    "class_tab": int(class_tab), "specs": specs})
    return out


def clean(html):
    """CoA descriptions carry inline HTML and run-together headers.

    "Bomb Toss Rank 1\\n6% of base mana\\nInstant 8 sec cooldown\\nLob a bomb..."
    arrives as one blob with <span> colour spans through it. Tags are stripped
    and whitespace collapsed; the header lines are deliberately KEPT, because
    cost and cooldown are real information the converter reads.
    """
    if not html:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"</(p|div|li)>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


COA_ICON_DIR = ROOT / "assets/icons/coa"

_ICON_CACHE = None


def _icon_index():
    global _ICON_CACHE
    if _ICON_CACHE is None:
        _ICON_CACHE = {}
        if COA_ICON_DIR.is_dir():
            for path in COA_ICON_DIR.iterdir():
                if path.suffix.lower() == ".png":
                    _ICON_CACHE[path.stem.lower()] = path.name
    return _ICON_CACHE


def icon_slug(name):
    """Filename stem the icon extractor used for a talent/ability name.

    Matched on the NAME, not on the node's iconPath. The extractor named its
    3,478 files after the ability ("a_curse_from_hell.png"), while iconPath
    holds Blizzard's internal art id ("inv_knife_1h_revendrethquest_b_03").
    Joining on iconPath matches 13 of 3,612 nodes; joining on the name
    matches 3,442 of 3,512 - which is the whole difference between having
    authentic art on new talents and having none.
    """
    text = (name or "").lower().replace("'", "_")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def icon_for(name):
    """Icon filename for this talent/ability, or None if we never got one.

    ~70 of CoA's 3,512 names have no extracted icon. They return None rather
    than a guess, so the caller can fall back deliberately instead of
    pointing a talent at the wrong art.
    """
    index = _icon_index()
    stem = icon_slug(name)
    for candidate in (stem, f"a_{stem}", stem.replace("__", "_")):
        if candidate in index:
            return index[candidate]
    return None


def nodes_for(slug):
    """Deduped nodes for one class, as {tab_id: [node, ...]}.

    Deduped on `id`. Every node in this export appears exactly twice; counting
    without deduping is what produced the first (wrong, doubled) talent census
    from this data.
    """
    path = REF_DIR / f"{slug}.json"
    if not path.exists():
        return {}
    seen = {}
    for entry in json.loads(path.read_text()):
        key = entry.get("id")
        if key in seen:
            continue
        seen[key] = entry
    by_tab = {}
    for entry in seen.values():
        by_tab.setdefault(entry.get("tabId"), []).append(entry)
    for rows in by_tab.values():
        rows.sort(key=lambda e: (e.get("y", 0), e.get("x", 0)))
    return by_tab


def summary():
    """One line per class: spec tabs, talent and ability counts."""
    out = []
    for info in classes():
        by_tab = nodes_for(info["slug"])
        if not by_tab:
            continue
        talents = sum(1 for rows in by_tab.values() for n in rows
                      if n.get("entryType") == "Talent")
        abilities = sum(1 for rows in by_tab.values() for n in rows
                        if n.get("entryType") == "Ability")
        out.append({
            "name": info["name"], "slug": info["slug"],
            "specs": [s["name"] for s in info["specs"]],
            "roles": [s["role"] for s in info["specs"]],
            "talents": talents, "abilities": abilities,
            "shared": len(by_tab.get(SHARED_CLASS_TAB, [])),
        })
    return out


if __name__ == "__main__":
    print(f"{'class':<18} {'talents':>7} {'abil':>5} {'shared':>6}  specs")
    for row in summary():
        specs = ", ".join(f"{s} ({r})" for s, r in zip(row["specs"], row["roles"]))
        print(f"{row['name']:<18} {row['talents']:>7} {row['abilities']:>5} "
              f"{row['shared']:>6}  {specs}")
