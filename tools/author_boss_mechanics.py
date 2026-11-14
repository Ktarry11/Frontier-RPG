#!/usr/bin/env python3
"""Give every dungeon boss one thing the party has to answer.

    PYTHONPATH=. python3 tools/author_boss_mechanics.py [--apply]

Kyle, 7 Nov: "Lets make this game more fun...with an actual challenge. Even
my friend is saying its tank and spank, 0 skill needed." And earlier: "we can
improve difficulty by having unique skills / things to deal with too. We have
such a varied magic system / skill system. Why not have more boss variety, it
feels very boring. everything is tank and spank with forgetable skills."

tools/audit_boss_threat.py measured why. Of 358 bosses, zero could stun, zero
carried a shield, and one applied anything dispellable. Mechanically the
bestiary had two tools, AoE and an enrage phase. The cause was structural -
MonsterAbility could not express a stun or an absorb at all - and that is
fixed; this is the content half.

SCOPE: the 185 bosses that stand in a dungeon, read off each cave zone's
boss_positions so it is the real in-game roster rather than a guess from
names. Kyle: "open world doesnt have to be VERY dangerous [...] but dungeons
should not just be free loot dispensers."

I SAID THE VARIETY WAS ALL IN THE NAMES. IT IS NOT, AND THAT CHANGED THIS
TOOL. Profiling the 185 dungeon kits:

    81 of 185 share the SHAPE   {buff: 1, damage: 4, dot: 1}
    59 of 185 share the SHAPE   {buff: 1, damage: 4}
    80 of 185 carry "Enrage"
    76 of 185 carry "Crushing Blow"
    28 of 185 carry "Sweeping Cleave"

The kits are unique as objects and assembled from a small shared vocabulary.
Two consequences:

  - A signature PREFERS a distinctive ability (GENERIC_NAMES). Putting the
    stun on "Crushing Blow" for 76 different bosses would have made the new
    mechanic exactly as generic as the name it rode on.
  - Shields and curses sometimes have to be ADDED rather than tagged. Nearly
    every boss has exactly one buff and for 80 of them it is Enrage, an
    hp_below phase ability, so a tag-only first run produced ZERO shields.
    Tagging alone reached 22 curses, which is not enough to make the game's
    14 cleanse abilities worth a global. Added abilities are named after the
    boss ("Aku'mai's Ward", "Silverlaine's Hex") so sixty of them do not all
    read "Barrier".

ONE SIGNATURE EACH, ROTATED WITHIN TEMPLATE. A first version mapped one
signature per creature template and produced 131 stuns out of 185, because 45
of the roster are humanoid_warrior and 28 are beast_large - samey with extra
steps, the exact thing this exists to stop. Each template now carries a
preference LIST and assignment rotates through it, which keeps every choice
appropriate to the creature while spreading the three mechanics evenly across
any given dungeon.

  stun     a hit that also costs you the next turn, so standing in the front
           rank is a decision
  shield   burn it off or waste your damage - a check that costs no health
  curse    a real dispel school, so the cleanses finally have PvE work

The combat log explains each one by itself (status_effects._describe_effect),
so a player meets "Grave Rot (19 shadow damage/turn, 4 turns)" rather than a
mystery.
"""

import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KITS = os.path.join(ROOT, "data/creatures/ability_kits.json")
CREATURES = os.path.join(ROOT, "data/creatures/creatures.json")

