/**
 * Hand-authored class/spec metadata for Conquest of Azeroth.
 * tabId 87 = shared Class tree for every class.
 *
 * Spec name <-> tabId pairs were re-verified against Ascension's own live CoA Builder
 * (https://ascension.gg/en/v2/coa-builder/voljin) by extracting the embedded
 * `classes[].tabs[]` payload from that page's server-rendered HTML (real tabId/tabName/
 * sortOrder tuples, not guessed). Several classes had id<->name pairs swapped in the
 * previous hand-authored version (e.g. Witch Doctor's Brewing/Voodoo/Shadow Hunting were
 * each pointing at the wrong tabId, so picking "Brewing" showed Shadow Hunting's talents).
 *
 * Primalist: an earlier pass here mistakenly renamed the specs to Life/Geomancy/Primal/
 * Mountain King, on the assumption the scrape's Grovekeeper/Wildwalker names were stale
 * pre-rename leftovers. They weren't - confirmed 2026-07-27 against actual tab content
 * (data/classes/primalist.json talent names per tabId) and against data/spec-icons.js's
 * COA_SPEC_ICON_FILES.PRIMALIST, which was keyed on WILDWALKER/GEOMANCY/GROVEKEEPER/
 * "MOUNTAIN KING" the whole time and simply never matched anything while this file used
 * the wrong names. Real names+roles: Wildwalker (DPS, melee, tab 82), Geomancy (DPS,
 * caster, tab 83), Grovekeeper (Support, tab 84), Mountain King (Tank, tab 91).
 *
 * Runemaster spec names (Runic/Arcane/Riftblade, not Glyphic/Engraving) have NOT been
 * re-checked the same way - treat that one the same way Primalist was until verified:
 * confirm against actual tab content before trusting the name, and verify roles against
 * the in-game builder if one looks off.
 *
 * Where Ascension's data ties/omits sortOrder (no real ordering info), tab display order
 * here is arbitrary and cosmetic only - it doesn't affect which talents load for which tab.
 *
 * `color` = each class's signature border/accent color, pulled directly from
 * coabuildhub.com/calculator's rendered build-card border colors (read via computed
 * style, not guessed/approximated) so it matches the community-standard palette.
 */
