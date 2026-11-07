#!/usr/bin/env python3
"""Give every dungeon boss one thing the party has to answer.

    PYTHONPATH=. python3 tools/author_boss_mechanics.py [--apply]

Kyle, 7 Nov: "Lets make this game more fun...with an actual challenge. Even
my friend is saying its tank and spank, 0 skill needed." And earlier: "we can
improve difficulty by having unique skills / things to deal with too. We have
such a varied magic system / skill system. Why not have more boss variety, it
feels very boring. everything is tank and spank with forgetable skills."

tools/audit_boss_threat.py measured why. Of 358 bosses, EACH WITH ITS OWN
UNIQUE KIT, zero could stun, zero carried a shield, and one applied anything
dispellable. The variety was entirely in the ability names; mechanically the
bestiary had two tools, AoE and an enrage phase. The cause was structural -
MonsterAbility could not express a stun or an absorb at all - and that is
fixed; this is the content half.

SCOPE: the 185 bosses that stand in a dungeon (read off each cave zone's
boss_positions, so it is the real in-game roster rather than a guess from
names). Kyle: "open world doesnt have to be VERY dangerous [...] but dungeons
should not just be free loot dispensers." Open-world rares are deliberately
left alone.

IT TAGS EXISTING ABILITIES, IT DOES NOT ADD NEW ONES. Every boss already has
a hand-authored kit with its own names, and those names are the one part of
the variety that was never broken - "Grave Cold", "Thirty Years of Silt",
"Nor Will You Leave". Inventing a generic "Crushing Stun" for 185 bosses
would trade the flavour that works for the mechanics that are missing. So the
boss's own biggest hit becomes the one that stuns, its own debuff becomes the
one worth dispelling, its own self-buff becomes the shield. The log already
explains what each does (combat/status_effects._describe_effect), so a player
meets "Grave Cold (69 shadow damage/turn, 4 turns)" rather than a mystery.

ONE SIGNATURE EACH, CHOSEN BY WHAT THE BOSS IS. Giving everything to everyone
is how you get back to samey with extra steps:

  stun     brutes and beasts - a hit that also costs you the next turn, so
           standing in the front rank is a decision
  shield   armoured things, elementals, constructs - burn it off or waste
           your damage, a check that costs no extra health
  curse    casters, undead, demons - tagged with a real dispel school, so
           the 14 cleanse abilities in the game finally have PvE work

A boss with no ability of the right shape is SKIPPED rather than given a
bolted-on one, and the report says how many and why.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KITS = os.path.join(ROOT, "data/creatures/ability_kits.json")
CREATURES = os.path.join(ROOT, "data/creatures/creatures.json")

#: template prefix -> signature. Read off the creature's template, which is
#: the one field that says what a thing IS rather than what it is called.
BY_TEMPLATE = {
    "beast": "stun", "vermin": "curse", "humanoid_warrior": "stun",
    "humanoid_rogue": "stun", "humanoid_caster": "curse",
    "humanoid_ranged": "stun", "undead_caster": "curse",
    "undead_warrior": "shield", "undead_basic": "curse", "undead_beast": "stun",
    "demon_caster": "curse", "demon_hound": "stun",
    "elemental_caster": "shield", "elemental_bruiser": "shield",
    "aquatic": "shield",
}

#: Dispel school by damage school, so a curse is tagged with something that
#: matches what the boss actually throws rather than a blanket "magic".
SCHOOL_TO_DISPEL = {
    "shadow": "curse", "arcane": "magic", "fire": "magic", "frost": "magic",
    "holy": "magic", "nature": "poison", "physical": None,
}

#: How long a boss stun lasts. One turn. A two-turn stun on a 12-turn
#: cooldown is a fight; a two-turn stun on a boss that can repeat it is a
#: player watching their party not act, which is not difficulty.
STUN_TURNS = 1

#: Absorb, as a multiple of the boss's own biggest hit. Burnable in about a
#: turn of focused damage - a check, not a wall.
SHIELD_MULTIPLE = 1.5


def dungeon_bosses():
    from world.zone_generator import create_all_zones
    names = set()
    for _n, tm in create_all_zones().items():
        if not getattr(tm, "is_cave", False):
            continue
        for b in (getattr(tm, "boss_positions", None) or []):
            if isinstance(b, dict):
                nm = b.get("name") or b.get("creature")
                if nm:
                    names.add(nm)
            elif isinstance(b, (list, tuple)) and len(b) > 2 and isinstance(b[2], str):
                names.add(b[2])
    return names


def signature_for(template):
    for prefix, sig in BY_TEMPLATE.items():
        if template.startswith(prefix):
            return sig
    return "stun"


def apply_stun(kit):
    """The boss's biggest damage ability also costs you your next turn."""
    hits = [a for a in kit if a.get("kind") == "damage" and (a.get("amount") or 0) > 0
            and not a.get("is_aoe")]
    if not hits:
        return None
    a = max(hits, key=lambda x: x["amount"])
    if a.get("rider", {}).get("is_stun"):
        return None
    rider = dict(a.get("rider") or {})
    rider.update({"effect": "debuff", "duration": STUN_TURNS, "is_stun": True})
    rider.setdefault("stat_mods", {})
    a["rider"] = rider
    # A stun that lands every turn is not a mechanic, it is a lockout.
    if (a.get("cooldown") or 0) < 4:
        a["cooldown"] = 4
    return a["name"]


