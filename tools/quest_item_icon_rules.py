"""Keyword rules that give every quest item an icon from art we already have (22 Nov 2026).

Kyle, 22 Nov 2026: "For quest icons we can just use existing icons and reuse, hue shift etc." So no new sheets: each
quest item without a hand-picked icon (tools/build_quest_item_icons.py GROUPS) is matched by its name against the
rules below, in order, and gets one of the rule's icons. The pick is stable (a hash of the item id), and when an icon
ends up shared, the later items get a hue shift ("<icon>~h<degrees>", drawn by icon_system_core) so a bag full of
letters doesn't look like one letter twenty times. A colour in the item's name ("Scarlet Dispatch", "Jade Idol
Shard") turns the icon to that colour instead.

The pools are the quest item sheet (qi_*) and the vendor trash sheet (vt_*, sv_*), which share one painted style.
The cooked food and devices are square WoW-style icons with their own backgrounds, so they're left out, and the hidden
finds (hf_*) and the Earth junk (ej_*) are never reused: those belong to their own items. Meat is the one thing with
no art of its own yet; haunches and fillets borrow the raw hide until a sheet adds a cut of meat.

HOW EACH ICON MAY SHIFT (MODE). Hue shifting suits some art and ruins other art: a crystal or a vial can be any colour,
a letter's wax seal and ribbon can change but its paper can't turn green, and a bone, a pelt or a plank has to stay the
colour it is. So each base icon has a mode: "h" turns the whole icon, "s" turns only its strongly coloured parts
(seals, ribbons, cords, paint, the stripes on a crate), and anything not listed never shifts.
"""
import re
import zlib

