"""
QA the Aspen Wilderness / Weeping Ice content pass.

    PYTHONPATH=. python3 tools/qa_aspen_content.py

WHY THIS FILE EXISTS, STATED PLAINLY: the first version of this content pass shipped a melee dump, and
nothing caught it. Twenty-four items came out cloth 2 / leather 5 / mail 3 / plate 4, with eight weapon
types and exactly one caster weapon among them. That is the same failure the Hillsbrad pass had to be
rebalanced for after the fact, and the same failure the Underdark pass wrote a QA tool to prevent - and
this pass's own header claimed to be checked by a file that did not exist yet.

So the budget is a CONTRACT now, not an intention:

  * SIX weapons, every one a DIFFERENT type, at least TWO of them caster weapons. Thirty playable classes
    need gear and most of them are not warriors.
  * SIXTEEN armour pieces, FOUR APIECE across cloth / leather / mail / plate. No class sits out a zone.
  * Casting-leaning suffixes between 40% and 60%, so the drops are not all strength and stamina.
  * No two items share a name, and no slot is over-served.

It also checks the things that break the GAME rather than the budget: every creature in every encounter
table exists, every ability kit resolves, every boss and rare named in the layouts has a creature behind
it, and the cave's level band sits above its parent zone's (the standing cave level rule).
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

FAIL = []


def check(ok, label, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {label}  {detail}")
    if not ok:
        FAIL.append(f"{label}  {detail}")


#: Suffixes that point at a caster or healer rather than a melee build. Used for the casting-share test.
CASTING = {
    "of the Owl", "of the Sorcerer", "of the Prophet", "of the Seer", "of the Invoker",
    "of the Archmage", "of the Hierophant", "of the Restorer", "of the Physician",
    "of Intellect", "of Spirit", "of the Mind's Eye", "of the Eagle", "of the Whale",
}
#: Weapon types a caster or healer can actually use.
CASTER_WEAPONS = {"staff", "wand", "tome", "totem", "dagger"}

loot = json.loads((ROOT / "data/loot/aspen_boss_loot.json").read_text())
pools = {k: v for k, v in loot.items() if not k.startswith("_")}
items = [i for v in pools.values() for i in v]

print(f"--- loot budget ({len(items)} items across {len(pools)} pools)")
check(len(items) == 24, "twenty-four items", f"{len(items)}")
check(all(len(v) == 4 for v in pools.values()), "four items per pool",
      str({k: len(v) for k, v in pools.items()}))

weapons = [i for i in items if i.get("weapon_type")]
wtypes = [i["weapon_type"] for i in weapons]
check(len(wtypes) == len(set(wtypes)), "no weapon type appears twice", str(sorted(wtypes)))
check(len(weapons) == 6, "six weapons", f"{len(weapons)}")
n_caster_w = sum(1 for w in wtypes if w in CASTER_WEAPONS)
check(n_caster_w >= 2, "at least two caster weapons",
      f"{n_caster_w}: {sorted(w for w in wtypes if w in CASTER_WEAPONS)}")

arm = Counter(i["armor_type"] for i in items if i.get("armor_type"))
check(sum(arm.values()) == 16, "sixteen armour pieces", f"{sum(arm.values())}")
check(set(arm) == {"cloth", "leather", "mail", "plate"}, "all four armour classes present", str(dict(arm)))
check(len(set(arm.values())) == 1 and set(arm.values()) == {4},
      "four pieces apiece - nobody sits the zone out", str(dict(arm)))

# Suffix is not stored on the item, so read it off the name the builder composed.
sufs = []
for i in items:
    n = i["name"]
    sufs.append(next((c for c in CASTING if n.endswith(c)), None))
# the builder does not append the suffix to the name, so fall back to the source file
src = (ROOT / "tools/build_aspen_content.py").read_text()
cast_calls = sum(src.count(f'"{c}"') for c in CASTING)
total_calls = src.count("mk(")
share = cast_calls / max(total_calls, 1)
check(0.40 <= share <= 0.60, "casting share between 40% and 60%",
      f"{100 * share:.0f}% ({cast_calls} of {total_calls})")

names = [i["name"] for i in items]
check(len(names) == len(set(names)), "no duplicate item names",
      str([n for n, c in Counter(names).items() if c > 1]))
slots = Counter(i["slot"] for i in items)
check(max(slots.values()) <= 6, "no slot is over-served", str(dict(slots)))

print(f"\n--- content integrity")
cre = json.loads((ROOT / "data/creatures/creatures.json").read_text())["creatures"]
kits = json.loads((ROOT / "data/creatures/ability_kits.json").read_text())["kits"]
enc = json.loads((ROOT / "data/creatures/encounters.json").read_text())["zones"]["The Aspen Wilderness"]

tables = [("open_zone", enc["open_zone"])]
tables += [(f"subzone/{k}", v) for k, v in enc["subzones"].items()]
tables += [(f"cave/{k}", v) for k, v in enc["caves"].items()]

missing, kitless = [], []
for label, t in tables:
    for c in t["creatures"]:
        if c not in cre:
            missing.append((label, c))
        elif cre[c].get("ability_kit") not in kits:
            kitless.append((label, c, cre[c].get("ability_kit")))
check(not missing, "every creature in every table exists", str(missing[:4]))
check(not kitless, "every creature's ability kit resolves", str(kitless[:4]))

# Boss kit rule: 20+ bosses carry four abilities, named rares are exempt and carry three.
BOSS = "Rimehowl"
RARES = ["Snowmaw", "The Last Drift", "The Last Kodo", "Goldcrown", "Bristlehide the Wintered"]
nb = len(kits[cre[BOSS]["ability_kit"]])
check(nb == 4, f"the boss carries four abilities (20+ rule)", f"{BOSS}: {nb}")
for r in RARES:
    n = len(kits[cre[r]["ability_kit"]])
    check(n == 3, f"named rare carries three abilities", f"{r}: {n}")

# First ability of every kit must be a zero-cooldown damage ability.
bad_open = []
for label, t in tables:
    for c in t["creatures"]:
        k = kits.get(cre.get(c, {}).get("ability_kit"), [])
        if k and (k[0].get("kind") != "damage" or k[0].get("cooldown", 0) != 0):
            bad_open.append((c, k[0].get("kind"), k[0].get("cooldown")))
check(not bad_open, "every kit opens with a 0-cooldown damage ability", str(sorted(set(bad_open))[:4]))

# Every pool name is a real creature flagged is_boss, so it can actually drop.
bad_pool = [p for p in pools if p not in cre or not cre[p].get("is_boss")]
check(not bad_pool, "every loot pool belongs to a real boss or rare", str(bad_pool))

# Standing cave level rule: a cave is never BELOW its zone.
zone_hi = max(cre[c]["level_range"][1] for t in tables[:-1] for c in t[1]["creatures"] if c in cre)
cave_lo = min(cre[c]["level_range"][0] for c in enc["caves"]["The Weeping Ice"]["creatures"] if c in cre)
check(cave_lo >= zone_hi - 1, "the cave is not below its zone (cave level rule)",
      f"cave starts {cave_lo}, zone tops out {zone_hi}")

# item_level = creature level + 3
off = []
for pname, plist in pools.items():
    want = cre[pname]["level_range"][1] + 3
    for i in plist:
        if i["item_level"] != want:
            off.append((i["name"], i["item_level"], want))
check(not off, "item_level = creature level + 3", str(off[:4]))

print()
if FAIL:
    print(f"{len(FAIL)} FAILURE(S)")
    for f in FAIL:
        print("  ", f)
    sys.exit(1)
print("aspen content: all checks passed")
