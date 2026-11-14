"""Build data/spellbook_tabs_coa.json: which spec tab each CoA ability lives in.

Source of truth for *which spec an ability belongs to* is the CoA class-preservation handoff (the
per-spec "Abilities" lists; "Shared Class Kit" = every spec's baseline kit -> Core tab).  Abilities are
matched by normalised display name against data/abilities/<class>.json; the result is a flat
{class: {ability_id: tree_id | "core"}} table the Skills screen reads.

    python3 tools/build_coa_spellbook_tabs.py <handoff.txt>
"""
import json, re, sys, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: handoff spec name -> our talent-tree spec name, where they differ.
SPEC_ALIASES = {("Venomancer", "Rot"): "venom"}


#: Abilities this game renamed/invented (no matching name in the handoff), placed by role.
MANUAL = {
    "cultist_eldritch_shock": "cultist_heretic", "cultist_void_strikes": "cultist_godblade",
    "cultist_bulwark_of_shadow": "cultist_dreadnought", "cultist_eldritch_bastion": "cultist_dreadnought",
    "runemaster_hurricane": "runemaster_glyphic",
    "stormbringer_call_of_the_storm": "stormbringer_wind", "stormbringer_call_of_the_lightning": "stormbringer_wind",
    "tinker_round_armor_pen": "tinker_mechanics", "tinker_stim_rounds": "tinker_mechanics",
    "tinker_healing_radiator": "tinker_invention", "tinker_battery_reclaimer": "tinker_invention",
    "venomancer_emerald_veil": "venomancer_vizier",
}


def norm(s):
    s = s.replace("*", "").replace("’", "'").replace("`", "'")
    s = re.sub(r"\(.*?\)", "", s)           # (T), (Generates 20 Heat)
    s = re.sub(r"[^a-z0-9 ]", "", s.lower())
    return re.sub(r"\s+", " ", s).strip()

def parse(path):
    cls = None; sect = None; out = {}
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = re.match(r"^# (.+)$", line)
        if m and m.group(1) not in ("Class Index",):
            cls = m.group(1).strip(); out[cls] = {"_shared": set()}; sect = None; continue
        m = re.match(r"^## Shared Class Kit", line)
        if m and cls: sect = "_shared"; continue
        m = re.match(r"^## Spec: (.+?) \(", line)
        if m and cls:
            sect = m.group(1).strip(); out[cls].setdefault(sect, set()); continue
        if cls and sect and re.match(r"^### .*Abilities", line):
            continue
        if cls and sect and line.startswith("- "):
            # Names are bold and often split by stray '****' around apostrophes ("N****'****Zoth"),
            # so take everything before the " - " description separator rather than the first bold span.
            head = re.split(r"\s+[\u2014\u2013-]\s+|\*\*\s+[\u2014\u2013-]", line[2:], maxsplit=1)[0]
            if "**" in line[:6] or head.startswith("*"):
                out[cls][sect].add(norm(head))
    return out

def main(handoff):
    parsed = parse(handoff)
    result = {}; report = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data/abilities/*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if not isinstance(d, dict) or not d.get("class"): continue
        cname = d["class"]
        if cname not in parsed: continue
        slug = cname.lower().replace(" ", "_")
        trees = {os.path.basename(t)[:-5] for t in glob.glob(os.path.join(ROOT, f"data/talents/{slug}_*.json"))}
        spec_to_tree = {}
        for spec in parsed[cname]:
            if spec == "_shared": continue
            tid = f"{slug}_{SPEC_ALIASES.get((cname, spec), spec).lower().replace(' ', '_')}"
            if tid in trees: spec_to_tree[spec] = tid
        table = {}; unmatched = []
        for a in d["abilities"]:
            n = norm(a["name"])
            if a["ability_id"] in MANUAL:
                table[a["ability_id"]] = MANUAL[a["ability_id"]]; continue
            owners = [s for s in spec_to_tree if n in parsed[cname][s]]
            if len(owners) == 1: table[a["ability_id"]] = spec_to_tree[owners[0]]
            elif len(owners) > 1: table[a["ability_id"]] = "core"          # shared by several specs
            elif n in parsed[cname]["_shared"]: table[a["ability_id"]] = "core"
            else:
                import difflib
                best = None
                for sp, names in list(parsed[cname].items()):
                    for cand in names:
                        r = difflib.SequenceMatcher(None, n, cand).ratio()
                        if r >= 0.86 and (best is None or r > best[0]): best = (r, sp)
                if best: table[a["ability_id"]] = "core" if best[1] == "_shared" else spec_to_tree.get(best[1], "core")
                elif a["ability_id"].endswith("_attack"): table[a["ability_id"]] = "core"
                else: unmatched.append(a["name"])
        result[cname] = table
        report.append((cname, len(d["abilities"]), len(table), unmatched, sorted(set(spec_to_tree.values()) - set(table.values()))))
    json.dump(result, open(os.path.join(ROOT, "data/spellbook_tabs_coa.json"), "w", encoding="utf-8"), indent=1, sort_keys=True)
    for c, n, m, u, empty in report:
        print(f"{c:12} abilities={n:3} matched={m:3} unmatched={len(u):2} {u[:12]} emptyTabs={empty}")

if __name__ == "__main__":
    main(sys.argv[1])
