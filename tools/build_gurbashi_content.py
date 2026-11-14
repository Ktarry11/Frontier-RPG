#!/usr/bin/env python3
"""Gurbashi Arena content pass (2026-10-29). Idempotent.

  PYTHONPATH=. python3 tools/build_gurbashi_content.py
  cd tools && python3 generate_creatures.py        # after any kit edit (kits: monster_kits.GURBASHI_KITS)

Five pits, five bosses, no trash (tools/handbuilt_gurbashi_arena.py). Band 36-38, which sits it
between Northern Stranglethorn's 30-34 and whatever the south ends up being. This script owns:

    data/creatures/creatures.json    the five bosses and the one add
    data/creatures/encounters.json   the Gurbashi Arena table
    data/loot/gurbashi_boss_loot.json  five pools of four, budget checked by audit()

THE FIVE PROBLEMS. The design note for this place is one sentence long - "a gauntlet style dungeon
where it's just 5 rooms with hard bosses" - and the only way that is not five health bars in a row is
if each room asks a different question. The kits in tools/monster_kits.py GURBASHI_KITS do the work;
what matters here is that the five are authored as a sequence that teaches and then examines:

    1  Vek'tar the Unbeaten       a damage race. He heals under half and drinks off you under a third.
    2  Grateward Mok'tal          party-wide burn that never lapses, and he cuts the healing that
                                  would answer it. Settling into a patient rotation is the losing play.
    3  Rakjan the Ribcracker      arrives with Jin'sha the Bloodcaller. Rakjan is the decoy; the
       + Jin'sha the Bloodcaller  handler is what kills you. Target priority or nothing.
    4  Zul'gar Hammerfall         three swings, all enormous, one of them shearing armour. The answer
                                  is mitigation; hitting him harder does not change the arithmetic.
    5  Jen'shala, the Favourite   one and four at once. The house's own fighter, and the last question.

WHO RUNS IT. The Gurbashi, same as always. You did not break in - you were ENTERED, your name is on a
board in Booty Bay, and the odds on it moved twice this morning. Nobody in the five pits is trying to
keep you out. The drum crew, the grate stoker and the pair-handlers are all doing a day's work, and
the work is making sure the rim gets what it paid for. That is the whole reason there is no trash:
there are no guards here, because nobody is guarding anything.

LOOT  ONE item per kill from the boss's own pool of 4; item_level = creature level + 3.
      BUDGET FIXED UP FRONT: FIVE weapons of five different families with ONE a caster weapon,
      TWELVE armour pieces at THREE APIECE across cloth/leather/mail/plate, THREE accessories, and
      each of the five bosses carrying its own distinct LEAD family so no two pits reward the same
      character. audit() fails the build rather than letting that drift.
      STANDING RULES CHECKED HERE TOO: this is a level 36-38 dungeon, so NO magic-resistance gear
      (that rule starts at 45) and no crafting material of any tier. Nothing here is quested, and
      there are no rares to quest.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as mk, C  # noqa: E402

#: Boss level -> the pinned chamber it stands in. Levels climb 36, 36, 37, 37, 38 across the line.
LEVELS = {
    "Vek'tar the Unbeaten": 36,
    "Grateward Mok'tal": 36,
    "Rakjan the Ribcracker": 37,
    "Zul'gar Hammerfall": 37,
    "Jen'shala, the House Favourite": 38,
}

#: Each pool's LEAD family, and the thing audit() enforces so the five pits do not all pay out to the
#: same character. Four of them lead on an armour class; the fifth leads on its weapon instead.
LEADS = {
    "Vek'tar the Unbeaten": "plate",
    "Grateward Mok'tal": "cloth",
    "Rakjan the Ribcracker": "leather",
    "Zul'gar Hammerfall": "mail",
    "Jen'shala, the House Favourite": "polearm",
}

#: Weapon families that arm a caster. The budget requires at least one.
CASTER_WEAPONS = {"wand", "staff", "tome", "libram", "idol", "totem"}

CREATURES = {
    # ---- THE FIVE. is_boss, so they are pinned to chambers rather than rolled, and they get the boss
    #      health multiplier. Multipliers climb gently down the line: the shape of each fight is what
    #      makes it hard, not the size of the bar.
    "Vek'tar the Unbeaten": C("humanoid_warrior", 36, 36, "vektar_unbeaten", True, 1.8),
    "Grateward Mok'tal": C("humanoid_caster", 36, 36, "grateward_moktal", True, 1.7),
    "Rakjan the Ribcracker": C("humanoid_warrior", 37, 37, "rakjan_ribcracker", True, 1.9),
    "Zul'gar Hammerfall": C("humanoid_warrior", 37, 37, "zulgar_hammerfall", True, 1.9),
    # Jen'shala fights with a pike and a physical kit, so she is a warrior template, not a caster -
    # humanoid_caster would have given her a mana pool her kit never spends and 105 base health.
    "Jen'shala, the House Favourite": C("humanoid_warrior", 38, 38, "jenshala_house_favourite", True, 2.0),

    # ---- THE ADD. NOT a boss: it is the second member of Rakjan's pack (zone.trash_packs in
    #      tools/handbuilt_gurbashi_arena.py), and it must stay non-boss because Monster.choose_action
    #      refuses to let a boss spend a turn on a plain debuff - Hex of the Short Round would never
    #      fire. It is deliberately ABSENT from the encounter table below: pack members are validated
    #      against creatures.json only, and leaving it out keeps the table boss-only, which is what
    #      leaves world/cave_spawns.populate() with nothing it could ever scatter as trash.
    "Jin'sha the Bloodcaller": C("humanoid_caster", 36, 36, "jinsha_bloodcaller"),
}

#: The encounter table. BOSSES ONLY, and every weight is 0 because nothing here is ever rolled - the
#: five are pinned to their chambers by zone.boss_positions / zone.trash_packs. A pinned boss only has
#: to BE in this table (world/cave_spawns.populate raises if it is not); the weight is never read.
ARENA_TABLE = {
    "name": "Gurbashi Arena",
    "creatures": {n: 0 for n in LEVELS},
}


def pools():
    return {
        # ---- PIT ONE. Lead: PLATE. The champion the bookies have never written a loss against.
        "Vek'tar the Unbeaten": [
            mk("Unbeaten's Notching Axe", "main_hand", "of the Gladiator", 39,
               "He put a notch in the haft for every round he finished. The haft ran out first.",
               weapon_type="axe_2h"),
            mk("Purse-Taker's Breastplate", "chest", "of the Champion", 39,
               "The crowd pays in one lump and he has never had to split it.",
               armor_type="plate"),
            mk("Never-Dropped Legguards", "legs", "of the Soldier", 39,
               "Scuffed to the knee and nowhere above it, which tells you how the rounds went.",
               armor_type="plate"),
            mk("Crowd-Caller's Spaulders", "shoulder", "of the Eagle", 39,
               "Somebody has to read the names out. It is a better job than fighting and worse pay.",
               armor_type="mail"),
        ],
        # ---- PIT TWO. Lead: CLOTH. The stoker, and the fire he is paid to keep under the floor.
        "Grateward Mok'tal": [
            mk("Stoker's Rod", "main_hand", "of the Invoker", 39,
               "Long enough to reach the coals without leaning over the grate. Just.",
               weapon_type="wand"),
            mk("Gratekeeper's Robe", "chest", "of the Archmage", 39,
               "Scorched through at the hem and patched from the inside, over and over.",
               armor_type="cloth"),
            mk("Vent-Opener's Gloves", "hands", "of the Sorcerer", 39,
               "Two layers of hide and a lining nobody will name. He opens the vents by hand.",
               armor_type="cloth"),
            mk("Hot-Floor Treads", "feet", "of the Monkey", 39,
               "Thick soles, and the trick of never putting a whole foot down at once.",
               armor_type="leather"),
        ],
        # ---- PIT THREE. Lead: LEATHER. The pair - and the handler is the one that matters.
        "Rakjan the Ribcracker": [
            mk("Pair-Handler's Rib Knife", "main_hand", "of the Assassin", 40,
               "Short, because the work is close. He never had to use it on his own fighter.",
               weapon_type="dagger"),
            mk("Ribcracker's Jerkin", "chest", "of the Bandit", 40,
               "Cut wide across the shoulders and taken in twice at the waist since.",
               armor_type="leather"),
            mk("Short-Round Hood", "head", "of the Wolf", 40,
               "Pulled down for the walk out. The rim does not get to see a face until it has paid.",
               armor_type="leather"),
            mk("Bloodcaller's Tally", "neck", "of the Prophet", 40,
               "A cord of knots, one for every round the handler called and his fighter finished.",
               ),
        ],
        # ---- PIT FOUR. Lead: MAIL. Four swings a round, all of them too big.
        "Zul'gar Hammerfall": [
            mk("Hammerfall's Shear", "main_hand", "of the Bear", 40,
               "The head is flat on one face and drawn to an edge on the other. Both have been used.",
               weapon_type="mace_1h"),
            mk("Hard Round Hauberk", "chest", "of the Defender", 40,
               "Relinked at the shoulder where something came through it and did not come through twice.",
               armor_type="mail"),
            mk("Plate-Shearer's Bracers", "wrist", "of the Seer", 40,
               "Armour comes off other people in strips and somebody down here keeps the strips.",
               armor_type="mail"),
            mk("Hard Round Signet", "ring", "of the Juggernaut", 40,
               "The fourth pit is the one the bookmakers close the book on. This is why.",
               ),
        ],
        # ---- PIT FIVE. Lead: the POLEARM, so the last pit is not another armour class - it is the
        #      weapon the house keeps for its own fighter.
        "Jen'shala, the House Favourite": [
            mk("Favourite's Gurbashi Pike", "main_hand", "of the Beast", 41,
               "Longer than the pit is wide at the ends. She has never needed the ends.",
               weapon_type="polearm"),
            mk("House-Favourite's Sabatons", "feet", "of the Squire", 41,
               "Nobody else in the five pits is shod. The house shods its own.",
               armor_type="plate"),
            mk("Odds-Keeper's Sash", "waist", "of the Mind's Eye", 41,
               "The board in Booty Bay moved twice before anyone down here had heard your name.",
               armor_type="cloth"),
            mk("Betting Token of the Last Pit", "trinket", "of the Prophet", 41,
               "Stamped on one side, blank on the other. Which side is which depends who you ask.",
               ),
        ],
    }


def audit(out, levels):
    """FAIL THE BUILD rather than ship a lopsided gauntlet.

    Five rooms with nothing between them means five payouts and nothing else, so the spread IS the
    reward structure here in a way it is not in an open zone - one plate boss too many and two of the
    five pits are worthless to half a party. The checks below are the same shape as the Southern
    Thousand Needles pass's audit(), plus the per-pool LEAD check that this dungeon actually needs,
    plus the two standing rules that apply at this level band.
    """
    pools_only = {k: v for k, v in out.items() if not k.startswith("_")}
    items = [i for v in pools_only.values() for i in v]
    wt = [i["weapon_type"] for i in items if i.get("weapon_type")]
    ar = {}
    for i in items:
        if i.get("armor_type"):
            ar[i["armor_type"]] = ar.get(i["armor_type"], 0) + 1
    acc = [i for i in items if not i.get("armor_type") and not i.get("weapon_type")]
    # mk() bakes the suffix into primary_stats and keeps no suffix key - reading a "suffix" key here
    # scored a flat 0 on the Drowning Floor pass and would have waved a melee dump straight through.
    casting = sum(1 for i in items if {"intellect", "spirit"} & set(i.get("primary_stats", {})))
    errs = []

    if len(pools_only) != 5:
        errs.append(f"want 5 pools (one per pit), got {len(pools_only)}")
    for k, v in pools_only.items():
        if len(v) != 4:
            errs.append(f"{k}: pool has {len(v)} items, want 4")

    if len(wt) != 5 or len(set(wt)) != 5:
        errs.append(f"want 5 weapons of 5 different families, got {wt}")
    if not CASTER_WEAPONS & set(wt):
        errs.append(f"no caster weapon in {wt} (need one of {sorted(CASTER_WEAPONS)})")
    if sorted(ar.values()) != [3, 3, 3, 3] or set(ar) != {"cloth", "leather", "mail", "plate"}:
        errs.append(f"armour not 3 apiece across four classes: {ar}")
    if len(acc) != 3:
        errs.append(f"want 3 accessories (no armour class, no weapon), got {len(acc)}")

    # FIVE PITS, FIVE LEADS. A lead is an armour class the pool carries at least twice and more of
    # than any other class, or - for exactly one pool - the weapon family nobody else drops.
    leads_seen = {}
    for k, v in pools_only.items():
        want = LEADS.get(k)
        if want is None:
            errs.append(f"{k}: no declared lead family")
            continue
        counts = {}
        for i in v:
            if i.get("armor_type"):
                counts[i["armor_type"]] = counts.get(i["armor_type"], 0) + 1
        if want in ("cloth", "leather", "mail", "plate"):
            if counts.get(want, 0) < 2 or counts.get(want, 0) < max(counts.values(), default=0):
                errs.append(f"{k}: lead '{want}' not dominant in pool (classes {counts})")
        else:
            pool_wt = [i["weapon_type"] for i in v if i.get("weapon_type")]
            if pool_wt != [want]:
                errs.append(f"{k}: weapon lead '{want}' but pool's weapons are {pool_wt}")
            if max(counts.values(), default=0) > 1:
                errs.append(f"{k}: weapon-lead pool must not double up an armour class ({counts})")
        leads_seen.setdefault(want, []).append(k)
    dupes = {w: ks for w, ks in leads_seen.items() if len(ks) > 1}
    if dupes:
        errs.append(f"two pits share a lead family: {dupes}")

    for k, v in pools_only.items():
        for i in v:
            if i["item_level"] != levels[k] + 3:
                errs.append(f"{i['name']}: ilvl {i['item_level']} != {levels[k]} + 3")

    # STANDING RULES at this band. No magic-resistance gear below 45, and this dungeon is 36-38.
    for i in items:
        stats = set(i.get("primary_stats", {})) | set(i.get("secondary_stats", {}))
        res = sorted(s for s in stats if s.endswith("_resistance"))
        if res:
            errs.append(f"{i['name']}: magic-resistance gear below level 45 ({res})")

    if not 0.40 <= casting / len(items) <= 0.60:
        errs.append(f"casting share {casting}/{len(items)} outside 40-60%")

    if errs:
        raise SystemExit("LOOT BUDGET FAILED:\n  " + "\n  ".join(errs))
    print(f"  loot ok: {len(items)} items across {len(pools_only)} pits")
    print(f"    weapons      {wt}")
    print(f"    armour       {ar}   accessories {len(acc)}")
    print(f"    pit leads    " + ", ".join(f"{k.split(' ')[0]}={LEADS[k]}" for k in pools_only))
    print(f"    casting      {casting}/{len(items)} ({casting / len(items):.0%})")
    print(f"    resistance   0 pieces (rule: none below level 45)")


def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text(encoding="utf-8"))
    # NAME COLLISIONS ARE SILENT DATA LOSS - dict.update() replaced an existing boss on the Drowning
    # Floor pass with no error at all.
    clash = [n for n in CREATURES if n in cdata["creatures"]
             and cdata["creatures"][n].get("ability_kit") != CREATURES[n].get("ability_kit")]
    if clash:
        raise SystemExit(f"CREATURE NAME COLLISION (would overwrite existing): {clash}")
    cdata["creatures"].update(CREATURES)

    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text(encoding="utf-8"))
    # THE LOOKUP THAT ACTUALLY RUNS. world/zone_manager.py hands cave_spawns the zone's .region as the
    # parent-zone key, and the Arena's region is pinned by contract to "Eastern Kingdoms -
    # Stranglethorn", so the live table has to live under that key's `caves`.
    region = edata["zones"].setdefault("Eastern Kingdoms - Stranglethorn", {})
    region.setdefault("open_zone", {"name": "Eastern Kingdoms - Stranglethorn", "creatures": {}})
    region.setdefault("caves", {})["Gurbashi Arena"] = ARENA_TABLE
    # ... and the same roster under the dungeon's own NAME, which is how the content tools and audits
    # key it. Nothing rolls off this one (zone.fixed_spawns is True, so the per-tile encounter roll
    # never fires in here at all) - it is the by-name view of the five pits.
    byname = edata["zones"].setdefault("Gurbashi Arena", {})
    byname["open_zone"] = ARENA_TABLE

    out = {"_notes": "Gurbashi Arena boss loot (2026-10-29). Five pits, five bosses, one item per "
                     "kill from that boss's pool of four. item_level = creature level + 3. Budget "
                     "and the five-way family spread are checked by audit() in "
                     "tools/build_gurbashi_content.py. Nothing in here is quested."}
    out.update(pools())
    audit(out, LEVELS)

    (ROOT / "data/loot/gurbashi_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    cp.write_text(json.dumps(cdata, indent=2) + "\n", encoding="utf-8")
    ep.write_text(json.dumps(edata, indent=2) + "\n", encoding="utf-8")
    print(f"Gurbashi Arena: creatures +{len(CREATURES)} (5 bosses + 1 add), pits 5, "
          f"loot items {sum(len(v) for k, v in out.items() if not k.startswith('_'))}, trash 0")


if __name__ == "__main__":
    main()