const COA_CLASSES = [
  { name: "Reaper", slug: "reaper", classTab: 87, iconClass: "class-reaper", color: "#708090", specs: [
    { name: "Harvest", role: "DPS", tab: 79 },
    { name: "Soul", role: "DPS", tab: 80 },
    { name: "Domination", role: "Tank", tab: 81 },
  ]},
  { name: "Primalist", slug: "primalist", classTab: 87, iconClass: "class-wildwalker", color: "#8B4513", specs: [
    { name: "Wildwalker", role: "DPS", tab: 82 },
    { name: "Geomancy", role: "DPS", tab: 83 },
    { name: "Grovekeeper", role: "Support", tab: 84 },
    { name: "Mountain King", role: "Tank", tab: 91 },
  ]},
  { name: "Runemaster", slug: "runemaster", classTab: 87, iconClass: "class-spiritmage", color: "#4169E1", specs: [
    { name: "Arcane", role: "DPS", tab: 11 },
    { name: "Runic", role: "DPS", tab: 85 },
    { name: "Riftblade", role: "DPS", tab: 86 },
  ]},
  { name: "Bloodmage", slug: "bloodmage", classTab: 87, iconClass: "class-sonofarugal", color: "#8788EE", specs: [
    { name: "Sanguine", role: "DPS", tab: 26 },
    { name: "Accursed", role: "DPS", tab: 52 },
    { name: "Eternal", role: "Tank", tab: 53 },
    { name: "Fleshweaver", role: "Healer", tab: 93 },
  ]},
  { name: "Barbarian", slug: "barbarian", classTab: 87, iconClass: "class-barbarian", color: "#C79C6E", specs: [
    { name: "Brutality", role: "DPS", tab: 31 },
    { name: "Headhunting", role: "DPS", tab: 32 },
    { name: "Ancestry", role: "Support", tab: 33 },
  ]},
  { name: "Stormbringer", slug: "stormbringer", classTab: 87, iconClass: "class-stormbringer", color: "#0070DE", specs: [
    { name: "Lightning", role: "DPS", tab: 42 },
    { name: "Wind", role: "Support", tab: 43 },
    { name: "Maelstrom", role: "DPS", tab: 44 },
  ]},
  { name: "Pyromancer", slug: "pyromancer", classTab: 87, iconClass: "class-pyromancer", color: "#FF4500", specs: [
    { name: "Incineration", role: "DPS", tab: 62 },
    { name: "Draconic", role: "DPS", tab: 63 },
    { name: "Flameweaving", role: "Healer", tab: 19 },
  ]},
  { name: "Tinker", slug: "tinker", classTab: 87, iconClass: "class-tinker", color: "#B8860B", specs: [
    { name: "Demolition", role: "DPS", tab: 73 },
    { name: "Invention", role: "Healer", tab: 74 },
    { name: "Mechanics", role: "DPS", tab: 75 },
  ]},
  { name: "Felsworn", slug: "felsworn", classTab: 87, iconClass: "class-demonhunter", color: "#A330C9", specs: [
    { name: "Slayer", role: "DPS", tab: 37 },
    { name: "Infernal", role: "DPS", tab: 38 },
    { name: "Tyrant", role: "Tank", tab: 18 },
  ]},
  { name: "Starcaller", slug: "starcaller", classTab: 87, iconClass: "class-starcaller", color: "#FFFFFF", specs: [
    { name: "Moon Guard", role: "Tank", tab: 67 },
    { name: "Sentinel", role: "DPS", tab: 69 },
    { name: "Moon Priest", role: "DPS", tab: 68 },
    { name: "Warden", role: "DPS", tab: 89 },
  ]},
  { name: "Knight of Xoroth", slug: "knight-of-xoroth", classTab: 87, iconClass: "class-fleshwarden", color: "#C41E3A", specs: [
    { name: "War", role: "DPS", tab: 45 },
    { name: "Hellfire", role: "DPS", tab: 46 },
    { name: "Defiance", role: "Tank", tab: 47 },
  ]},
  { name: "Venomancer", slug: "venomancer", classTab: 87, iconClass: "class-prophet", color: "#00FF00", specs: [
    { name: "Venom", role: "DPS", tab: 76 },
    { name: "Stalking", role: "DPS", tab: 77 },
    { name: "Fortitude", role: "Tank", tab: 78 },
    { name: "Vizier", role: "Healer", tab: 92 },
  ]},
  { name: "Templar", slug: "templar", classTab: 87, iconClass: "class-monk", color: "#F48CBA", specs: [
    { name: "Zealot", role: "DPS", tab: 50 },
    { name: "Oathkeeper", role: "Tank", tab: 16 },
    { name: "Crusader", role: "DPS", tab: 51 },
  ]},
  { name: "Sun Cleric", slug: "sun-cleric", classTab: 87, iconClass: "class-suncleric", color: "#FFD700", specs: [
    { name: "Piety", role: "DPS", tab: 70 },
    { name: "Blessings", role: "Healer", tab: 71 },
    { name: "Valkyrie", role: "DPS", tab: 90 },
    { name: "Seraphim", role: "Tank", tab: 72 },
  ]},
  { name: "Chronomancer", slug: "chronomancer", classTab: 87, iconClass: "class-chronomancer", color: "#3FC7EB", specs: [
    { name: "Infinite", role: "DPS", tab: 56 },
    { name: "Time", role: "Healer", tab: 58 },
    { name: "Artificer", role: "DPS", tab: 57 },
  ]},
  { name: "Witch Doctor", slug: "witch-doctor", classTab: 87, iconClass: "class-witchdoctor", color: "#00FF96", specs: [
    { name: "Voodoo", role: "DPS", tab: 34 },
    { name: "Brewing", role: "Healer", tab: 35 },
    { name: "Shadow Hunting", role: "DPS", tab: 36 },
  ]},
  { name: "Guardian", slug: "guardian", classTab: 87, iconClass: "class-guardian", color: "#FF7C0A", specs: [
    { name: "Vanguard", role: "Tank", tab: 7 },
    { name: "Inspiration", role: "Support", tab: 48 },
    { name: "Gladiator", role: "DPS", tab: 49 },
  ]},
  { name: "Ranger", slug: "ranger", classTab: 87, iconClass: "class-ranger", color: "#AAD372", specs: [
    { name: "Archery", role: "DPS", tab: 54 },
    { name: "Brigand", role: "DPS", tab: 55 },
    { name: "Farstrider", role: "Support", tab: 2 },
  ]},
  { name: "Cultist", slug: "cultist", classTab: 87, iconClass: "class-cultist", color: "#9B30FF", specs: [
    { name: "Godblade", role: "DPS", tab: 64 },
    { name: "Corruption", role: "DPS", tab: 65 },
    { name: "Heretic", role: "Healer", tab: 66 },
    { name: "Dreadnought", role: "Tank", tab: 88 },
  ]},
  { name: "Necromancer", slug: "necromancer", classTab: 87, iconClass: "class-necromancer", color: "#556B2F", specs: [
    { name: "Death", role: "DPS", tab: 59 },
    { name: "Rime", role: "DPS", tab: 60 },
    { name: "Animation", role: "DPS", tab: 61 },
  ]},
  { name: "Witch Hunter", slug: "witch-hunter", classTab: 87, iconClass: "class-witchhunter", color: "#ABD473", specs: [
    { name: "Boltslinger", role: "DPS", tab: 39 },
    { name: "Houndmaster", role: "DPS", tab: 40 },
    { name: "Inquisition", role: "DPS", tab: 41 },
    { name: "Black Knight", role: "DPS", tab: 94 },
  ]},
];

if (typeof module !== "undefined") module.exports = COA_CLASSES;
