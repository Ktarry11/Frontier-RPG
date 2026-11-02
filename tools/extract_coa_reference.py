#!/usr/bin/env python3
"""
Turn the 7,378 CoA reference screenshots into greppable structured data.

    PYTHONPATH=. python3 tools/extract_coa_reference.py manifest
    PYTHONPATH=. python3 tools/extract_coa_reference.py index  [--limit N] [--every N]
    PYTHONPATH=. python3 tools/extract_coa_reference.py tips   --class Primalist

Source: https://postimg.cc/gallery/NfWbcjv - every skill and every talent of all 21 CoA classes,
captured in-game. See claude/coa_reference_screenshots.md.

WHY OCR AND NOT A MODEL LOOKING AT PICTURES. 7,378 images read one at a time is the wrong shape
of job at any price. Every shot is the SAME screen - the Character Advancement panel, class name
top-left, spec name top-right, one tooltip under the cursor - so the variable part is small and
machine-readable. The expensive step becomes CPU in the sandbox and the output is a file we keep.

THREE THINGS MAKE THIS WORK, AND ALL THREE ARE ABOUT NOT TRUSTING OCR:

  1. THE HEADER IS A CLOSED VOCABULARY. We already know all 29 classes and their spec names -
     they are the filenames in data/talents/. So the header OCR does not have to be right, it has
     to be CLOSE, and difflib picks the real one. "STORMBRING Ahi" and "MAEL ST wn" both resolve
     correctly, and that is the normal quality of a big gold word sitting on painted artwork.

  2. THE TOOLTIP IS FOUND, NOT CROPPED. It follows the cursor, so a fixed crop gets the wrong
     part of the screen on most shots. It is also the only large near-uniform dark rectangle on
     the panel, which makes it findable: threshold, label, take the biggest component with
     tooltip-ish proportions.

  3. THE TOOLTIP IS READ INVERTED. Tesseract assumes dark text on light. These are light text on
     a near-black box, and raw tesseract on the full screenshot returns the HUD and nothing else.
     Crop, upscale 5x, invert, threshold - then the body text comes out essentially clean.

STAGES, because the whole set is ~1.9GB and you want to be able to stop:

  manifest  one request. postimg's ?page=N is CUMULATIVE, so ?page=200 returns every image in
            the gallery at once and pages past the end return byte-identical HTML - which is how
            the total was pinned at 7,378 rather than guessed.
  index     download + read the header only. Cheap per image, and it answers "which shots are
            Primalist", which is what you need before processing anything.
  tips      the real work: find the tooltip, read it, parse it into fields.
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

GALLERY = "https://postimg.cc/gallery/NfWbcjv?page=200"
WORK = Path(os.environ.get("COA_WORK", "/tmp/claude-0/coa"))
IMG = WORK / "img"
MANIFEST = WORK / "manifest.json"
INDEX = WORK / "index.json"
OUT = ROOT / "data/reference/coa_abilities.json"

#: THE CLASS IS IN THE CHARACTER NAME, and that is the single most useful thing about this
#: gallery. Whoever captured it rolled one character per class and named them all "Adunai" plus
#: the class - Adunaipyro, Adunaiprimal, Adunaicult, Adunaitinker. The name plate is at fixed
#: coordinates in the top-left of EVERY shot whatever screen is open, so it works on the trainer
#: window, the talent panel and the character pane alike.
#:
#: The first attempt read the class off the talent panel's header instead and resolved 16% of
#: shots, because most of the gallery is not the talent panel at all - it is the trainer window,
#: which has no header. Tight crop, 8x upscale, invert, threshold 130: the plate is gold on near
#: black and anything looser picks up the portrait frame beside it.
NAME_BOX = (76, 22, 172, 38)
#: Every way the OCR has actually rendered "Adunai" in this gallery. The capital I is the problem
#: child - it comes back as l, r, : or nothing at all depending on the threshold.
NAME_PREFIXES = ("adunai", "adunal", "adunar", "aduna", "aduaa", "adua", "ndua", "acuinai",
                 "aglaal", "agena", "aglna", "aclna")
#: ONE THRESHOLD IS NOT ENOUGH. The plate sits over whatever the 3D scene is doing behind it, so
#: the brightness that separates gold lettering from background moves between shots. 130 resolved
#: 42% of the sample; walking these four and taking the first that matches a real class resolves
#: nearly all of it, and costs an extra tesseract call only on the ones that would have failed.
NAME_THRESHOLDS = (150, 170, 130, 190)

#: Talent-panel header. Present only on talent shots - used for the SPEC, which the name cannot
#: give, since one character covers all of that class's trees.
CLASS_BOX = (250, 116, 600, 152)
SPEC_BOX = (720, 116, 1030, 152)
#: The talent panel's interior. The tooltip never leaves it.
PANEL = (180, 110, 1105, 525)
#: The trainer window's interior, which is where that screen's tooltip lives instead.
TRAINER = (14, 90, 290, 430)


def _vocab():
    """(classes, specs) as the game spells them - the closed vocabulary the OCR is matched to."""
    classes, specs = set(), set()
    for p in sorted((ROOT / "data/talents").glob("*.json")):
        spec = json.loads(p.read_text()).get("spec_name") or ""
        if not spec:
            continue
        specs.add(spec)
        # "Knight of Xoroth Defiance" -> class is the longest known prefix; derived rather than
        # split on whitespace, because four classes have multi-word names.
        classes.add(spec)
    known = ["Knight of Xoroth", "Sun Cleric", "Witch Doctor", "Witch Hunter"]
    out = set(known)
    for s in specs:
        if not any(s.startswith(k) for k in known):
            out.add(s.split()[0])
    return sorted(out), sorted(specs)


def _best(text, options, floor=0.45):
    """The closest member of a closed vocabulary, or None. OCR noise is expected and fine."""
    t = re.sub(r"[^A-Za-z ]", " ", (text or "")).strip().lower()
    t = re.sub(r"\s+", " ", t)
    if len(t) < 3:
        return None
    best, score = None, 0.0
    for o in options:
        s = SequenceMatcher(None, t, o.lower()).ratio()
        # A short OCR fragment of a long name ("MAEL ST wn" vs "Stormbringer Maelstrom") scores
        # badly on whole-string ratio but is a strong partial - so take the better of the two.
        s = max(s, SequenceMatcher(None, t, o.lower().split()[-1]).ratio())
        if s > score:
            best, score = o, s
    return best if score >= floor else None


def _class_from_name(text, classes):
    """The class, from the character-name plate. 'Adunaiprimal' -> 'Primalist'.

    The OCR of a 10px gold plate is never clean - real output includes 'Adunarcult',
    'Acuinaivena' and 'Adunaritinker'. So the prefix is stripped loosely and the REMAINDER is
    matched against the class list by prefix overlap rather than whole-string similarity, since
    the capture names are abbreviations ('veno' for Venomancer, 'primal' for Primalist) and a
    whole-string ratio punishes exactly the thing that makes them recognisable.
    """
    t = re.sub(r"[^A-Za-z]", "", (text or "")).lower()
    for p in NAME_PREFIXES:
        i = t.find(p)
        if i >= 0:
            t = t[i + len(p):]
            break
    else:
        # the prefix itself was mangled; drop a leading 'a...' run of ~6 chars and hope
        t = t[6:] if len(t) > 8 else t
    t = t.strip()
    if len(t) < 3:
        return None
    best, score = None, 0.0
    for c in classes:
        key = re.sub(r"[^a-z]", "", c.lower())
        n = 0
        while n < min(len(t), len(key)) and t[n] == key[n]:
            n += 1
        s = n / max(3, min(len(t), len(key)))
        s = max(s, SequenceMatcher(None, t, key).ratio())
        if s > score:
            best, score = c, s
    return best if score >= 0.6 else None


def _ocr(img, psm="7", invert=True, thresh=120, scale=4):
    from PIL import ImageOps
    img = img.resize((img.width * scale, img.height * scale))
    if invert:
        img = ImageOps.invert(img)
    img = img.point(lambda p: 255 if p > thresh else 0)
    # A FIXED TEMP PATH IS A RACE. Two of these running at once - an index pass in the
    # background and a tips pass in the foreground, which is exactly how this gets used - both
    # wrote to WORK/_ocr.png and read each other's half-written image. It does not error: OCR
    # just returns empty, which reads as "no tooltip here" and silently drops real data.
    tmp = WORK / f"_ocr_{os.getpid()}.png"
    try:
        img.save(tmp)
        r = subprocess.run(["tesseract", str(tmp), "-", "--psm", psm],
                           capture_output=True, text=True)
        return r.stdout.strip()
    finally:
        tmp.unlink(missing_ok=True)


# ------------------------------------------------------------------------------------ manifest
def stage_manifest():
    WORK.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(GALLERY, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=180).read().decode("utf-8", "replace")
    urls = re.findall(r"https://i\.postimg\.cc/[A-Za-z0-9]+/(Wo-WScrn-Shot-[0-9-]+\.jpg)", html)
    full = re.findall(r"(https://i\.postimg\.cc/[A-Za-z0-9]+/Wo-WScrn-Shot-[0-9-]+\.jpg)", html)
    by_name = {}
    for u in full:
        by_name.setdefault(u.rsplit("/", 1)[1], []).append(u)
    # TWO URLs PER IMAGE - a thumbnail and the full size, distinguished only by the hash in the
    # path. There is no size marker to sort on, so both are kept and the downloader takes
    # whichever comes back larger. A thumbnail is ~8KB and OCRs to nothing.
    rows = [{"name": n, "urls": sorted(set(v))} for n, v in sorted(by_name.items())]
    MANIFEST.write_text(json.dumps(rows, indent=1))
    print(f"{len(rows)} images ({len(set(full))} urls, {len(urls)} refs) -> {MANIFEST}")
    return 0


def _fetch(row):
    """Download the biggest variant. Returns the local path, or None."""
    IMG.mkdir(parents=True, exist_ok=True)
    dest = IMG / row["name"]
    if dest.exists() and dest.stat().st_size > 50_000:
        return dest
    best = b""
    for u in row["urls"]:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=40).read()
        except Exception:
            continue
        if len(data) > len(best):
            best = data
        if len(best) > 50_000:
            break
    if not best:
        return None
    dest.write_bytes(best)
    return dest


# --------------------------------------------------------------------------------------- index
def stage_index(limit=None, every=1):
    from PIL import Image
    rows = json.loads(MANIFEST.read_text())
    classes, specs = _vocab()
    rows = rows[::every][:limit] if limit else rows[::every]
    index = json.loads(INDEX.read_text()) if INDEX.exists() else {}
    done = 0
    for row in rows:
        if row["name"] in index:
            continue
        p = _fetch(row)
        if not p:
            continue
        im = Image.open(p).convert("L")
        cls = None
        for th in NAME_THRESHOLDS:
            cls = _class_from_name(_ocr(im.crop(NAME_BOX), thresh=th, scale=8), classes)
            if cls:
                break
        # The spec header only exists on talent shots; on a trainer shot it reads as nothing,
        # which is the correct answer rather than a failure.
        spec = _best(_ocr(im.crop(SPEC_BOX)), specs)
        if spec and cls and not spec.lower().startswith(cls.lower()):
            spec = None       # header matched a different class's tree: trust the name plate
        index[row["name"]] = {"class": cls, "spec": spec}
        done += 1
        if done % 25 == 0:
            INDEX.write_text(json.dumps(index, indent=1))
            print(f"  indexed {done}/{len(rows)}", flush=True)
    INDEX.write_text(json.dumps(index, indent=1))
    hit = sum(1 for v in index.values() if v["class"])
    print(f"{len(index)} indexed, {hit} with a class ({100 * hit / max(1, len(index)):.0f}%)")
    from collections import Counter
    for c, n in Counter(v["class"] for v in index.values()).most_common():
        print(f"  {str(c):26} {n}")
    return 0


# ---------------------------------------------------------------------------------------- tips
def find_tooltip(im):
    """(box) of the tooltip, or None.

    The tooltip is the only large near-uniform DARK rectangle inside the panel. Everything else
    in there is painted artwork and icon grid, both of which are busy. So: threshold hard, label,
    and take the biggest component whose bounding box is tooltip-shaped.
    """
    import numpy as np
    from scipy import ndimage
    # SEARCH THE WHOLE FRAME, not one panel. The gallery is mostly the TRAINER window, whose
    # tooltip sits far left at x~53 - outside the talent panel entirely. Searching only the
    # talent panel found nothing on the majority of shots.
    a = np.asarray(im, dtype=np.uint8)
    mask = a < 62
    lab, n = ndimage.label(mask)
    if not n:
        return None
    best, best_area = None, 0
    for sl in ndimage.find_objects(lab):
        y, x = sl
        h, w = y.stop - y.start, x.stop - x.start
        # The unbounded dark background connects across the whole image and comes out as one
        # 1280x720 component; the size cap is what rejects it.
        if w < 110 or h < 38 or w > 430 or h > 340:
            continue
        if y.start > 640 or y.stop < 60:      # action bar / top HUD, never a tooltip
            continue
        if mask[sl].mean() < 0.55:            # a real box is mostly filled; icon shadow is not
            continue
        if w * h > best_area:
            best, best_area = (x.start, y.start, x.stop, y.stop), w * h
    return best


#: OCR TURNS DIGITS INTO LETTERS in this font: 0 reads as O, 1 as I or l, 5 as S. Real output
#: from this gallery includes "1S yd range" and "1O Heat Each Tick". Every numeric pattern below
#: therefore accepts the letters too, and _num puts them back before the value is stored -
#: writing the regexes with \d alone silently dropped about a third of the ranges and costs.
_DC = r"0-9OISl|iB"       # the CONTENT of a digit character class, no brackets. The pipe and
                          # the lowercase i are how this font's "1" comes back; B is its "8".
_D = f"[{_DC}]"           # ...and the class itself. Nesting the second inside another [...]
                          # builds "[[0-9OISl],]", which Python warns about and matches wrong.
_COST = re.compile(rf"({_D}[{_DC},]*)\s*(Mana|Rage|Energy|Focus|Runic Power|Fury)\b", re.I)
_RANGE = re.compile(rf"({_D}+)\s*yd\s*range", re.I)
_CAST = re.compile(rf"(Instant cast|Channeled|[{_DC}.]+\s*sec cast)", re.I)
_CD = re.compile(rf"([{_DC}.]+\s*(?:sec|min|hr)s?)\s*cooldown", re.I)
_RANK = re.compile(rf"Rank\s*({_D}+)\s*/\s*({_D}+)", re.I)
#: SUBSTITUTIONS THIS FONT FORCES. The percent sign is the one that matters: tesseract reads it
#: as a degree sign almost every time, and "increases your damage by 20°" is the exact sentence
#: this whole extraction exists to count. Losing it would have made every scaling talent in the
#: archive unreadable to a grep for '%'.
_SUBS = ((" thames", " flames"), ("thame", "flame"), ("Thame", "Flame"),
         ("°", "%"), ("º", "%"), ("•", "%"))


def _num(s):
    out = (s or "")
    for a, b in (("O", "0"), ("I", "1"), ("l", "1"), ("|", "1"), ("i", "1"),
                 ("S", "5"), ("B", "8")):
        out = out.replace(a, b)
    return out


def parse_tip(text):
    """The tooltip's fields. Everything is optional - a talent has no cost or range."""
    for bad, good in _SUBS:
        text = text.replace(bad, good)
    # "Rank 0/1" is often the LAST thing on a line rather than its own line, and the OCR spaces
    # it oddly ("Rank O/ |"). Pull it out wherever it sits so it stops polluting the effect text.
    text = _RANK.sub(lambda m: f"\nRank {_num(m.group(1))}/{_num(m.group(2))}\n", text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # Drop OCR crust: lines that are mostly punctuation are crop-edge noise, not content.
    lines = [l for l in lines if sum(c.isalnum() for c in l) >= max(3, len(l) * 0.5)]
    if not lines:
        return None
    rec = {"name": lines[0], "cost": None, "range": None, "cast": None,
           "cooldown": None, "rank": None, "text": ""}
    body = []
    for l in lines[1:]:
        m = _COST.search(l)
        if m:
            rec["cost"] = f"{_num(m.group(1))} {m.group(2)}"
        m = _RANGE.search(l)
        if m:
            rec["range"] = f"{_num(m.group(1))} yd"
        m = _CAST.search(l)
        if m:
            cast = m.group(1).strip()
            # "Instant" and "Channeled" are WORDS, not numbers. Repairing them turned "Instant
            # cast" into "1nstant cast", because I is how this font writes 1.
            if re.match(r"(?i)instant|channel", cast):
                rec["cast"] = cast
            else:
                head = re.match(rf"[{_DC}.]+", cast)
                rec["cast"] = (_num(head.group(0)) + cast[head.end():]) if head else cast
        m = _CD.search(l)
        if m:
            # REPAIR THE NUMBER, NOT THE UNIT. _num maps i->1 because this font renders 1 that
            # way, so running it over the whole capture turned "2.5 min" into "2.5 m1n".
            cd = m.group(1).strip()
            head = re.match(rf"[{_DC}.]+", cd)
            rec["cooldown"] = (_num(head.group(0)) + cd[head.end():]) if head else cd
        m = _RANK.search(l)
        if m:
            rec["rank"] = f"{_num(m.group(1))}/{_num(m.group(2))}"
            continue
        if not (_COST.search(l) or _RANGE.search(l) or _CAST.search(l) or _CD.search(l)):
            body.append(l)
    # Mixed-case tokens that are MOSTLY digits are numbers the OCR mangled - "1O" for 10, "35O"
    # for 350. Only converted when digits already outnumber letters, so real words are left
    # alone: a blanket O->0 across the body turns "Of" into "0f" and ruins the effect text.
    def fix_token(w):
        core = w.strip(".,;:()%")
        if len(core) >= 2 and sum(c.isdigit() for c in core) >= len(core) - 1 \
                and any(c.isdigit() for c in core) and not core.isdigit():
            return w.replace(core, _num(core))
        return w
    rec["text"] = " ".join(fix_token(w) for w in " ".join(body).split())
    return rec


#: The trainer's collapsible tree list, top-left. Fixed position - the window does not move.
TREE_LIST = (18, 160, 290, 320)


def spec_from_list(im, specs, cls=None):
    """The spec, read off the trainer's tree list - the ONE place that actually states it.

    The list shows every tree with a +/- marker and exactly one of them expanded:

        + Geomancy
        + Grovekeeper
        - Mountain King          <- the open one, and the one these entries belong to
          Mountain Hammer ...

    This replaces reading the "Requires:" line, which was the wrong field and said so in the
    data: in CoA a talent in one tree can require points in ANOTHER, so Mountain King entries
    cite "Geomancy (1)" perfectly correctly and the inference came out with 9 Mountain King
    talents against 76 Geomancy ones. Prerequisites describe what you need; the expanded header
    describes where you are.
    """
    text = _ocr(im.crop(TREE_LIST), psm="6", thresh=150, scale=4)
    pool = [s for s in specs if not cls or s.lower().startswith(cls.lower())] or specs
    expanded, collapsed = None, set()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # The marker is the first glyph; OCR renders minus as -, em dash or ~, plus as + or *.
        mark, rest = line[0], line[1:].strip()
        hit = _best(rest, pool, floor=0.7)
        if not hit:
            continue
        if mark in "+*":
            collapsed.add(hit)
        elif mark in "-—–~_" and expanded is None:
            expanded = hit
    if expanded:
        return expanded
    # Only one tree is ever open, so if every tree but one read as collapsed, the remaining one
    # is the open one even when its own marker was lost to OCR.
    rest = [s for s in pool if s not in collapsed]
    return rest[0] if len(rest) == 1 and collapsed else None


def spec_from_requires(im, box, specs, cls=None):
    """The spec, read off the trainer's 'Requires:' line under the tooltip.

    The trainer window prints "Requires: Level 16, Wildwalker (1), Wildclaw (Rank 2)" in a detail
    panel below the hovered entry, and the tree name in the middle of that is the spec. This is
    DIRECT evidence, unlike the ordering, so it is tried first and the ordering fills the gaps.

    The level number is usually lost - it is drawn in gold and thresholds away - but the spec
    name is plain text and comes through.
    """
    reg = (14, box[3], min(320, box[2] + 50), box[3] + 80)
    if reg[3] > im.height or reg[1] >= reg[3]:
        return None
    text = _ocr(im.crop(reg), psm="6", thresh=150, scale=5)
    m = re.search(r"Requires?\s*:(.{0,90})", text, re.I | re.S)
    if not m:
        return None
    # Only consider this class's own trees when the class is known - "Wildwalker" is unique but
    # "Holy" and "Protection" are not, and a cross-class match would be worse than no answer.
    pool = [s for s in specs if not cls or s.lower().startswith(cls.lower())] or specs
    for chunk in re.split(r"[,.()]", m.group(1)):
        chunk = chunk.strip()
        if len(chunk) < 4 or re.match(r"(?i)level", chunk):
            continue
        hit = _best(chunk, pool, floor=0.6)
        if hit:
            return hit
    return None


def fill_by_order(seq):
    """Give every shot a spec by CONTIGUITY, from the ones that read a Requires line.

    Kyle, 2026-11-01: "we can SEE what is what based on the order. like it goes through each
    tree, then into things like wildwalker. then the next series are wildwalker skills" - and he
    is right. The trainer list is expanded ONE TREE AT A TIME (Geomancy, Grovekeeper, Mountain
    King, Wildwalker) and every entry under it is screenshotted before the next is opened, so a
    run of consecutive shots is a single tree.

    THE ORDER IS THE PRIMARY SIGNAL AND THE REQUIRES LINE IS THE NOISY ONE, which is the
    opposite of how this was first built. The Requires line lists PREREQUISITES, and in CoA a
    talent in one tree can require points in another - so a Mountain King entry whose line reads
    "Geomancy (1)" is not mislabelled by OCR, it is correctly reporting a prerequisite that is
    not its own tree. Trusting it per-shot produced a stretch of Primalist alternating
    Geomancy/Mountain King one or two shots at a time, which no real capture would do.

    So: segment the sequence into runs by Kyle's ordering, then let each run VOTE on its tree
    using whatever Requires lines fall inside it. A run is one tree by construction; the
    majority reading inside it is that tree, and a single contrary prerequisite cannot outvote
    the rest of the run.

    A MODE FILTER, NOT GAP DETECTION. The first attempt segmented on pauses in the shot
    timestamps, on the theory that changing tree means stopping to collapse one list and expand
    the next. It splits far too often - the capturer also pauses mid-tree - and shattered each
    tree into a dozen fragments separated by unlabelled shots.

    The signal's real shape is piecewise-constant with isolated noise: long stretches of one
    tree, with the occasional shot misread or unread. That is exactly what a sliding-window mode
    filter is for. Each position takes the most common direct reading within +/-W of it, so a
    lone contrary shot is outvoted by its neighbours and a gap is filled by whatever surrounds
    it, without anyone having to guess where the boundaries are.
    """
    import collections
    W = 8
    direct = [s for _sh, s in seq]
    out = []
    for i in range(len(direct)):
        window = [s for s in direct[max(0, i - W):i + W + 1] if s]
        out.append(collections.Counter(window).most_common(1)[0][0] if window else None)
    return out


def class_blocks(index, all_names):
    """Infer each shot's class from the sampled index by CONTIGUITY.

    The capture is one character at a time and the filenames are timestamps, so shots of the same
    class sit in an unbroken run. A sampled index at stride 20 therefore pins the class of 5% of
    the gallery directly and implies the rest: any shot between two samples of the same class
    belongs to that class.

    This is what makes "process only Primalist" affordable. Indexing all 7,378 shots to find the
    ~400 Primalist ones means downloading the entire 1.9GB first, which is the thing the staging
    exists to avoid.
    """
    known = [(n, index[n]["class"]) for n in all_names
             if n in index and index[n].get("class")]
    out = {}
    for i, (name, cls) in enumerate(known):
        lo = known[i - 1][0] if i else all_names[0]
        hi = known[i + 1][0] if i + 1 < len(known) else all_names[-1]
        for n in all_names:
            if lo <= n <= hi:
                # Only claim the gap when BOTH bracketing samples agree; a boundary between two
                # characters is exactly where a wrong guess would land.
                prev_cls = known[i - 1][1] if i else cls
                next_cls = known[i + 1][1] if i + 1 < len(known) else cls
                if n < name and prev_cls != cls:
                    continue
                if n > name and next_cls != cls:
                    continue
                out[n] = cls
    return out


def stage_tips(only_class=None, limit=None):
    from PIL import Image
    index = json.loads(INDEX.read_text())
    rows = {r["name"]: r for r in json.loads(MANIFEST.read_text())}
    all_names = sorted(rows)
    inferred = class_blocks(index, all_names)
    for n, c in inferred.items():
        index.setdefault(n, {"class": None, "spec": None})
        if not index[n].get("class"):
            index[n]["class"] = c
    names = [n for n, v in sorted(index.items())
             if not only_class or (v.get("class") or "").lower() == only_class.lower()]
    if limit:
        names = names[:limit]
    print(f"{len(names)} shots" + (f" for {only_class}" if only_class else ""))

    out, missed = [], 0
    for i, name in enumerate(names, 1):
        p = _fetch(rows[name])
        if not p:
            continue
        im = Image.open(p).convert("L")
        box = find_tooltip(im)
        if not box:
            missed += 1
            continue
        pad = 4
        tip = im.crop((box[0] + pad, box[1] + pad, box[2] - pad, box[3] - pad))
        tip = tip.resize((tip.width * 5, tip.height * 5))
        rec = parse_tip(_ocr(tip, psm="6", thresh=150))
        if not rec:
            missed += 1
            continue
        rec.update(shot=name, **{k: index[name].get(k) for k in ("class", "spec")})
        if not rec.get("spec"):
            # The expanded tree header first - it STATES the tree. The Requires line is a
            # fallback only, and a poor one: it lists prerequisites, which in CoA routinely
            # name a different tree than the talent's own.
            rec["spec"] = (spec_from_list(im, _vocab()[1], rec.get("class"))
                           or spec_from_requires(im, box, _vocab()[1], rec.get("class")))
        # Keep what this shot ITSELF read, before any smoothing. Tuning the fill is otherwise a
        # full re-OCR of the class every time, which is 5 minutes a go for no reason.
        rec["raw_spec"] = rec.get("spec")
        out.append(rec)
        if i % 25 == 0:
            print(f"  {i}/{len(names)}  {rec['name'][:40]}", flush=True)

    # THE ORDER IS EVIDENCE. Fill the specs the Requires line could not read from the shots
    # around them, which works because the capture walks one tree at a time.
    out.sort(key=lambda r: r["shot"])
    filled = fill_by_order([(r["shot"], r.get("raw_spec")) for r in out])
    for r, s in zip(out, filled):
        r["spec"] = s
    direct = sum(1 for r in out if r.get("spec"))

    # One screenshot per talent RANK means the same ability appears many times. Keep the richest
    # version of each (class, spec, name): the one with the most fields filled in.
    best = {}
    for r in out:
        key = (r.get("class"), r.get("spec"), r["name"].lower())
        score = sum(1 for k in ("cost", "range", "cast", "cooldown") if r.get(k)) + len(r["text"]) / 500
        if key not in best or score > best[key][0]:
            best[key] = (score, r)
    recs = [r for _s, r in best.values()]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = {"_notes": "CoA reference abilities and talents, OCR'd from the in-game capture gallery "
                     "by tools/extract_coa_reference.py. Reference material for the class audit - "
                     "NOT game data, and nothing reads it at runtime.",
           "entries": sorted(recs, key=lambda r: (str(r.get("class")), str(r.get("spec")),
                                                  r["name"])),
           # The capture order, kept because it is the evidence the spec inference rests on -
           # if a tree boundary ever looks wrong, this is where you check it.
           "sequence": [{"shot": r["shot"], "spec": r.get("spec"),
                         "raw_spec": r.get("raw_spec"), "name": r["name"]}
                        for r in out]}
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(out)} tooltips read, {missed} with no tooltip found, "
          f"{len(recs)} unique, {direct} with a spec -> {OUT.relative_to(ROOT)}")
    return 0


def main(argv):
    WORK.mkdir(parents=True, exist_ok=True)
    stage = argv[0] if argv else "manifest"
    arg = lambda f, d=None: (argv[argv.index(f) + 1] if f in argv else d)
    if stage == "manifest":
        return stage_manifest()
    if stage == "index":
        return stage_index(limit=int(arg("--limit", 0)) or None,
                           every=int(arg("--every", 1)))
    if stage == "tips":
        return stage_tips(only_class=arg("--class"), limit=int(arg("--limit", 0)) or None)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