# (pattern, icons). First match wins, so the specific things come before the general ones.
RULES = [
    # ---- named objects first, where the word is the whole story
    (r"\bkey\b|keystone", ["qi_key_iron", "qi_key_brass"]),
    (r"signet|\bring\b", ["qi_signet", "vt_grave_ring"]),
    (r"locket|keepsake|trinket|heirloom|family silver|\bdoll\b", ["vt_locket", "vt_locket_t2"]),
    (r"prayer|beads", ["qi_prayer_beads"]),
    (r"headstone|grave marker|name.stone|name.tablet|terrace name", ["qi_headstone"]),
    (r"wreath", ["qi_wreath"]),
    (r"pumpkin", ["qi_pumpkin"]),
    (r"\begg\b", ["qi_egg"]),
    (r"pennant|banner|nameboard", ["qi_pennant"]),
    (r"harpoon|boarding hook", ["qi_harpoon"]),
    (r"bloodstone|moonstone|sunstone", ["qi_gem"]),
    (r"pelt|hide\b|skin\b|\bfur\b|hair|fleece", ["vt_pelt", "vt_raw_hide", "vt_fur_tuft"]),
    (r"lantern cap|spore|(?<!blasting )\bcap\b|bloodcap|mushroom", ["vt_spore_cap", "vt_spore_cap_t2"]),
    (r"lantern(?!.*dust)|\blamp\b|lumen|guttering light", ["qi_lantern"]),
    (r"whistle|signal horn|ram horn", ["qi_horn"]),
    (r"charm|fetish|totem|idol\b", ["qi_totem", "vt_idol"]),
    (r"powder|blasting|\bcharges?\b|unmarked keg|vent tar", ["qi_powder_keg"]),
    (r"dosimeter|tiltmeter|gauge", ["qi_lantern"]),
    (r"gyro|governor|gear|cog\b|assembly|drive", ["qi_ore"]),
    (r"compass|route card", ["qi_chart"]),
    (r"lens|goggle", ["qi_crystal"]),
    (r"specimen press|\bpress\b", ["qi_journal"]),
    (r"\bmask\b|breastplate|\bboot\b|plate fragment|archive plate|builder's plate", ["vt_sigil", "vt_sigil_t2"]),
    (r"axe|blade|\bsaw\b|\bpick\b|pry bar|spear|\bstave\b|throwing", ["vt_broken_dagger", "vt_broken_dagger_t2"]),
    (r"snare|\bnet\b|rope|cord\b|coil|harness|knot|sinew|cable|line catch|fitting.line", ["qi_trophy_cord"]),
    (r"\bthread\b|silk|\bweave\b|course.weave|\bweb\b|web.wrapped", ["vt_silk_ball", "qi_gold_thread"]),
    # ---- writing
    (r"tally|token|badge|\btag\b|\bpins?\b|\bcoin\b|\bpay\b", ["qi_dog_tag", "qi_coin_pouch"]),
    (r"orders?\b|dispatch|writ\b|accord|grant|roll of oaths|scroll|decree|notice|contract|confession", ["qi_scroll"]),
    (r"chart|\bmap\b|plan\b|route\b|sketch|drawings?|rubbing", ["qi_chart", "vt_map_scrap"]),
    (r"ledger|codex|\bbook\b|\blog\b|catalogue|journal|figures|chapter|evening office", ["qi_ledger", "qi_journal"]),
    (r"\bpage\b|leaf\b(?!.*(grown|heart))|scrap\b|transcript|copy\b|copied", ["qi_page"]),
    (r"report|roster|findings|\blist\b|manifest|survey|notes?\b|soundings|readings?|count\b|account|\bclaim\b",
     ["qi_papers"]),
    (r"letter|reply|answer|message|\bword\b|query|request|warning|question|\boffer\b|endorsement|complaint|mail|"
     r"proposal|\bmark\b", ["qi_letter"]),
    (r"ticket|\bpass\b|\bslip\b|\bchit\b|stamp list", ["qi_ticket"]),
    (r"seal\b|council's seal|court seal|coffer.seal", ["qi_ward_seal"]),
    # ---- liquids and samples
    (r"\bwater\b|rainwater|spring water|mere.water|moonwell|meltwater", ["qi_flask"]),
    (r"serum|vial|phial|zeal|nectar", ["qi_vial"]),
    (r"sample|flask|sludge|residue|fouling|blood\b|\bsap\b|bladder", ["qi_flask", "qi_vial"]),
    (r"\bjar\b|loam|clay", ["qi_clay_jar"]),
    # ---- food and drink
    (r"\bale\b|beer|brew", ["qi_powder_keg"]),
    (r"stew|crock|ration", ["qi_clay_jar"]),
    (r"bread|flour", ["qi_seed_sack"]),
    (r"honey", ["qi_amber"]),
    (r"haunch|flank|venison|shank|\bmeat\b|fillet|cut of|tail meat|\bcrow\b", ["vt_raw_hide"]),
    (r"\bfat\b|tallow|\bgel\b|jelly|fodder|feed block", ["qi_clay_jar"]),
    # ---- containers
    (r"crate|cask|barrel|bundle|consignment|parcel|\bbox\b|supply", ["qi_crate", "sv_wreck_crate"]),
    (r"strongbox|coffer|case\b|\bkit\b|kitbag|\btin\b", ["qi_strongbox", "sv_barnacled_lockbox"]),
    (r"sack|pouch|basket|tray", ["qi_seed_sack", "qi_coin_pouch"]),
    # ---- stone, metal and light
    (r"tablet|relief|slate|flue stone|course stone", ["qi_tablet"]),
    (r"amber|resin", ["qi_amber"]),
    (r"pearl|\beye\b", ["vt_pearl", "vt_pearl_t2"]),
    (r"geode|druse|lattice", ["vt_geode", "vt_geode_arcane"]),
    (r"crystal|glass|prism|\bgem\b|star\b|focus", ["qi_crystal", "qi_gem"]),
    (r"core\b|anchorlight|light\b|spark|mote|wisp|essence|ember|living coal", ["vt_core", "vt_mote"]),
    (r"shard|fragment|chip\b|splinter(?!.*wood)", ["vt_shard", "vt_shard_t2"]),
    (r"ore\b|slag|bronze|brass|\biron\b|hinge|nail|fitting|boiler|wheel|cable end|\bband\b", ["qi_ore", "vt_slag",
                                                                                           "vt_slag_earth"]),
    # ---- off creatures
    (r"fang|tooth|toot", ["vt_fang", "vt_fang_t2"]),
    (r"tusk", ["vt_tusk"]),
    (r"claw|dewclaw", ["vt_claw", "vt_charred_claw"]),
    (r"barb\b|spur|stinger|sting\b", ["vt_stinger"]),
    (r"antler|horn", ["vt_horn_chunk", "vt_demon_horn"]),
    (r"\bjaw\b", ["vt_jawbone"]),
    (r"bone|marrow|knuckle", ["vt_bone", "vt_bone_t2"]),
    (r"feather|quill|plume|down\b|pinion|crest", ["vt_feathers", "vt_feathers_t2"]),
    (r"scale", ["vt_fish_scales", "vt_dried_scales"]),
    (r"shell|carapace|chitin|plate|scrapings", ["vt_shell", "vt_chitin_plate"]),
    (r"gland|sac\b|venom|gizzard|tumour|stitching|clot", ["vt_venom_gland", "vt_egg_sac"]),
    (r"mandible", ["vt_mandibles"]),
    (r"\bfin\b|gill", ["vt_fin"]),
    (r"membrane|wing\b", ["vt_wing_membrane"]),
    # ---- dust and ground
    (r"dust|\bash\b|ochre|earth|soil|spoil|crust|salt|\btar\b|ground sample", ["vt_grave_dust", "vt_ash"]),
    # ---- plants and wood
    (r"moss", ["qi_moss"]),
    (r"seed|seedling|cutting|pod\b", ["qi_seed_packet", "vt_seed_pod"]),
    (r"root|tuber", ["qi_root"]),
    (r"vine|bloom|flower|petal", ["vt_thorn_vine", "qi_petals"]),
    (r"leaf|herb|straw|bitterbark", ["qi_herbs", "qi_dewleaf"]),
    (r"timber|plank|batten|heartwood|splinter|yew|ivywood|stake|bark|bolt\b|strip", ["vt_bark", "vt_bark_t2"]),
    # ---- relics last, they catch the odd ones
    (r"relic|carving|offering|find\b|midden", ["qi_totem", "vt_idol"]),
    (r"sigil|ward", ["vt_sigil"]),
    (r"chalice|cup", ["qi_chalice"]),
]
MODE_H = set("""qi_crystal qi_gem vt_shard vt_shard_t2 vt_core vt_mote qi_vial qi_flask qi_totem vt_idol vt_sigil
vt_sigil_t2 vt_geode vt_geode_arcane vt_venom_gland vt_egg_sac vt_silk_ball qi_gold_thread vt_fish_scales
vt_dried_scales vt_shell vt_chitin_plate vt_spore_cap vt_spore_cap_t2 qi_petals vt_thorn_vine qi_prayer_beads vt_locket
vt_locket_t2 qi_signet qi_ward_seal qi_pennant vt_feathers vt_feathers_t2 vt_demon_horn vt_pearl vt_pearl_t2
vt_stinger vt_mandibles vt_wing_membrane vt_fin qi_dewleaf""".split())
MODE_S = set("""qi_letter qi_papers qi_scroll qi_page qi_ledger qi_journal qi_ticket qi_chart vt_map_scrap qi_dog_tag
qi_coin_pouch qi_crate qi_strongbox qi_seed_sack qi_clay_jar qi_powder_keg qi_trophy_cord sv_wreck_crate
sv_barnacled_lockbox""".split())
SAT_FLOOR = 170   # "s" mode: only pixels at least this saturated (0-255) turn