#: template prefix -> signatures that FIT that kind of thing, in preference
#: order. Assignment rotates through the list; see the module docstring.
BY_TEMPLATE = {
    "beast_large": ["stun", "shield"],
    "beast_fast": ["stun", "curse"],
    "beast": ["stun", "curse"],
    "vermin": ["curse", "stun"],
    "humanoid_warrior": ["stun", "shield", "curse"],
    "humanoid_rogue": ["stun", "curse"],
    "humanoid_caster": ["curse", "shield", "stun"],
    "humanoid_ranged": ["stun", "curse"],
    "undead_caster": ["curse", "shield"],
    "undead_warrior": ["shield", "stun"],
    "undead_basic": ["curse", "shield"],
    "undead_beast": ["stun", "curse"],
    "demon_caster": ["curse", "shield"],
    "demon_hound": ["stun", "curse"],
    "elemental_caster": ["shield", "curse"],
    "elemental_bruiser": ["shield", "stun"],
    "aquatic": ["shield", "curse"],
}

#: Ability names shared across many bosses - measured, not guessed. A
#: signature avoids these where the kit offers anything else.
GENERIC_NAMES = {
    "Enrage", "Crushing Blow", "Sweeping Cleave", "Thorned Lash",
    "Shadow Rend", "Wild Surge", "Dark Frenzy", "Thrashing Storm",
    "Arcane Overload", "Killing Chill",
}

#: Dispel school by damage school, so a curse matches what the boss actually
#: throws rather than a blanket "magic". A physical bleed is never
#: dispellable in WoW and is not made so here to hit a quota.
SCHOOL_TO_DISPEL = {
    "shadow": "curse", "arcane": "magic", "fire": "magic", "frost": "magic",
    "holy": "magic", "nature": "poison", "physical": None,
}

#: NATURE IS NOT ALWAYS POISON, and the school alone cannot tell them apart.
#: A first run tagged "Entangling Roots" and "Earthbind" as poison purely
#: because they are nature, which would send a player reaching for a poison
#: cleanse against a root. The ability's own name is the better signal: a
#: nature effect that says it is venomous is a poison, and everything else
#: nature is treated as magic.
POISON_WORDS = ("poison", "venom", "toxin", "toxic", "sting", "spore", "bile",
                "fang", "nettle")

#: SHADOW IS NOT ALL CURSE EITHER, and this one was worse than the nature
#: case because of what it did to the distribution. Mapping shadow -> curse
#: wholesale made CURSE the commonest enemy school by a mile - and curse is
#: the school the FEWEST player abilities can remove. Measured across
#: data/abilities/*.json:
#:
#:     magic    16 player dispels      enemy effects: 84
#:     disease  10 player dispels      enemy effects: 0
#:     poison    8 player dispels      enemy effects: 26
#:     curse     5 player dispels      enemy effects: 122
#:
#: The most common thing to be afflicted by was the hardest thing to
#: answer, and the ten disease cleanses in the game had literally nothing
#: to act on. That is the same "the player's toolkit has nothing to act on"
#: problem this whole pass exists to fix, reintroduced one layer down.
#:
#: Resolved by the ability's own name, the same technique as the nature
#: case: a shadow effect that names itself a curse is a curse, one that
#: names itself a sickness is a disease, and the rest are magic.
CURSE_WORDS = ("curse", "hex", "jinx", "doom", "malediction", "bane",
               "mark of", "evil eye", "ill omen", "shadow word")
DISEASE_WORDS = ("rot", "plague", "pestil", "fever", "pox", "blight",
                 "decay", "infect", "sick", "fester", "canker", "putrid",
                 "contagion", "miasma", "corrupt")


def dispel_for(ability):
    """Which cleanse answers this effect. Name first, school as the fallback.

    The school alone is too coarse: it is what made every nature debuff a
    poison and every shadow one a curse. The author already said what the
    thing IS in its name.
    """
    name = (ability.get("name") or "").lower()
    school = ability.get("school", "physical")
    base = SCHOOL_TO_DISPEL.get(school)
    if base is None:
        return None
    if any(w in name for w in DISEASE_WORDS):
        return "disease"
    if any(w in name for w in CURSE_WORDS):
        return "curse"
    if any(w in name for w in POISON_WORDS):
        return "poison"
    # Nothing in the name: fall back to the school, except that shadow
    # defaults to magic rather than curse so the scarcest cleanse in the
    # game is not also the most demanded.
    return "magic" if base in ("curse", "poison") else base

