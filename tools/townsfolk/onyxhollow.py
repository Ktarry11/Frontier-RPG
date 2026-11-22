"""Onyxhollow's people: the Dark Iron hold in the Tanaris rock (22 Nov 2026).

Kyle: "ensure ALL towns are actually populated", and "medium can be 25-30 ... cities lean towards one or two races but
not exclusive." The Dark Iron of the thane's hold: miners, smelters, stokers and their families, the vault's clerks, the
forge row's apprentices, and a few outsiders the thane lets in to trade. None of them gives a quest, sells or trains.
"""
M, F = "male", "female"

PEOPLE = [
    # ---- the Thane's Hall
    ("onx_tf_hall_scribe", "Scribe Brunhild Ashquill", "dwarf", F, "The Thane's Hall",
     "Every word the thane speaks in the hall goes into the great book, and he speaks a great many words. My ink's mixed with coal dust, so the book's as black as the walls."),
    ("onx_tf_hall_guard", "Hallguard Dagny", "dwarf", F, "The Thane's Hall",
     "Twenty years guarding the great hall's doors, and nobody's ever tried to get past. It's the statues, the outsiders say, they look like they're watching."),
    ("onx_tf_hall_petitioner", "Bergrun Coalbeard", "dwarf", M, "The Thane's Hall",
     "My claim on the third seam's been waiting on the thane's word for a month. He'll get to it, the scribe says, after the forge quotas and before the next feast."),
    # ---- the Mine Head
    ("onx_tf_cart_pusher", "Cart-Hand Grimli", "dwarf", M, "The Mine Head",
     "A hundred carts a day up from the mine head, and every one heavier than the last. The thane says the seam's getting richer, and my back says the same."),
    ("onx_tf_mine_widow", "Old Sigrun", "dwarf", F, "The Mine Head",
     "My husband went down the mine head forty years ago and never came up. I sit by the shaft every morning anyway, because the rock owes me a goodbye."),
    ("onx_tf_lamp_boy", "Lamp-Boy Torvi", "dwarf", M, "The Mine Head",
     "The miners' lamps get filled and trimmed before every shift, and that's my job. A dark lamp in the deep is a dead miner, so I never miss one."),
    ("onx_tf_crane_hand", "Crane-Hand Hilde", "dwarf", F, "The Mine Head",
     "The ore crane lifts the big stones out of the shaft, and it's older than my grandmother. It groans like her too, and it's never once dropped anything."),
    # ---- the Vault Ward
    ("onx_tf_vault_clerk", "Clerk Ormund Ledgerstone", "dwarf", M, "The Vault Ward",
     "Every ingot in the vault is weighed, stamped and written down. The thane counts them himself once a year, and the count has never once come up short."),
    ("onx_tf_vault_guard", "Vaultguard Ragna", "dwarf", F, "The Vault Ward",
     "Three locks on the vault door, and only the thane holds all three keys. One of them's mine to guard, and I sleep with it on a chain round my neck."),
    ("onx_tf_rune_carver", "Rune-Carver Eldir", "dwarf", M, "The Vault Ward",
     "The obelisks by the hall carry runes older than the hold itself. Recutting them when the soot wears them down is slow work, and the oldest still won't tell me what they say."),
    # ---- the Inn Yard
    ("onx_tf_inn_regular", "Stoker Hrolf", "dwarf", M, "The Inn Yard",
     "After a shift in front of the blast furnace, Brenna's ale is the only thing that cools a dwarf down. Two mugs, and my eyebrows stop smoking."),
    ("onx_tf_inn_singer", "Singer Gudrun", "dwarf", F, "The Inn Yard",
     "The old forge songs, every evening in the inn yard, the ones about the deep fire and the first anvil. The young ones bang their mugs in time, and that's how the songs survive."),
    ("onx_tf_boiler_hand", "Boiler-Hand Snorri", "dwarf", M, "The Inn Yard",
     "The boiler works heat half the hold, and the pipes run under every floor. If your feet are warm in Onyxhollow, you've got the boilers to thank."),
    # ---- the Market Steps
    ("onx_tf_goblin_trader", "Gizmo Brassgrin", "goblin", M, "The Market Steps",
     "The Dark Iron sell the best steel in Kalimdor, and they let one goblin in to buy it. That's me, and I've never once haggled, because they don't."),
    ("onx_tf_market_wife", "Frida Cinderhand", "dwarf", F, "The Market Steps",
     "Bread, cheese and smoked mushrooms from the deep caves, sold on the steps by the shop. The smelters buy the mushrooms, and nobody else is brave enough."),
    ("onx_tf_orc_buyer", "Grulka", "orc", F, "The Market Steps",
     "Orgrimmar sends me here for blades, and the dwarves stare like I'm about to steal the anvil. They sell to me anyway, because the Warchief's gold is good."),
    ("onx_tf_market_kid", "Little Brokk", "dwarf", M, "The Market Steps",
     "When I'm grown I'll work the blast furnace, like my father and his father. For now I carry the coal scuttle, and I'm very good at it."),
    # ---- Forge Row
    ("onx_tf_forge_apprentice", "Apprentice Kari", "dwarf", F, "Forge Row",
     "The forgemaster says a blade's not finished until it's been quenched in the old way, and he won't say what the old way is. I've been watching for two years."),
    ("onx_tf_smelter_hand", "Smelter Thrand", "dwarf", M, "Forge Row",
     "The smeltery runs hotter than anything else in the hold, and I've lost my beard to it twice. It grows back blacker every time, and I've decided that's an honour."),
    ("onx_tf_slag_hauler", "Slag-Hauler Bodil", "dwarf", F, "Forge Row",
     "Every day the slag heap grows by a cartload, and every day it's my cart. One day it'll be taller than the watchtowers, and they'll name it after me."),
    ("onx_tf_bellows_boy", "Bellows-Boy Ari", "dwarf", M, "Forge Row",
     "The bellows by the forge anvil never stop, and neither do I. My arms are the strongest in my year, and my ears are the worst."),
    ("onx_tf_shrine_tender", "Tender Valdis", "dwarf", F, "Forge Row",
     "The ash shrine by the crane warehouse keeps the names of every dwarf the deep fire took. A pinch of fresh ash goes on it every morning, one for each name."),
    # ---- the Gate Yard
    ("onx_tf_gate_watch", "Watchman Ulf", "dwarf", M, "The Gate Yard",
     "From the watchtower you can see the sand for leagues, and nothing good has ever come across it. The gate stays shut until the captain says otherwise."),
    ("onx_tf_barracks_cook", "Cook Hedda", "dwarf", F, "The Gate Yard",
     "The barracks eat more than the rest of the hold put together, and every bowl comes off my fire. The soldiers say my stew's heavier than their armour."),
    ("onx_tf_cage_keeper", "Keeper Brand", "dwarf", M, "The Gate Yard",
     "The cage by the barracks holds whatever the patrols drag in off the sand. Today it's a very angry scorpid, and I'm not feeding it by hand."),
]
