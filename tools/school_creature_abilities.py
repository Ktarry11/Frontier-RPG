#!/usr/bin/env python3
"""Give the generic-"magic" creature abilities a real damage school.

    PYTHONPATH=. python3 tools/school_creature_abilities.py [--apply]

WHY IT MATTERS, precisely. Character.take_damage has two magic paths. A real
school (fire/frost/arcane/shadow/nature/holy) goes through get_resistance and
so is reduced by the player's own Fire Resistance, Shadow Resistance and the
rest. The legacy "magic" school instead uses the flat magic_resistance stat,
which is 10 on every creature template and 0 on most players - so 139
creature abilities were resisted by one flat number and ignored every piece
of resistance gear in the game. Kyle's whole per-school system (60 resistance
cap, 1 spell penetration removing 1 point) simply did not apply to them.

HEALS AND BUFFS ARE LEFT ALONE ON PURPOSE. 30 of the 139 are kind "heal" or
"buff", and nothing ever reads their school: they do not call take_damage, so
retagging them would be churn in a data file for no mechanical change. The
109 that matter are damage, dot and debuff.

HOW EACH SCHOOL IS DECIDED, strongest signal first, and nothing is guessed:

  1. THE KIT'S OWN VOICE. 66 of the 139 sit in a kit that already casts
     exactly one real school. An Ember Wisp whose other ability is fire does
     not have a second, different magic; its Smolder is fire. This is the
     same reasoning CreatureManager._apply_cast_affinity already uses to
     derive what a creature resists.
  2. THE NAME, anchored at a WORD START. Substring matching has bitten this
     codebase three times - "B-light-ed" and "Twi-light" matched a light
     rule, and audit_quests' number check matched "Redst-one scorpids" and
     "g-one and the charges". Every root here is \\b-anchored, which kills
     all three of those: there is no word boundary before the "light" in
     "blighted".

     Anchored at the start and NOT at the end, though, because this writing
     compounds heavily and a full-word rule could not see any of it:
     Thundercrack, Sumpchoke, Riptide, Iceshard, Weed-Choked, Bonefield.
     A handful of roots are kept full-word anyway because a DIFFERENT word
     starts with the same letters - "sear" would otherwise claim "search",
     "wind" would claim "window", "star" would claim "starved" - see
     WHOLE_WORD below. Every decision this makes is printed with the root
     that made it, and all of them were read by eye.
  3. NOTHING. Anything the first two cannot settle keeps "magic" and is
     printed, because a wrong school is worse than a flat one: it makes the
     wrong resistance gear work and tells the player something false about
     the enemy.

Idempotent, and re-runnable after Kyle rules on any of the leftovers.
"""

import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KITS = ROOT / "data/creatures/ability_kits.json"
CREATURES = ROOT / "data/creatures/creatures.json"
#: tools/rework_boss_kits.py's PRE-REWORK SNAPSHOT, and the reason this tool
#: has to write two files. The rework rebuilds every boss kit from this
#: snapshot, so schooling only the live ability_kits.json is undone the next
#: time anybody re-runs it - which is exactly what happened on the first
#: attempt here: 69 schooled abilities went straight back to "magic" and the
#: generic count climbed from 70 to 151. Schooling the snapshot as well
#: means the rework DERIVES its filler from the real schools (a kobold with
#: a Tallow Torch gets Searing Blast rather than Arcane Burst) instead of
#: reverting them.
BOSS_BASE = ROOT / "tools/boss_kits_base.json"

SCHOOLS = ("fire", "frost", "arcane", "shadow", "nature", "holy")
#: Only these kinds ever reach take_damage or carry a damage_school.
SCHOOLED_KINDS = ("damage", "dot", "debuff")