#: Titles stripped before naming an added ability after a boss, so the result
#: is "Hedessa's Ward" rather than "Admiral's Ward" - several bosses share a
#: rank and none of them share a name.
TITLES = ("The ", "Lady ", "Lord ", "Baron ", "Baroness ", "Captain ",
          "Overseer ", "Foreman ", "Archmage ", "Apothecary ", "Magister ",
          "Acolyte ", "Admiral ", "Bosun ", "Sergeant ", "Rifle-Sergeant ",
          "Gatewarden ", "Houndmaster ", "Prospector ", "Hunt-King ",
          "Shrine-Keeper ", "Grateward ", "Bonewarden ", "Matriarch ",
          "Broodmother ", "Alpha ", "Blind ", "Doctor ", "Master ",
          "Warlord ", "Chief ", "High ", "Grand ")

#: How long a boss stun lasts. ONE turn. A two-turn stun is a player watching
#: their party not act, which is not difficulty.
STUN_TURNS = 1

#: Absorb, as a multiple of the boss's own biggest hit. Burnable in about a
#: turn of focused damage - a check, not a wall.
SHIELD_MULTIPLE = 1.5

#: An added curse ticks for this share of the boss's biggest hit.
CURSE_SHARE = 0.28

#: RARES ARE NOT BOSSES. A rare is a named is_boss creature sitting in a
#: SUBZONE encounter table rather than pinned in a dungeon - 170 of them -
#: and it is met by whoever is passing through, often without a full party.
#: Kyle: "open world doesnt have to be VERY dangerous, but there should be
#: some brainpower. But dungeons should not just be free loot dispensers."
#:
#: So they get the same vocabulary at lower intensity, and NO SHIELDS. An
#: absorb on a world rare does not add a decision, it adds seconds - which
#: is the HP-sponge feel Kyle explicitly rejected ("i dont want them to be
#: massive HP sponges"). A stun you have to play around and a curse worth
#: cleansing are both answerable on the spot.
RARE_SIGNATURES = ["stun", "curse"]
RARE_STUN_COOLDOWN = 6      # vs 4 on a boss - it lands, it does not recur
RARE_CURSE_SHARE = 0.18     # vs 0.28


def _short_name(boss_name):
    short = (boss_name or "").split(",")[0].strip()
    for prefix in TITLES:
        if short.startswith(prefix):
            short = short[len(prefix):]
            break
    short = short.split()[0] if short else ""
    return short or "Dread"


def _possessive(short, noun):
    return f"{short}' {noun}" if short.endswith("s") else f"{short}'s {noun}"


def _biggest(kit, kinds=("damage",)):
    return max([x.get("amount", 0) or 0 for x in kit
                if x.get("kind") in kinds] or [40])


def _prefer_distinctive(cands):
    own = [a for a in cands if a.get("name") not in GENERIC_NAMES]
    return own or cands


#: Words in a boss's name that say it commands something. A summon is the
#: rarest of the signatures on purpose - "this one brings friends" should be
#: a thing a dungeon has once or twice, not every fight - so eligibility is
#: thematic rather than a quota.
LEADER_WORDS = ("King", "Queen", "Lord", "Lady", "Warlord", "Chief", "Captain",
                "Matriarch", "Patriarch", "Broodmother", "Overseer", "Foreman",
                "Master", "Alpha", "Commander", "Sergeant", "Warden", "Keeper",
                "Mother", "Father", "Elder", "Prime", "High", "Bosun",
                "Houndmaster", "Packleader", "Hunt-King")

#: Templates that summon because of WHAT they are rather than what they are
#: called - a necromancer raises, a warlock calls.
SUMMONER_TEMPLATES = ("undead_caster", "demon_caster", "humanoid_caster")

#: At most this many summoners per dungeon, so adds stay an event.
SUMMONERS_PER_DUNGEON = 2

