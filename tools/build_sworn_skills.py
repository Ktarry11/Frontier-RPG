#!/usr/bin/env python3
"""Wave 4: every recruit's Sworn skill, checked and ranked.

    PYTHONPATH=. python3 tools/build_sworn_skills.py [--strict]

Reads tools/wave4/sworn_skills.json (authored, keyed by recruit_id) and writes
data/npcs/sworn_skills.json (what the game reads, through world/personal_kits.py).

Kyle, 19 Nov 2026: "These character traits should be slightly stronger than the other ones.
They still will get 5 ranks when appropriate (lvl 1,15,30,45, and 60)." The other ones are the
personal kits ("character traits"), so a Sworn skill is ranked by the kits' own rule in
tools/rank_kit_abilities.py with every size SWORN times bigger: the last rank of anything that
does damage, heals or shields is set from the class abilities at 60 times TRUMP times SWORN.
Percentage effects keep one rank, as the kits do, and are authored about SWORN times the kits'
matching effects (the check below compares each one against the strongest kit ability of the
same kind).

Kyle's standing rules, checked here for every skill:
  - "no character traits will ever be 'once per fight' they'll usually have 10-15 turn
    cooldowns depending on how strong they are". A Sworn skill is stronger than a trait, so it
    takes 12 to 15.
  - descriptions state the mechanic with its number ("dont give weird ass 'and they dont say
    why'"), and every skill quotes the profile line it came from (the "from" field).
  - Asher is never touched.
Every key must be one the ability loader reads or a personal kit already uses, so nothing is
authored that the engine would silently drop.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
SRC = ROOT / "tools" / "wave4" / "sworn_skills.json"
OUT = ROOT / "data" / "npcs" / "sworn_skills.json"
KITS = ROOT / "data" / "npcs" / "personal_kits.json"

#: how much stronger than a character trait
SWORN = 1.15
COOLDOWN = (12, 15)
EXCLUDED = {"asher_paladin", "asher_coleman", "asher"}
BASE_KEYS = {"ability_id", "name", "from", "engine", "effect_type", "target_type", "resource_type",
             "cooldown", "duration", "stat_mods", "description", "ranks", "is_instant"}
DOC_KEYS = {"from", "engine"}


def loader_keys():
    """Every key combat/abilities._ability_from_data reads, plus every key a personal kit
    already uses (those are proven to load)."""
    src = (ROOT / "combat" / "abilities.py").read_text(encoding="utf-8")
    i = src.index("def _ability_from_data")
    j = src.index("\ndef ", i + 10)
    body = src[i:j]
    keys = set(re.findall(r'entry\.get\("(\w+)"', body)) | set(re.findall(r'entry\["(\w+)"\]', body))
    for tup in re.findall(r"for key in \(([^)]*)\)", body):
        keys |= set(re.findall(r'"(\w+)"', tup))
    kits = json.loads(KITS.read_text(encoding="utf-8"))
    for rid, kit in kits.items():
        if rid.startswith("_"):
            continue
        for a in kit["abilities"]:
            keys |= set(a)
    return keys | BASE_KEYS


def passive_keys():
    kits = json.loads(KITS.read_text(encoding="utf-8"))
    keys = set()
    for rid, kit in kits.items():
        if not rid.startswith("_"):
            keys |= {k for k in (kit.get("passives") or {}) if not k.startswith("_")}
    try:
        from combat.status_effects import StatusEffectMixin
        keys |= set(StatusEffectMixin.STAT_LABELS)
    except Exception:
        pass
    from world.personal_kits import COMBAT_KEYS
    return keys | set(COMBAT_KEYS) | {"_name", "_text", "_from"}


def ranks_for(a, kits):
    """The kits' rank rule, every size SWORN times bigger."""
    import rank_kit_abilities as R
    what = R.grows(a)
    base = dict(a["ranks"][0])
    base["rank"], base["level_req"] = 1, 1
    if not what:
        return [base]
    key = R.kind_of(a)
    ref = R.class_refs().get(key) or R.class_refs().get((key[0], "single")) or 200
    share = R.base_size(a) / max(1, R.group_medians(kits).get(key, R.base_size(a)))
    mult = min(R.HIGH * SWORN, max(R.LOW * SWORN, R.TRUMP * SWORN * share))
    start = R.base_size(a)
    end = int(round(max(start * 3 * SWORN, ref * mult)))
    out = []
    mana = a.get("resource_type") == "mana"
    for i, lvl in enumerate(R.LEVELS):
        size = start + (end - start) * i / 4.0
        r = dict(base)
        r["rank"], r["level_req"] = i + 1, lvl
        if "effect_value" in what:
            r["effect_value"] = int(round(size))
        if "absorb" in what:
            r["absorb"] = int(round(size))
        if "on_damage_hot_potency" in what:
            r["on_damage_hot_potency"] = int(round(size / a["on_damage_hot"].get("duration", 3)))
        if mana and base.get("cost"):
            r["cost"] = int(round(base["cost"] * R.MANA[i]))
        out.append(r)
    return out