def mode(icon):
    return "h" if icon in MODE_H else "s" if icon in MODE_S else None


_COMPILED = [(re.compile(p), icons) for p, icons in RULES]
FALLBACK = ["vt_idol", "qi_totem"]

# Hue targets for colours named in an item's name (degrees on the HSV wheel).
COLOURS = [
    (r"scarlet|crimson|\bred\b|blood(?!hoof)|ruby", 0),
    (r"amber|orange|ochre|ember|cinder|fire", 28),
    (r"gold|golden|yellow|sunstone|sun.", 48),
    (r"fel|jade|green|moss|venom|plague", 110),
    (r"sea\b|tide|storm|azure|blue|frost|ice|rime|sky", 210),
    (r"violet|purple|void|arcane|shadow|night", 275),
]
_COLOURS = [(re.compile(p), h) for p, h in COLOURS]
# offsets for an icon's second, third ... item, spread round the wheel so neighbours differ
OFFSETS = [0, 150, 60, 240, 110, 300, 30, 200, 330, 90]


def _stable(s):
    return zlib.crc32(s.encode("utf-8"))


def pick(item_id, name):
    """(base icon, the rule's pattern or None) for an item with no hand-picked icon."""
    text = f"{(name or '').lower()} {item_id.replace('_', ' ')}"
    for rx, icons in _COMPILED:
        if rx.search(text):
            return icons[_stable(item_id) % len(icons)], rx.pattern
    return FALLBACK[_stable(item_id) % len(FALLBACK)], None


def colour_target(name):
    low = (name or "").lower()
    for rx, h in _COLOURS:
        if rx.search(low):
            return h
    return None