#: How many adds, and how far below the boss they come in.
SUMMON_COUNT = 2
SUMMON_LEVEL_OFFSET = -2
SUMMON_MAX_ALIVE = 3
SUMMON_COOLDOWN = 7
#: Times a boss may call for help in one fight. See MonsterAbility._summon:
#: without this a live cap alone just tops the adds back up forever and the
#: fight stops resolving.
SUMMON_MAX_CASTS = 2


def dungeon_rosters():
    """-> {dungeon name: (set of boss names, [trash creature names])}

    A boss summoning its OWN DUNGEON'S trash is the whole reason this reads
    as an encounter rather than as a generic mechanic: Hunt-King Valorin
    calling Howling Barrows wolves is a fight, calling "Summoned Minion" is
    a placeholder. Both lists are read off the generated zone, which is
    where the game gets them.
    """
    from world.zone_generator import create_all_zones
    out = {}
    for name, tm in create_all_zones().items():
        if not getattr(tm, "is_cave", False):
            continue
        bosses = set()
        for b in (getattr(tm, "boss_positions", None) or []):
            if isinstance(b, dict):
                nm = b.get("name") or b.get("creature")
                if nm:
                    bosses.add(nm)
            elif isinstance(b, (list, tuple)) and len(b) > 2 and isinstance(b[2], str):
                bosses.add(b[2])
        trash = []
        for t in (getattr(tm, "trash_spawns", None) or []):
            nm = t[2] if isinstance(t, (list, tuple)) and len(t) > 2 else None
            if isinstance(nm, str) and nm not in trash:
                trash.append(nm)
        if bosses and trash:
            out[name] = (bosses, trash)
    return out


def subzone_rares():
    """Named is_boss creatures that live in a SUBZONE encounter table.

    Kyle, 30 Oct: "Rares should only be in subzones", and
    tools/qa_rare_placement.py enforces it - world/creature_manager rolls a
    named creature in exactly one place, the subzone branch. So the subzone
    tables ARE the rare roster, and reading them is how this gets the real
    170 rather than guessing from names.

    They are keyed by name in a weights dict (weight 0 = not in the trash
    roll), not listed as strings - a first pass walked for string values and
    found 2 rares instead of 170.
    """
    with open(os.path.join(ROOT, "data/creatures/encounters.json"), encoding="utf-8") as fh:
        zones = json.load(fh)["zones"]
    with open(CREATURES, encoding="utf-8") as fh:
        creatures = json.load(fh)["creatures"]
    bosses = {n for n, c in creatures.items() if c.get("is_boss")}
    out = set()
    for _z, d in zones.items():
        for _sz, sd in (d.get("subzones") or {}).items():
            for n in (sd.get("creatures") or {}):
                if n in bosses:
                    out.add(n)
    return out


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


def signature_for(template, rotation):
    """Next signature for this template, rotating through its list."""
    for prefix in sorted(BY_TEMPLATE, key=len, reverse=True):
        if template.startswith(prefix):
            opts = BY_TEMPLATE[prefix]
            i = rotation[prefix]
            rotation[prefix] += 1
            return opts[i % len(opts)], opts
    return "stun", ["stun"]