#: The keys the engine reads inside the dict-valued fields (a misspelt one is silently ignored).
NESTED = {
    "damage_share": {"pct", "reduction_pct", "heal_pct", "uses", "spread", "even"},
    "death_prevent": {"pct", "hp", "lethal_only", "uses"},
    "cleanses": {"types", "count"},
    "immediate": {"action", "turns", "resource", "cost_pct", "mult", "mode", "amount"},
    "delayed": {"turns", "mult", "mode"},
}


def check(rid, entry, recruits, keys, pkeys, seen):
    probs = []
    if rid in EXCLUDED:
        probs.append("Asher is never touched")
    if rid not in recruits:
        probs.append("not a recruit")
    first = recruits.get(rid, {}).get("name", rid).split()[0].lower()
    import unicodedata
    first = re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", first).encode("ascii", "ignore").decode())
    if not entry.get("from"):
        probs.append("no 'from' quote from the profile")
    ab, pas = entry.get("ability"), entry.get("passives")
    if bool(ab) == bool(pas):
        probs.append("needs exactly one of 'ability' or 'passives'")
    text = ""
    if ab:
        aid = ab.get("ability_id", "")
        if not aid.startswith(f"personal_sworn_{first}_"):
            probs.append(f"ability_id should start personal_sworn_{first}_")
        if aid in seen:
            probs.append(f"duplicate id {aid}")
        seen.add(aid)
        bad = set(ab) - keys
        if bad:
            probs.append(f"keys the engine doesn't read: {sorted(bad)}")
        for outer, inner in NESTED.items():
            if isinstance(ab.get(outer), dict) and set(ab[outer]) - inner:
                probs.append(f"{outer} keys the engine doesn't read: {sorted(set(ab[outer]) - inner)}")
        for k in ("name", "effect_type", "target_type", "resource_type", "description", "ranks"):
            if not ab.get(k):
                probs.append(f"missing {k}")
        cd = ab.get("cooldown") or 0
        if not COOLDOWN[0] <= cd <= COOLDOWN[1]:
            probs.append(f"cooldown {cd}, wants {COOLDOWN[0]} to {COOLDOWN[1]}")
        text = ab.get("description", "")
        import rank_kit_abilities as R
        grows = R.grows(ab) if ab.get("ranks") and ab.get("effect_type") else set()
        if grows:
            # the number grows with rank and the tooltip shows the rank's own; a number written
            # into the text would be wrong from level 15
            base = str(R.base_size(ab))
            if re.search(rf"\b{base}\b", text):
                probs.append(f"description names the rank 1 amount ({base}), which grows")
        elif not re.search(r"\d", text):
            probs.append("description states no number")
        if not ab.get("engine"):
            probs.append("no engine note")
    if pas:
        bad = {k for k in pas if not k.startswith("_")} - pkeys
        if bad:
            probs.append(f"passive keys nothing reads: {sorted(bad)}")
        if not pas.get("_name"):
            probs.append("passive needs a _name")
        text = pas.get("_text", "")
        if not re.search(r"\d", text):
            probs.append("passive _text states no number")
    blob = json.dumps(entry, ensure_ascii=False).lower()
    if re.search(r"once (a|per|each) (fight|combat|battle)", blob):
        probs.append("'once a fight' (Kyle: 10 to 15 turn cooldowns, never once per fight)")
    if "—" in text or "–" in text or " - " in text:
        probs.append("dash in the description")
    return probs


def main():
    strict = "--strict" in sys.argv
    src = json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else {}
    kits = json.loads(KITS.read_text(encoding="utf-8"))
    recruits = {}
    data = json.loads((ROOT / "data" / "npcs" / "recruits.json").read_text(encoding="utf-8"))
    for group in data.values() if isinstance(data, dict) else [data]:
        for r in group if isinstance(group, list) else []:
            if isinstance(r, dict) and r.get("recruit_id"):
                recruits[r["recruit_id"]] = r
    for rid, kit in kits.items():
        if not rid.startswith("_"):
            recruits.setdefault(rid, {"name": kit.get("name", rid)})
    keys, pkeys = loader_keys(), passive_keys()
    out = {"_doc": ["SWORN SKILLS - built by tools/build_sworn_skills.py from tools/wave4/sworn_skills.json. "
                    "Do not edit here; edit the source and rebuild."]}
    problems, seen, ranked = [], set(), 0
    for rid, entry in sorted(src.items()):
        if rid.startswith("_"):
            continue
        probs = check(rid, entry, recruits, keys, pkeys, seen)
        problems += [f"{rid}: {p}" for p in probs]
        built = json.loads(json.dumps(entry))
        if built.get("ability") and built["ability"].get("ranks"):
            built["ability"]["ranks"] = ranks_for(built["ability"], kits)
            ranked += len(built["ability"]["ranks"]) == 5
        out[rid] = built
    want = sorted(r for r in kits if not r.startswith("_") and r not in EXCLUDED)
    missing = [r for r in want if r not in src]
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for p in problems:
        print("  -", p)
    done = len(out) - 1
    print(f"{done} Sworn skills ({ranked} with five ranks), {len(missing)} recruits still to write, "
          f"{len(problems)} problems -> {OUT.relative_to(ROOT)}")
    if problems or (strict and missing):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