#: root -> school. Anchored at a word START (see the docstring): "\\bfire"
#: matches Firebolt and Fire Nova and cannot match the "fire" inside any
#: word, because there is no word boundary there.
LEXICON = [
    ("fire", ["fire", "flame", "flaming", "burn", "ember", "cinder", "scald",
              "scorch", "smolder", "molten", "magma", "lava", "pyre",
              "incinerat", "immolat", "blaz", "torch", "tallow", "boiler",
              "furnace", "brazier", "ash", "bomb"]),
    ("frost", ["frost", "ice", "icy", "freez", "frozen", "chill", "rime",
               "glacier", "glacial", "hoarfrost", "winter", "snow", "sleet",
               "permafrost", "coldsnap", "cold"]),
    ("nature", ["nature", "thorn", "vine", "root", "earthbind", "poison",
                "venom", "toxic", "toxin", "spore", "blight", "rot",
                "disease", "plague", "pestilen", "lightning", "thunder",
                "storm", "static", "gale", "tempest", "quake", "stone",
                "stoneskin", "boulder", "rock", "sand", "dust", "grit",
                "moss", "bramble", "sap", "wrath", "regenerat", "bloom",
                "growth", "brine", "seawater", "drown", "flood", "tide",
                "riptide", "water", "sump", "muck", "mire", "silt", "weed",
                "thistle", "paralytic", "retch", "damp", "swamp", "bog"]),
    ("shadow", ["shadow", "shade", "dark", "void", "umbral", "nether",
                "dread", "terror", "horror", "despair", "sorrow", "grief",
                "mourn", "wail", "banshee", "siphon", "curse", "hex", "doom",
                "corrupt", "unholy", "necro", "death", "grave", "crypt",
                "bone", "boneyard", "dirge", "tomb", "wither", "decay",
                "nightmare", "undercroft", "wretch"]),
    ("arcane", ["arcane", "mana", "spellbreak", "rune", "runic", "glyph",
                "sigil", "orrery", "astral", "starfall", "lunar", "moonfire",
                "portal", "rift", "banish", "polymorph", "teleport",
                "chrono", "anomaly"]),
    ("holy", ["holy", "radiant", "radiance", "divine", "sacred",
              "consecrat", "righteous", "judgment", "judgement", "smite",
              "hallowed", "blessing", "blessed", "sanctif", "seraph",
              "dawn", "benediction", "crusade", "censer"]),
]

#: Roots that must match a WHOLE word, because another word begins with the
#: same letters and a prefix rule would claim it:
#:   sear/search, wind/window, star/starved, light/lightning (two different
#:   schools), soul/soup, time/timber, mend/mendicant, drain/drainage.
WHOLE_WORD = {"sear", "searing", "wind", "star", "light", "lights", "soul",
              "souls", "time", "mend", "mending", "drain", "fear", "night",
              "moon", "spell", "ward", "magic", "cold"}
#: TOO OVERLOADED TO DECIDE ALONE. A name hit on one of these counts only
#: when the kit's own voice agrees; on its own it goes to the leftover pile.
#: "Light" is the whole reason this exists - it is a noun in "Hammer of the
#: Light" (holy), a different noun in "Cold Light" (a wisp, frost) and a
#: VERB in "Light the Seam", where Grubbis Tallow is committing arson. No
#: lexicon tells those apart, and schooling the arson as holy would make
#: Holy Resistance gear work against a fire.
NEEDS_CORROBORATION = {"light", "lights"}

#: THE AUTHOR NAMED THE SCHOOL, so nothing infers over it. A multi-school
#: caster makes the kit's voice useless for its individual abilities -
#: Archmage Atiesh casts arcane AND shadow, so his Arcane Bolt disagreed
#: with his kit and landed in the undecidable pile, as did High Inquisitor
#: Fairbanks' Holy Smite and Jergosh the Invoker's Immolate. When the name
#: carries the school's own word, or a verb that means exactly one element
#: and nothing else, that is a statement and not a hint.
EXPLICIT = {
    "arcane": ["arcane"],
    "fire": ["fire", "immolat", "searing", "sear", "flame", "pyre",
             "incinerat", "molten", "magma", "inferno"],
    "frost": ["frost", "glacial", "permafrost"],
    "nature": ["nature", "lightning", "poison", "venom"],
    "shadow": ["shadow", "unholy", "necro"],
    "holy": ["holy", "divine", "consecrat", "sanctif"],
}
EXPLICIT_RX = [(re.compile(r"\b(?:%s)" % "|".join(sorted(v, key=len, reverse=True)),
                          re.I), k) for k, v in EXPLICIT.items()]