def apply_stun(kit, boss_name=None, rare=False):
    """The boss's biggest distinctive hit also costs you your next turn."""
    # NEVER SLOT 0. kit[0] is the basic attack and the engine's guaranteed
    # free swing - Monster.choose_action falls back to it when everything
    # else is on cooldown, and qa_aspen_content asserts "every kit opens
    # with a 0-cooldown damage ability". A first run put the stun's 4-turn
    # cooldown floor on slot 0 for four bosses (Gorrek Passkeeper, Hagra
    # Stormcrown, Rimehowl, Snowmaw) and broke that invariant: a monster
    # whose only free attack is on cooldown spends turns hesitating, which
    # is the opposite of the point of this pass.
    hits = [a for a in kit[1:] if a.get("kind") == "damage"
            and (a.get("amount") or 0) > 0 and not a.get("is_aoe")]
    if not hits:
        return None
    a = max(_prefer_distinctive(hits), key=lambda x: x["amount"])
    if (a.get("rider") or {}).get("is_stun"):
        return None
    rider = dict(a.get("rider") or {})
    rider.update({"effect": "debuff", "duration": STUN_TURNS, "is_stun": True})
    rider.setdefault("stat_mods", {})
    a["rider"] = rider
    # A stun that lands every turn is a lockout, not a mechanic.
    floor = RARE_STUN_COOLDOWN if rare else 4
    if (a.get("cooldown") or 0) < floor:
        a["cooldown"] = floor
    a["authored_mechanic"] = "stun"
    return a["name"]


def apply_shield(kit, boss_name=None, rare=False):
    """A shield that has to be burned off before the damage lands."""
    if rare or any(a.get("absorb") for a in kit):
        return None
    name = _possessive(_short_name(boss_name), "Ward")
    kit.append({
        "name": name, "kind": "buff", "amount": 0, "cooldown": 6,
        "mana_cost": 0, "school": "physical", "duration": 4,
        "self_only": True, "stat_mods": {},
        "absorb": int(round(_biggest(kit, ("damage", "dot")) * SHIELD_MULTIPLE)),
        "authored_mechanic": "shield",
    })
    return name


def apply_curse(kit, boss_name=None, rare=False):
    """Tag the boss's own dot/debuff with a real dispel school, or add one."""
    cands = [a for a in kit if a.get("kind") in ("debuff", "dot")
             and not a.get("dispel_type")]
    magic = [c for c in cands if dispel_for(c)]
    if magic:
        a = max(magic, key=lambda x: (x.get("kind") == "dot",
                                      x.get("amount", 0) or 0))
        a["dispel_type"] = dispel_for(a) or "magic"
        a["authored_mechanic"] = "curse"
        return f"{a['name']} ({a['dispel_type']})"

    if any(a.get("dispel_type") for a in kit):
        return None
    schools = [a.get("school", "physical") for a in kit
               if a.get("kind") in ("damage", "dot")]
    school = next((s for s in schools if SCHOOL_TO_DISPEL.get(s)), "shadow")
    dispel = SCHOOL_TO_DISPEL[school]
    noun = {"curse": "Curse", "poison": "Venom", "magic": "Hex"}[dispel]
    name = _possessive(_short_name(boss_name), noun)
    kit.append({
        "name": name, "kind": "dot",
        "amount": max(3, int(round(_biggest(kit)
                                   * (RARE_CURSE_SHARE if rare else CURSE_SHARE)))),
        "cooldown": 5, "mana_cost": 0, "school": school, "duration": 4,
        "dispel_type": dispel, "authored_mechanic": "curse",
    })
    return f"{name} ({dispel}, added)"


HANDLERS = {"stun": apply_stun, "shield": apply_shield, "curse": apply_curse}
#: Tried in order when the chosen signature has nothing to work with.
FALLBACK = ["curse", "stun", "shield"]


