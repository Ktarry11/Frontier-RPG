#!/usr/bin/env python3
"""Fetch icons for the player abilities that drew a name box on the combat hotbar, and part the two shared pairs.

    python3 tools/fetch_missing_ability_icons.py            # fetch and install
    python3 tools/fetch_missing_ability_icons.py --dry-run  # say what each would get

Kyle, 18 Nov 2026, on the 20 abilities with no art and the two pairs sharing a picture: "For the wow classic ones,
you CAN find them online." Same CDN and the same verification as tools/fetch_classic_ability_icons.py and
tools/fetch_coa_icons.py: every response is opened as an image and checked before anything is written.

The classic and WoW abilities get their real icon. The Conquest of Azeroth ones have no canonical icon, so each
gets a thematic pick from Blizzard's library, the way fetch_coa_icons.py chose. Each row lists candidates in order;
the first that's a real image AND isn't already the picture of another of the same class's abilities or talents
(compared pixel for pixel) is installed, so no bar gets a pair of look-alikes. Another class using the same Blizzard
icon is fine: they're never on one bar, and fetch_coa_icons.py had already given several real icons out that way.
"""
import hashlib
import io
import sys
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/icons/abilities"
CDN = "https://wow.zamimg.com/images/wow/icons/large/{}.jpg"

WANT = {
    # classic and WoW: the real icon
    "druid_remove_curse": ["spell_holy_removecurse"],
    "druid_abolish_poison": ["spell_nature_nullifypoison_02"],
    "mage_remove_curse": ["spell_nature_removecurse"],
    "hunter_trueshot_aura": ["ability_trueshot"],
    "priest_divine_spirit": ["spell_holy_divinespirit"],
    "warrior_commanding_shout": ["ability_warrior_rallyingcry"],
    "warlock_demonic_pact": ["spell_shadow_demonicpact"],
    "shaman_cure_toxins": ["spell_nature_nullifypoison"],
    # on stand-ins until now (the art backlog's "Greater Heal and Chain Heal need proper icons")
    "priest_greater_heal": ["spell_holy_greaterheal"],
    "shaman_chain_heal": ["spell_nature_healingwavegreater"],
    # the two shared pairs: Swiftmend and Living Flame get their own
    "druid_swiftmend": ["inv_relics_idolofrejuvenation"],
    "druid_rejuvenation": ["spell_nature_rejuvenation"],        # it was wearing Swiftmend's idol
    "mage_living_flame": ["spell_fire_masterofelements", "spell_fire_flamebolt", "spell_fire_fire"],
    # Conquest of Azeroth: thematic
    "bloodmage_bloodbond": ["spell_deathknight_bloodpresence", "spell_shadow_bloodboil", "spell_shadow_lifedrain02", "inv_misc_gem_bloodstone_01",
                            "spell_shadow_lifedrain", "spell_deathknight_bloodtap", "ability_warlock_improveddemonictactics"],
    "chronomancer_borrowed_moments": ["spell_holy_borrowedtime", "inv_misc_pocketwatch_01", "spell_nature_timestop"],
    "felsworn_felbrand": ["spell_fire_felflamering", "spell_fire_felfire", "spell_shadow_curseofmannoroth"],
    "guardian_marching_song": ["inv_misc_drum_01", "inv_misc_drum_02", "inv_misc_horn_03"],
    "knight_of_xoroth_hellfire_ward": ["spell_fire_sealoffire", "spell_fire_firearmor", "spell_fire_incinerate"],
    "necromancer_grave_wisdom": ["inv_misc_book_06", "spell_shadow_ritualofsacrifice", "spell_shadow_raisedead"],
    "ranger_farstriders_mark": ["ability_hunter_markedfordeath", "ability_hunter_snipershot", "ability_marksmanship", "ability_hunter_mastermarksman",
                                "ability_hunter_rapidkilling", "inv_misc_eye_01", "ability_hunter_aimedshot"],
    "rogue_cutthroats_edge": ["ability_rogue_cuttothechase", "ability_rogue_slicedice", "ability_criticalstrike"],
    "starcaller_moonwells_blessing": ["spell_nature_moonglow", "inv_misc_gem_pearl_04", "spell_arcane_starfire"],
    "templar_templars_oath": ["spell_holy_sealofsacrifice", "ability_paladin_beaconoflight", "spell_holy_sealofwisdom"],
    "witch_doctor_spirit_fetish": ["inv_misc_idol_02", "inv_misc_idol_03", "inv_misc_head_troll_01", "inv_misc_idol_01",
                                   "inv_misc_idol_04", "inv_misc_bone_humanskull_01", "spell_shadow_shadesofdarkness"],
    "witch_hunter_hunters_ward": ["spell_holy_powerwordbarrier", "spell_holy_ashestoashes", "spell_holy_sealofprotection"],
}