def from_explicit(name):
    """The school the name states outright, or None."""
    hits = {s: rx.search(name or "") for rx, s in EXPLICIT_RX}
    hits = {s: m.group(0) for s, m in hits.items() if m}
    return next(iter(hits.items())) if len(hits) == 1 else None

#: ...and these are only useful as whole words, so they live here rather
#: than in the prefix lists above.
EXTRA_WHOLE = {
    "fire": ["searing", "sear"],
    "nature": ["wind", "gust"],
    "shadow": ["soul", "souls", "fear", "night", "drain"],
    "arcane": ["star", "time", "spell", "ward"],
    "holy": ["light", "lights"],
}


def _pattern(school, roots):
    whole = [r for r in roots if r in WHOLE_WORD] + EXTRA_WHOLE.get(school, [])
    prefix = [r for r in roots if r not in WHOLE_WORD]
    parts = []
    if prefix:
        parts.append(r"\b(?:%s)" % "|".join(sorted(prefix, key=len, reverse=True)))
    if whole:
        parts.append(r"\b(?:%s)\b" % "|".join(sorted(set(whole), key=len, reverse=True)))
    return re.compile("|".join(parts), re.I)


COMPILED = [(_pattern(school, roots), school) for school, roots in LEXICON]


def from_name(name):
    """Every school the name claims, and the root that claimed it.

    More than one school means the name decides nothing on its own.
    """
    hits = {}
    for rx, school in COMPILED:
        m = rx.search(name or "")
        if m:
            hits[school] = m.group(0)
    return hits


#: Every ability name tools/rework_boss_kits.py INVENTS, from its own HEAVY,
#: AOE and ENRAGE tables. These are filler it adds to pad a boss up to four
#: attacks and give it a phase ability - they are not the creature's own kit.
REWORK_FILLER = {
    "Crushing Blow", "Searing Blast", "Frost Lance", "Thorned Lash",
    "Shadow Rend", "Arcane Burst", "Holy Smite",
    "Sweeping Cleave", "Fire Nova", "Frost Nova", "Thrashing Storm",
    "Wave of Dread", "Arcane Wave", "Consecrated Wave",
    "Enrage", "Inferno Surge", "Killing Chill", "Wild Surge",
    "Dark Frenzy", "Arcane Overload", "Zealous Fury",
}