def author_trash(creatures, kits, kitdoc, args):
    """Caster trash gets a dispel school on the debuff it already casts.

    Kyle: "EVEN TRASH MOBS!" - but trash does NOT get stuns, shields or
    summons. There are 744 of them, and if every gnoll stuns you the
    mechanic stops meaning anything on the things that are supposed to be
    dangerous. Kyle's own line draws it: "open world doesnt have to be VERY
    dangerous, but there should be some brainpower."

    Measured: 145 trash creatures use a caster template and exactly ONE of
    them applies anything dispellable, while 105 already cast a dot or
    debuff that is simply untagged. So this changes no numbers and adds no
    abilities - it makes the spell the mob was already casting the kind of
    thing a Cleanse answers, which is texture on a pull rather than a
    second boss.

    Physical effects stay undispellable. A bleed is not a curse.
    """
    rows = []
    for name, c in sorted(creatures.items()):
        if c.get("is_boss") or "caster" not in c.get("template", ""):
            continue
        kit = kits.get(c.get("ability_kit"))
        if not kit or any(a.get("dispel_type") for a in kit):
            continue
        cands = [a for a in kit if a.get("kind") in ("dot", "debuff")
                 and dispel_for(a)]
        if not cands:
            continue
        a = max(cands, key=lambda x: (x.get("kind") == "dot",
                                      x.get("amount", 0) or 0))
        a["dispel_type"] = dispel_for(a) or "magic"
        a["authored_mechanic"] = "trash_curse"
        rows.append((name, c.get("template", ""), a["name"], a["dispel_type"]))

    print(f"  {len(rows)} caster trash mobs now cast something dispellable\n")
    print(f"  {'creature':30}{'template':20}{'ability':24}{'school'}")
    for n, t, ab, sch in rows[:args.show or 20]:
        print(f"  {n[:29]:30}{t[:19]:20}{ab[:23]:24}{sch}")
    if len(rows) > (args.show or 20):
        print(f"  ... and {len(rows) - (args.show or 20)} more")
    if args.apply:
        with open(KITS, "w", encoding="utf-8") as fh:
            json.dump(kitdoc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"\n  written to {KITS}")
    else:
        print("\n  (report only; pass --apply to write)")
    return 0