#: Kyle, 18 Nov 2026: "For the CoA classes, just colour tint some other stuff to the theme of the class itself bro."
#: These classes' picks are tinted toward their class colour, read off the class's own icon (assets/ui/class_icons),
#: so a borrowed Blizzard icon reads as that class's. Classic classes keep the real icon untouched.
COA_TINT = {"bloodmage", "chronomancer", "felsworn", "guardian", "knight_of_xoroth", "necromancer", "ranger",
            "starcaller", "templar", "witch_doctor", "witch_hunter"}
TINT_STRENGTH = 0.5


def theme_colour(cls):
    """The class icon's saturation-weighted average colour, pushed to full brightness."""
    import colorsys
    im = Image.open(ROOT / "assets/ui/class_icons" / f"{cls}.png").convert("RGB").resize((48, 48))
    tot, acc = 0.0, [0.0, 0.0, 0.0]
    for r, g, b in im.getdata():
        h, sat, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        w = sat * v
        tot += w
        acc = [a + c * w for a, c in zip(acc, (r, g, b))]
    r, g, b = (a / max(tot, 1e-6) for a in acc)
    h, sat, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    r, g, b = colorsys.hsv_to_rgb(h, min(1.0, sat * 1.2), 1.0)
    return int(r * 255), int(g * 255), int(b * 255)


def tint(img, colour):
    """Recolour by luminance toward `colour`, blended with the original so its detail survives."""
    from PIL import ImageOps
    toned = ImageOps.colorize(ImageOps.grayscale(img), black=(0, 0, 0), white=colour, mid=None)
    return Image.blend(img.convert("RGB"), toned.convert("RGB"), TINT_STRENGTH)


def pixels(img):
    return hashlib.md5(img.convert("RGB").resize((56, 56)).tobytes()).hexdigest()


def fetch(name):
    req = urllib.request.Request(CDN.format(name), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        img = Image.open(io.BytesIO(r.read()))
        img.load()
    if img.size[0] != img.size[1] or img.size[0] < 32:
        raise ValueError(f"not an icon {img.size}")
    return img.convert("RGB")


def main():
    dry = "--dry-run" in sys.argv
    classes = sorted({p.stem.split("_")[0] for p in OUT.glob("*.png")} | {"knight_of_xoroth", "witch_doctor",
                                                                        "witch_hunter"}, key=len, reverse=True)

    def cls_of(stem):
        return next((c for c in classes if stem.startswith(c + "_")), stem.split("_")[0])
    taken = {}
    for d in ("abilities", "talents", "coa"):
        for p in (ROOT / "assets/icons" / d).glob("*.png"):
            if p.stem in WANT:
                continue
            try:
                taken.setdefault(pixels(Image.open(p)), set()).add((cls_of(p.stem), p.stem))
            except Exception:
                pass
    done, fails = [], []
    for aid, names in WANT.items():
        got = None
        for name in names:
            try:
                img = fetch(name)
            except Exception as e:      # noqa: BLE001 - try the next candidate
                continue
            h = pixels(img)
            name_part = aid[len(cls_of(aid)) + 1:]
            # a talent named for the ability ("Improved Chain Heal") wears its icon in WoW too
            if any(c == cls_of(aid) and name_part not in stem for c, stem in taken.get(h, ())):
                continue
            got = (name, img, h)
            break
        if not got:
            fails.append(aid)
            continue
        name, img, h = got
        taken.setdefault(h, set()).add((cls_of(aid), aid))
        done.append((aid, name))
        if cls_of(aid) in COA_TINT:
            img = tint(img, theme_colour(cls_of(aid)))
        if not dry:
            img.resize((56, 56)).save(OUT / f"{aid}.png")
    for aid, name in done:
        print(f"  {aid:34} {name}")
    print(f"{'would install' if dry else 'installed'} {len(done)} of {len(WANT)}")
    for aid in fails:
        print("  NO UNUSED CANDIDATE", aid)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
