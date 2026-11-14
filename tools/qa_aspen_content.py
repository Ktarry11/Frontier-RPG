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

loot = json.loads((ROOT / "data/loot/aspen_boss_loot.json").read_text(encoding="utf-8"))
pools = {k: v for k, v in loot.items() if not k.startswith("_")}
all_items = [i for v in pools.values() for i in v]

#: THE ZONE'S OWN LOOT, separated from the cross-zone loot-balance overlay.
#: tools/build_loot_gap_items.py added 64 items for the five starved weapon
#: types across every boss and quest file in the game (Kyle: "fix loot
#: balance. Throw in an item throughout caves or Dungeons or quest rewards"
#: - thrown 4 -> 21, tome 7 -> 32, fist_weapon 17 -> 32, libram 0 -> 5, idol
#: 0 -> 2), and it put an Aspen Snow-Dart into The Last Drift's pool. That is
#: a deliberate addition and it is NOT a budget error, but the budget checks
#: below describe what this zone was authored to hold - so counting the
#: overlay in made the zone read as over budget on three counts at once (25
#: items, a 5-item pool, 7 weapons) for one item nobody did wrong.
#:
#: Gap items carry a "label"; the zone's own items do not. Both sets still
#: have to obey the per-pool item level, which is checked over ALL items
#: further down - that check is how the Snow-Dart's real bug surfaced (ilvl
#: 30 in a pool of 33s, since fixed).
GAP = [i for i in all_items if "label" in i]
items = [i for i in all_items if "label" not in i]
zone_pools = {k: [i for i in v if "label" not in i] for k, v in pools.items()}

print(f"--- loot budget ({len(items)} authored items across {len(pools)} pools"
      + (f", plus {len(GAP)} from the loot-balance overlay" if GAP else "") + ")")
check(len(items) == 24, "twenty-four items", f"{len(items)}")
check(all(len(v) == 4 for v in zone_pools.values()), "four items per pool",
      str({k: len(v) for k, v in zone_pools.items()}))

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
src = (ROOT / "tools/build_aspen_content.py").read_text(encoding="utf-8")
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
cre = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
kits = json.loads((ROOT / "data/creatures/ability_kits.json").read_text(encoding="utf-8"))["kits"]
enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]["The Aspen Wilderness"]

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

# BOSS KIT RULE, post-rework. This asserted four abilities for the boss and
# three for each named rare, which was the shape before
# tools/rework_boss_kits.py ran - Kyle, 2026-10-24, on bosses being
# "glorified punching bags". That pass set the rule the game actually
# follows now, in its own words: MIN_ATTACKS = 4, "basic + 3 distinct
# attacks, not counting the phase ability", plus a one-shot phase ability at
# 35% health for every boss without a heal. Five entries is therefore the
# MINIMUM a reworked boss carries, and across the whole game the level-20+
# bosses and rares come in at 3:1, 4:14, 5:120, 6:103 - five and six are the
# norm and four is the leftover. All six Aspen creatures sit at five and
# carry the rework's own boss_rework marker on their opener.
BOSS = "Rimehowl"
RARES = ["Snowmaw", "The Last Drift", "The Last Kodo", "Goldcrown", "Bristlehide the Wintered"]
MIN_ATTACKS = 4  # kept in step with tools/rework_boss_kits.py


def kit_shape(name):
    """(attacks, has_phase_ability) for one creature's kit."""
    kit = kits[cre[name]["ability_kit"]]
    phase = [a for a in kit if a.get("hp_below")]
    return len(kit) - len(phase), bool(phase)


for who in [BOSS] + RARES:
    attacks, phase = kit_shape(who)
    check(attacks >= MIN_ATTACKS and phase,
          f"{who} carries {MIN_ATTACKS}+ attacks and a phase ability",
          f"{who}: {attacks} attacks, phase={phase}")

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
#
# zone_hi was read off tables[:-1], which drops the LAST table on the
# assumption that the only cave is last. The Aspen Wilderness has TWO
# caves - The Weeping Ice and Rocky Pass - so the slice left one of them
# inside the "zone" set and the cave was being compared against itself:
# Meltwater Yeti (29-31) lives in The Weeping Ice, so the cave's own top
# became the zone's top and the cave read as starting two levels below a
# number it had supplied. The real zone tops out at 30 (Bristlehide the
# Wintered, Beaverdam Benches) and the cave starts at 29, which the rule
# allows. Selected by what each table IS rather than by position.
OPEN_AND_SUBZONES = [t for label, t in tables if not label.startswith("cave/")]
zone_hi = max(cre[c]["level_range"][1] for t in OPEN_AND_SUBZONES
              for c in t["creatures"] if c in cre)
for cave_name, cave in enc["caves"].items():
    cave_lo = min(cre[c]["level_range"][0] for c in cave["creatures"] if c in cre)
    check(cave_lo >= zone_hi - 1, f"{cave_name} is not below its zone (cave level rule)",
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