def apply_shield(kit):
    """The boss's own self-buff becomes a shield that must be burned off."""
    buffs = [a for a in kit if a.get("kind") == "buff" and a.get("self_only", True)
             and not a.get("hp_below")]
    if not buffs:
        return None
    a = buffs[0]
    if a.get("absorb"):
        return None
    biggest = max([x.get("amount", 0) or 0 for x in kit
                   if x.get("kind") == "damage"] or [40])
    a["absorb"] = int(round(biggest * SHIELD_MULTIPLE))
    if (a.get("cooldown") or 0) < 5:
        a["cooldown"] = 5
    return a["name"]


def apply_curse(kit):
    """The boss's own debuff/dot gets a real dispel school."""
    cands = [a for a in kit if a.get("kind") in ("debuff", "dot")
             and not a.get("dispel_type")]
    if not cands:
        return None
    # Prefer the one that hurts most: a dot the party is bleeding to is worth
    # a global to remove; a -5 Agility debuff is not.
    a = max(cands, key=lambda x: (x.get("kind") == "dot", x.get("amount", 0) or 0))
    school = SCHOOL_TO_DISPEL.get(a.get("school", "physical"))
    if not school:
        # A physical bleed is never dispellable in WoW and should not become
        # so here just to hit a quota.
        magic = [c for c in cands if SCHOOL_TO_DISPEL.get(c.get("school"))]
        if not magic:
            return None
        a = max(magic, key=lambda x: x.get("amount", 0) or 0)
        school = SCHOOL_TO_DISPEL[a["school"]]
    a["dispel_type"] = school
    return f"{a['name']} ({school})"


HANDLERS = {"stun": apply_stun, "shield": apply_shield, "curse": apply_curse}
#: If the chosen signature has nothing to attach to, try these in order
#: before giving up - a boss with no self-buff can still carry a curse.
FALLBACK = ["curse", "stun", "shield"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=20)
    args = ap.parse_args()

    with open(CREATURES) as fh:
        creatures = json.load(fh)["creatures"]
    with open(KITS) as fh:
        kitdoc = json.load(fh)
    kits = kitdoc["kits"]

    targets = dungeon_bosses()
    rows, skipped = [], []
    counts = {"stun": 0, "shield": 0, "curse": 0}

    for name in sorted(targets):
        c = creatures.get(name)
        if not c or not c.get("is_boss"):
            continue
        kit = kits.get(c.get("ability_kit"))
        if not kit:
            skipped.append((name, "no kit"))
            continue
        want = signature_for(c.get("template", ""))
        order = [want] + [f for f in FALLBACK if f != want]
        done = None
        for sig in order:
            got = HANDLERS[sig](kit)
            if got:
                done = (sig, got)
                break
        if done is None:
            skipped.append((name, "nothing of the right shape to tag"))
            continue
        counts[done[0]] += 1
        rows.append((name, c.get("template", ""), done[0], done[1],
                     done[0] != want))

    print(f"  {len(targets)} dungeon bosses, {len(rows)} given a signature, "
          f"{len(skipped)} skipped")
    print(f"  stun {counts['stun']}   shield {counts['shield']}   "
          f"curse {counts['curse']}\n")
    print(f"  {'boss':30}{'template':20}{'signature':10}{'on'}")
    for name, tmpl, sig, what, fell in rows[:args.show]:
        tag = f"{sig}*" if fell else sig
        print(f"  {name[:29]:30}{tmpl[:19]:20}{tag:10}{what}")
    if len(rows) > args.show:
        print(f"  ... and {len(rows) - args.show} more"
              f"   (* = fell back; its type's signature had nothing to tag)")
    if skipped:
        print(f"\n  skipped:")
        for name, why in skipped[:8]:
            print(f"       {name[:34]:36}{why}")

    if args.apply:
        with open(KITS, "w") as fh:
            json.dump(kitdoc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"\n  written to {KITS}")
    else:
        print("\n  (report only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