def kit_voice(kit):
    """The one real school this kit's OWN abilities cast, or None.

    THE REWORK'S FILLER IS EXCLUDED, and leaving it in made this circular.
    tools/rework_boss_kits.py picks a school for the filler it adds by
    totalling the kit's existing damage by school - and when a kit had no
    real school at all, it did this:

        if school not in HEAVY:
            school = "arcane"          # legacy generic "magic" school

    So every creature whose own abilities were ALL generic "magic" was given
    arcane-named filler, and reading that back as the kit's voice then told
    this tool the creature was arcane - on the strength of a default that
    was chosen precisely because nobody knew the school. Grubbis Tallow, a
    kobold whose two abilities are Tallow Torch and Light the Seam, came out
    arcane because the rework had handed him Arcane Burst.
    """
    others = {a.get("school") for a in kit
              if a.get("school") not in (None, "magic", "physical")
              and a.get("name") not in REWORK_FILLER}
    others = {s for s in others if s in SCHOOLS}
    return next(iter(others)) if len(others) == 1 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    kdoc = json.loads(KITS.read_text())
    kits = kdoc.get("kits", kdoc)
    bdoc = json.loads(BOSS_BASE.read_text())
    cre = json.loads(CREATURES.read_text())["creatures"]
    owner = collections.defaultdict(list)
    for n, v in cre.items():
        if v.get("ability_kit"):
            owner[v["ability_kit"]].append(n)

    decided, left, skipped = [], [], []
    by_source = collections.Counter()

    # ITERATED TO A FIXED POINT, because a kit's voice grows as its own
    # abilities get schooled. Grubbis Tallow's two abilities are Tallow Torch
    # and Light the Seam; the first resolves to fire off its name, and only
    # once it has does the kit have a voice for the second to be checked
    # against. One pass left every such sibling unresolved.
    rounds = 0
    while True:
        rounds += 1
        progress = False
        for kid, abilities in kits.items():
            for a in abilities:
                if a.get("school") != "magic":
                    continue
                if a.get("kind") not in SCHOOLED_KINDS:
                    continue
                # RECOMPUTED PER ABILITY, not once per kit. Grubbis Tallow's
                # two abilities are Tallow Torch and Light the Seam, and they
                # are decided in the same pass - with the voice read once up
                # front it was still None when the second was reached, so the
                # fixed-point iteration could never help it.
                voice = kit_voice(abilities)
                named = from_name(a["name"])
                roots = named
                explicit = from_explicit(a["name"])
                if explicit:
                    a["school"], src = explicit[0], f'named "{explicit[1]}"'
                elif voice and (not named or voice in named):
                    a["school"], src = voice, "kit"
                elif voice and len(named) > 1:
                    a["school"], src = voice, "kit (name scattered)"
                elif voice:
                    continue   # disagreement - decided below, after the loop
                elif (len(named) == 1
                      and next(iter(roots.values())).lower()
                      not in NEEDS_CORROBORATION):
                    school = next(iter(named))
                    a["school"], src = school, f'name "{roots[school]}"'
                else:
                    continue
                by_source[src] += 1
                decided.append((kid, a["name"], a.get("kind"), a["school"], src,
                                owner.get(kid, ["(unused)"])[0]))
                progress = True
        if not progress:
            break

    # Whatever is still "magic" could not be settled: either nothing speaks
    # for it, or the name and the kit disagree.
    for kid, abilities in kits.items():
        voice = kit_voice(abilities)
        for a in abilities:
            if a.get("school") != "magic":
                continue
            if a.get("kind") not in SCHOOLED_KINDS:
                skipped.append((kid, a["name"], a.get("kind")))
                continue
            named = from_name(a["name"])
            why = ([f"name:{next(iter(named))}", f"kit:{voice}"]
                   if voice and len(named) == 1 else sorted(named) or ["-"])
            left.append((kid, a["name"], a.get("kind"), why,
                         owner.get(kid, ["(unused)"])[0]))

    print(f"{len(decided) + len(left) + len(skipped)} abilities on generic "
          f'"magic"\n')
    print(f"  {len(skipped):>3} heal/buff - school is never read, left alone")
    print(f"  {len(decided):>3} given a real school   " +
          ", ".join(f"{k}: {v}" for k, v in by_source.most_common()))
    print(f"  {len(left):>3} undecidable, kept as magic")
    print(f"      (settled over {rounds} pass(es) to a fixed point)\n")

    print(f"{'ability':34}{'kind':8}{'school':9}{'from':22}creature")
    for kid, name, kind, school, src, who in sorted(decided, key=lambda r: (r[3], r[1])):
        print(f"{name[:33]:34}{kind:8}{school:9}{src:22}{who[:30]}")

    if left:
        print(f"\nKEPT AS \"magic\" - the kit says nothing and the name does "
              f"not settle it. Kyle's call:")
        for kid, name, kind, named, who in sorted(left, key=lambda r: r[1]):
            print(f"  {name[:33]:34}{kind:8}name suggests {'/'.join(named):22}{who[:28]}")

    counts = collections.Counter(r[3] for r in decided)
    print("\nnew school spread: " + ", ".join(f"{k} {v}" for k, v in counts.most_common()))

    if not args.apply:
        print("\n(report only; pass --apply to write)")
        return 0
    KITS.write_text(json.dumps(kdoc, indent=2, ensure_ascii=False) + "\n")
    print(f"\nwrote {KITS}")

    # Mirror every decision into the rework's snapshot, matched on kit id and
    # ability name, so a later rework run keeps them and re-flavours its own
    # filler off them.
    mirrored = 0
    decided_by = {(kid, name): school for kid, name, _k, school, _s, _w in decided}
    for kid, abilities in bdoc.items():
        for a in abilities:
            school = decided_by.get((kid, a.get("name")))
            if school and a.get("school") == "magic":
                a["school"] = school
                mirrored += 1
    BOSS_BASE.write_text(json.dumps(bdoc, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {BOSS_BASE} ({mirrored} mirrored into the rework snapshot)")
    print("\nNOW RE-RUN: PYTHONPATH=. python3 tools/rework_boss_kits.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
