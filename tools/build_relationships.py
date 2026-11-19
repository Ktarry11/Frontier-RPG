#!/usr/bin/env python3
"""Wave 3: how the recruits get on. Builds data/npcs/relationships.json from tools/wave3/.

    PYTHONPATH=. python3 tools/build_relationships.py            # check, then write
    PYTHONPATH=. python3 tools/build_relationships.py --check    # check only
    PYTHONPATH=. python3 tools/build_relationships.py --strict   # also fail on anyone unfinished

One file per recruit, tools/wave3/<recruit_id>.json:

  traits   talk (quiet, middle, talker), humour (joker, dry, earnest), manner (blunt, gentle,
           formal), pace (careful, steady, bold); "is" (what other people notice about them, from
           DESCRIPTORS); likes and dislikes (descriptors they warm to or can't stand in somebody
           else); tags (common ground from Earth, from TAGS, and each needs a common_<tag> line);
           warm_to, wary_of and spar (recruits their profile names: spar is a pair who argue
           and enjoy it). world/relationship_manager.py turns all that into chemistry.
  lines    the recruit's own pool, one line per key in KEYS (relationship_manager.py says what
           each key is for), plus common_<tag> for each tag.

tools/wave3/_pairs.json holds the signature arcs: hand-written exchanges for the pairs whose
profiles name each other. Those lines may name each other; nothing else may.

Kyle's rules from Wave 2 hold, and the checker enforces them: plain speech, contractions, no one or
two word sentences, no dashes, no stage asides, none of the stock phrases. And three of his for
Wave 3: neighbours start on nodding terms, {name} only once they're friendly, no romance. Lines
also have to stay true before and after the recruit's own story ends, because they can be said at
any stage of it: talk about the people you miss, not about whether you've found them.

Two things the checker can't see, so they're written down here. A reaction (bite_back, hurt,
laugh_off, accept, deflect, tease_back, take_it_kindly, bristle, listen, brush_off) has to fit
anything it might be answering: laugh_off follows a dig about talking too much as easily as one
about being reckless, and accept follows "stay behind me" as well as "are you hurt". And a line
that can be said to every friend they make can't claim to be rare ("I don't say that often").
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from world.relationship_manager import KEYS, NAMED  # noqa: E402
from tools.wave2_text import TICS, STOP  # noqa: E402

SRC = ROOT / "tools" / "wave3"
OUT = ROOT / "data" / "npcs" / "relationships.json"
NEVER_TOUCH = {"asher_coleman"}

TALK, HUMOUR, MANNER, PACE = {"quiet", "middle", "talker"}, {"joker", "dry", "earnest"}, \
    {"blunt", "gentle", "formal"}, {"careful", "steady", "bold"}
DESCRIPTORS = {"healer", "showoff", "pious", "cynic", "sentimental", "worker", "maker", "artist",
               "scholar", "outdoors", "fighter", "host", "posh", "young", "elder", "sarcastic",
               "competitive", "honest", "patient", "teacher", "musician", "sporty", "bossy",
               "macabre", "easygoing",
               # the ones traits give them (relationship_manager.described)
               "loud", "quiet", "careful", "reckless", "funny", "dry", "earnest", "blunt",
               "gentle", "formal"}
TAGS = {"parent", "spanish", "medic", "arabic", "night_work", "teacher", "sport", "animals",
        "machines", "numbers", "rescue", "portuguese", "kitchen", "hosts", "road", "chile", "wild",
        "sky", "mexico", "desert", "craft", "scandinavian", "snow", "growing", "blood", "boats",
        "radiation", "venom", "mountains", "brazil", "faith", "italian", "american", "music", "fel",
        "fire_crew", "ring", "birds", "north_england", "factory", "aussie", "stone", "the_dark",
        "scots", "ukrainian", "locks", "turkish", "names", "ex_scarlet", "greek", "irish", "docks",
        "engineers", "welsh", "polish"}
#: lines that can come first or second in a beat, so they can't open like a reply
EITHER_WAY = ("meet", "meet_neighbour", "chat_", "common_", "turn_", "make_up")
REPLY_START = re.compile(r"^(same|me too|me neither|so do|so did|so am|likewise|you too|and me|"
                         r"snap|ha|that too|that's true)\b", re.I)
#: words for "you" that change with who's listening. In a line said to another recruit they go in a
#: {man's form|woman's form} pair, which world/relationship_manager.py fills in by the listener.
GENDERED = re.compile(r"\b(bloke|lad|lass|mijo|mija|hermano|hermana|irmão|irmã|abi|abla|habibi|habibti|"
                      r"compadre|comadre|chico|chica|carnal|carnala|querido|querida|ragazzo|ragazza|uagliò|bello|bella|"
                      r"basha|hanem|nene|nena|my man|my boy|my girl|sir|madam|ma'am|"
                      r"son|brother|sister|mate)\b(?![^{]*\})", re.I)
#: these are said about somebody, or to the party, so there's nobody to match a form to
NO_ADDRESS = ("defend", "friend_left")
#: "mate", "brother" and "son" are everywhere in ordinary speech about other people, so they only
#: count when they're plainly said to the listener: at the start of the line or after a comma
ADDRESSED = re.compile(r"(^|[,.!?] )(son|brother|sister)\b|, (son|brother|sister)[,.!?]", re.I)
ROMANCE = re.compile(r"\b(kiss|darling|sweetheart|gorgeous|handsome|date with|fancy you|"
                     r"in love with you|my love)\b", re.I)


def load():
    out = {}
    for p in sorted(SRC.glob("*.json")):
        if not p.stem.startswith("_"):
            out[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    return out


def load_pairs():
    p = SRC / "_pairs.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def _texts(lines):
    for k, t in lines.items():
        for x in (t if isinstance(t, list) else [t]):
            yield k, x


def problems(data=None, pairs=None, strict=False):
    from tools.build_tempest_quests import voice_problems
    data = load() if data is None else data
    pairs = load_pairs() if pairs is None else pairs
    recruits = json.loads((ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))["recruits"]
    names = {r["recruit_id"]: r["name"].split()[0] for r in recruits}
    bad, unfinished = [], []
    runs, openers = {}, {}
    for rid, d in data.items():
        if rid not in names or rid in NEVER_TOUCH:
            bad.append(f"{rid}: not a Wave 3 recruit")
            continue
        t = d.get("traits", {})
        for k, allowed in (("talk", TALK), ("humour", HUMOUR), ("manner", MANNER), ("pace", PACE)):
            if t.get(k) not in allowed:
                bad.append(f"{rid}: {k} {t.get(k)!r}")
        for k in ("is", "likes", "dislikes"):
            for x in t.get(k, []):
                if x not in DESCRIPTORS:
                    bad.append(f"{rid}: unknown descriptor {x} in {k}")
        for x in t.get("tags", []):
            if x not in TAGS:
                bad.append(f"{rid}: unknown tag {x}")
        for k in ("warm_to", "wary_of", "spar"):
            for x in t.get(k, []):
                if x not in data:
                    bad.append(f"{rid}: {k} names {x}, who has no Wave 3 file")
        lines = d.get("lines", {})
        wanted = list(KEYS) + [f"common_{x}" for x in t.get("tags", [])]
        missing = [k for k in wanted if not lines.get(k)]
        if missing and lines:
            unfinished.append(f"{rid}: missing {', '.join(missing)}")
        elif missing:
            unfinished.append(f"{rid}: no lines yet")
        others = {first for oid, first in names.items() if oid != rid and first != names[rid]}
        for k, x in _texts(lines):
            where = f"{rid} {k}"
            if k not in wanted:
                bad.append(f"{where}: unknown key")
            flat = re.sub(r"\{([^{}|]+)\|[^{}|]+\}", r"\1", x)
            bad += [f"{where}: {p}" for p in voice_problems(flat.replace("{name}", "Sam"))]
            for m in GENDERED.finditer(x):
                w = m.group(1).lower()
                if w in ("son", "brother", "sister") and not ADDRESSED.search(x):
                    continue
                if w == "mate":
                    continue        # Aussie and Cumbrian "mate" is the same for everybody
                bad.append(f"{where}: {m.group(1)!r} changes with who's listening, use {{{w}|...}}")
            if "|" in x and k in NO_ADDRESS:
                bad.append(f"{where}: a {{his|hers}} form in a line said about somebody else")
            if "—" in x or " - " in x or "–" in x:
                bad.append(f"{where}: a dash")
            if "{name}" in x and k not in NAMED:
                bad.append(f"{where}: {{name}} in a key that can be said before they're friendly")
            if x.count("{name}") > 1:
                bad.append(f"{where}: {{name}} twice")
            if re.search(r"\{(?!name\}|[^{}|]+\|[^{}|]+\})", x):
                bad.append(f"{where}: a stray brace")
            hit = others & set(re.findall(r"[A-ZÀ-Ý][\w'À-ÿ-]+", x))
            if hit:
                bad.append(f"{where}: names another recruit {sorted(hit)}")
            if k.startswith(EITHER_WAY) and REPLY_START.search(x):
                bad.append(f"{where}: opens like a reply, and this key can come first: {x!r}")
            if ROMANCE.search(x):
                bad.append(f"{where}: reads as romance (Kyle: leave it out): {x!r}")
            for rx, why in TICS:
                if re.search(rx, x, re.I):
                    bad.append(f"{where}: {why}: {x!r}")
            w = re.findall(r"[\w']+", x.lower().replace("{name}", "NAME"))
            for g in {" ".join(w[i:i + 4]) for i in range(len(w) - 3)}:
                if sum(y not in STOP and y != "name" for y in g.split()) >= 2:
                    runs.setdefault(g, set()).add(rid)
                    runs.setdefault((k.split("_")[0], g), set()).add(rid)
            openers.setdefault((k, " ".join(w[:3])), set()).add(rid)
    # Ninety-eight people will share some ordinary English, so these are about what a player
    # would notice: the same phrase from eight different mouths, the same phrase doing the same
    # job for five, or five people opening the same kind of line the same way. Questions get more
    # room, because "where are you from" is what people say.
    for g, rids in sorted(runs.items(), key=str):
        limit = 8 if isinstance(g, str) else 5
        if len(rids) >= limit:
            bad.append(f"shared by {len(rids)} recruits: {g!r} ({', '.join(sorted(rids))})")
    for (k, g), rids in sorted(openers.items()):
        if len(rids) >= (8 if k.startswith(("ask_", "answer_")) else 5) and len(g.split()) == 3:
            bad.append(f"{k} opens the same way for {len(rids)} recruits: {g!r} ({', '.join(sorted(rids))})")
    seen = set()
    for p in pairs:
        key = "|".join(sorted((p["a"], p["b"])))
        if key in seen:
            bad.append(f"signature {key}: twice")
        seen.add(key)
        for who in (p["a"], p["b"]):
            if who not in data:
                bad.append(f"signature {key}: {who} has no Wave 3 file")
        for i, s in enumerate(p.get("steps", [])):
            w = s.get("when", "met")
            if not re.fullmatch(r"met|friendly|close|grating|(outings|gap):\d+", w):
                bad.append(f"signature {key} step {i}: unknown when {w!r}")
            for who, x in s["lines"]:
                if who not in (p["a"], p["b"]):
                    bad.append(f"signature {key} step {i}: {who} isn't in this pair")
                bad += [f"signature {key} step {i}: {q}" for q in voice_problems(x)]
                if "—" in x or " - " in x:
                    bad.append(f"signature {key} step {i}: a dash")
                if ROMANCE.search(x):
                    bad.append(f"signature {key} step {i}: reads as romance")
                outsiders = {names[o] for o in names if o not in (p["a"], p["b"])} - \
                    {names[p["a"]], names[p["b"]]}
                hit = outsiders & set(re.findall(r"[A-ZÀ-Ý][\w'À-ÿ-]+", x))
                if hit:
                    bad.append(f"signature {key} step {i}: names somebody outside the pair {sorted(hit)}")
    if strict:
        bad += unfinished
    return bad, unfinished


def build(data, pairs):
    return {"_about": "Wave 3, how the recruits get on. Written by tools/build_relationships.py from "
                      "tools/wave3/; read by world/relationship_manager.py.",
            "traits": {rid: d["traits"] for rid, d in data.items()},
            "lines": {rid: d.get("lines", {}) for rid, d in data.items() if d.get("lines")},
            "pairs": pairs}


def main(argv):
    data, pairs = load(), load_pairs()
    bad, unfinished = problems(data, pairs, strict="--strict" in argv)
    for b in bad:
        print("  -", b)
    done = len(data) - len(unfinished)
    print(f"{len(data)} recruits, {done} with every line written, {len(pairs)} signature pairs, "
          f"{len(bad)} problems")
    if bad:
        return 1
    if "--check" not in argv:
        OUT.write_text(json.dumps(build(data, pairs), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"-> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