def author_summons(creatures, kits, kitdoc, args):
    """A couple of bosses per dungeon call in that dungeon's own trash."""
    rows = []
    for dungeon, (bosses, trash) in sorted(dungeon_rosters().items()):
        eligible = []
        for name in sorted(bosses):
            c = creatures.get(name)
            if not c or not c.get("is_boss"):
                continue
            kit = kits.get(c.get("ability_kit"))
            if not kit or any(a.get("kind") == "summon" for a in kit):
                continue
            by_name = any(w in name for w in LEADER_WORDS)
            by_type = c.get("template", "") in SUMMONER_TEMPLATES
            if by_name or by_type:
                # Name beats template, so the Hunt-King summons before the
                # anonymous caster standing next to him does.
                eligible.append((0 if by_name else 1, name, c, kit))
        eligible.sort()
        # Weakest trash first - adds are a tax on the party's time and
        # attention, not a second boss - but each summoner in a dungeon takes
        # a DIFFERENT one, so two bosses down the same corridor do not both
        # shout for the identical mob with the identical ability name.
        ladder = sorted(
            (t for t in trash if (creatures.get(t) or {}).get("template")),
            key=lambda t: (creatures.get(t, {}).get("level_range") or [99])[0])
        if not ladder:
            continue
        for slot, (_rank, name, c, kit) in enumerate(eligible[:SUMMONERS_PER_DUNGEON]):
            pick = ladder[slot % len(ladder)]
            tc = creatures.get(pick) or {}
            if not tc.get("template"):
                continue
            verb = "Raise" if c.get("template", "").startswith("undead") else "Call"
            label = f"{verb} the {pick.split()[-1]}s" if verb == "Raise" \
                else f"Call the {pick.split()[-1]}s"
            kit.append({
                "name": label, "kind": "summon", "amount": 0,
                "cooldown": SUMMON_COOLDOWN, "mana_cost": 0,
                "school": "physical", "duration": 0,
                "summon": {
                    "name": pick, "template": tc["template"],
                    "kit": tc.get("ability_kit"),
                    "count": SUMMON_COUNT,
                    "level_offset": SUMMON_LEVEL_OFFSET,
                    "max_alive": SUMMON_MAX_ALIVE,
                    "max_casts": SUMMON_MAX_CASTS,
                },
                "authored_mechanic": "summon",
            })
            rows.append((dungeon, name, label, pick))

    print(f"  {len(rows)} bosses across {len({r[0] for r in rows})} dungeons "
          f"can now call for help\n")
    print(f"  {'dungeon':26}{'boss':28}{'ability':24}{'summons'}")
    for d, b, label, pick in rows[:args.show or 20]:
        print(f"  {d[:25]:26}{b[:27]:28}{label[:23]:24}{pick}")
    if len(rows) > (args.show or 20):
        print(f"  ... and {len(rows) - (args.show or 20)} more")
    if args.apply:
        with open(KITS, "w", encoding="utf-8") as fh:
            json.dump(kitdoc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"\n  written to {KITS}")
    else:
        print("\n  (report only; pass --apply to write)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=20)
    ap.add_argument("--rares", action="store_true",
                    help="the 170 subzone rares instead of the 185 dungeon bosses")
    ap.add_argument("--trash", action="store_true",
                    help="tag caster trash debuffs with a dispel school")
    ap.add_argument("--summons", action="store_true",
                    help="give a couple of bosses per dungeon a call-for-help")
    args = ap.parse_args()

    with open(CREATURES, encoding="utf-8") as fh:
        creatures = json.load(fh)["creatures"]
    with open(KITS, encoding="utf-8") as fh:
        kitdoc = json.load(fh)
    kits = kitdoc["kits"]

    if args.trash:
        return author_trash(creatures, kits, kitdoc, args)
    if args.summons:
        return author_summons(creatures, kits, kitdoc, args)

    rotation = collections.defaultdict(int)
    rare = args.rares
    targets = subzone_rares() if rare else dungeon_bosses()
    rows, skipped = [], []
    counts = collections.Counter()

    for name in sorted(targets):
        c = creatures.get(name)
        if not c or not c.get("is_boss"):
            continue
        kit = kits.get(c.get("ability_kit"))
        if not kit:
            skipped.append((name, "no kit"))
            continue
        if rare:
            # Rares rotate through a two-item list regardless of template:
            # with shields off the table, the template preferences collapse
            # to the same two choices anyway, and rotating globally keeps
            # the split even instead of leaving one subzone all stuns.
            i = rotation["rare"]
            rotation["rare"] += 1
            want = RARE_SIGNATURES[i % len(RARE_SIGNATURES)]
            opts = RARE_SIGNATURES
        else:
            want, opts = signature_for(c.get("template", ""), rotation)
        order = [want] + [o for o in opts if o != want] \
                + [f for f in FALLBACK if f not in opts]
        done = None
        for sig in order:
            got = HANDLERS[sig](kit, name, rare)
            if got:
                done = (sig, got)
                break
        if done is None:
            skipped.append((name, "nothing of the right shape"))
            continue
        counts[done[0]] += 1
        rows.append((name, c.get("template", ""), done[0], done[1],
                     done[0] != want))

    label = "subzone rares" if rare else "dungeon bosses"
    print(f"  {len(targets)} {label}, {len(rows)} given a signature, "
          f"{len(skipped)} skipped")
    print(f"  stun {counts['stun']}   shield {counts['shield']}   "
          f"curse {counts['curse']}\n")
    print(f"  {'boss':30}{'template':20}{'signature':11}{'on'}")
    for name, tmpl, sig, what, fell in rows[:args.show]:
        print(f"  {name[:29]:30}{tmpl[:19]:20}{(sig + '*') if fell else sig:11}{what}")
    if len(rows) > args.show:
        print(f"  ... and {len(rows) - args.show} more"
              f"   (* = fell back; its type's first choice had nothing to tag)")
    if skipped:
        print("\n  skipped:")
        for name, why in skipped[:8]:
            print(f"       {name[:34]:36}{why}")

    if args.apply:
        with open(KITS, "w", encoding="utf-8") as fh:
            json.dump(kitdoc, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print(f"\n  written to {KITS}")
    else:
        print("\n  (report only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
