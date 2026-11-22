"""underdark_dungeons story pass (22 Nov 2026), to docs/quest_writing_standard.md. Where the giver's speech sat in the accept
line and the journal showed a summary or narration, the speech is now the description and the accept line a new short
beat; the rest were written fresh. Turn-ins untouched."""

STORY = {
    'fd_long_way_down': (
        "Go down, and keep going down. The ice holds for the first stretch. It's old ice, Alterac ice, nothing stranger than cold.\n\nAfter that it stops being ice, and I can't tell you what it becomes, because the two men I sent came back without agreeing. Get past the frozen watercourse and see the seam for yourself. That's all I'm asking for, and it's more than I have.",
        'Mark the place where the ice stops. I want to know exactly how far down that is.',
    ),
    'fd_yeti_marrow': (
        "Bring me draws of marrow from the hoarfrost yeti in the upper galleries. They're easier to find than to leave.\n\nI want them cold. Pack them in ice from the chamber you take them in. If they're warm when they reach me I learn nothing, and I'll have sent you up there for a story.",
        "Take the draws from the big ones. The young yeti haven't been up there long enough to matter.",
    ),
    'fd_frozen_page': (
        "You pull a page out of the ice, and the ice gives it up cleanly, the way ice does when a thing has been in it a long time without ever settling. The hand is Alteraci and the date is forty-one years old. It reads: the readings are wrong and I'm going on. Below that, smaller, the same hand has added: there's no bottom to this and I've stopped telling the others. There was a camp down here before the Codex, and it didn't come back up, and the walkers along the seam still carry its fittings, its buckles and straps and lamp-brackets. Somebody at the Bastion will want to know their own road was walked forty years before they found it.",
        'You fold the page into your coat, away from the cold, and start looking for the rest of them.',
    ),
    'fd_hoarfang': (
        "I've watched the passage mouth for three years, and I know exactly how long the walk from the Hillsbrad side takes. For two months it's taken longer, and the people who make it arrive short of someone. Something is holding the ice chambers of the Frostward Descent against us, well enough that I've started sending people up in threes. The porters call it Hoarfang, and it takes the back of a column in the narrow stretch above the frozen watercourse, and it doesn't stay to fight. Go up there and make it stay.",
        "Walk at the back of the column on your way up. That's the place it chooses.",
    ),
    'fd_cartographer': (
        "He's at the seam, where the ice stops. He has a rod and a board, and he takes a reading off everything that comes near him, including people.\n\nI'm not sending you to put a man out of his misery, because I've no evidence he's in any. I want his board. Whatever he's been drawing for forty-one years, the Codex doesn't have a copy, and I'd like to be the one who does.\n\nThe Codex has him down as the Frozen Cartographer.",
        'Keep his board dry and flat on the way back. I want every line he drew.',
    ),
    'fd_latticeborn': (
        "The lower chambers have grown a warden, and I've entered it as the Latticeborn. It doesn't patrol and it doesn't hunt. It simply stands in the passage and won't be gone around.\n\nWatch what it does before you close. It strikes twice, identically, every time, and the second strike is the same event happening again, not another try. If you understand why that frightens me, you'll do better in there than most.",
        'Count the strikes. If it ever does a third one, get out and tell me.',
    ),
    'hg_crack': (
        "I run the last supply post before the Geode, and I'm required to say so and required not to say why. The why is that the Hollow Geode is a crystal cavity that's been filling for longer than anybody can estimate, and you can only walk where the crystal hasn't reached yet. Go in through the crack in the shell as far as the first gallery, then turn round and come out. Don't think of it as a cave with rooms, because it's a space being closed, in layers, from the outside in. Every way further inward is a pinch where the growth has nearly met, and if you're in a hurry you'll walk into one sideways and the crystal will decide the matter.",
        "Touch nothing on the way in. Some of the crystal's sharper than it looks, and all of it's older than you.",
    ),
    'hg_druse': (
        "The druse gallery runs just inside the Geode's shell, broken into bays by crystal masses that have grown inward from the wall. The Druse Crawlers live in the gaps, they're shaped like the gaps, and they've been getting narrower along with everything else. Clear them out of the gallery bays, and work them bay by bay rather than trying to run the ring. The ring winds, and a thing that lives in a pinch will let you pass it and take the second person. I lost a digger that way, and there's no second person with you, which is the part people forget about coming down here alone.",
        "Count the bays as you clear them. There are more than you'd think, and they look alike.",
    ),
    'hg_cavity': (
        "Bring me pieces of druse with something in them, and I mean something that was made. You'll find them. The crawlers break the shell down, and what comes loose is full of it.\n\nI'm not a cataloguer and I don't want to be one. But a thing that grows in layers around whatever's near it keeps a list whether anyone asks it to or not, and this cavern is three years old, and there are things in the deep druse.",
        "Leave anything you can't lift. I'd rather know it's there than have you break your back for it.",
    ),
    'hg_shardmaw': (
        "Go to the east bay, where the gallery is widest and the crystal is thinnest. It's lined with teeth and it isn't a mouth, and I've given up trying to describe it better than that.\n\nIt takes the light off you while you're fighting it. Everything you can see gets further away. Go in expecting that, because the first ten seconds of discovering it are what killed Veshan.\n\nThe diggers named it Shardmaw.",
        "Carry a second light. When it takes the first, you'll be glad of it.",
    ),
    'hg_prism': (
        "I hold that the Codex are cataloguers and not colonists, and I hold it sincerely. It's become harder to hold since the inner cavity produced something that stands in a throat and refuses passage, because a thing that guards is a thing that was posted. Go to the Hollow Geode, east of the Bastion, through its north throat and into the inner cavity, where the Prism Warden will be standing in the way. It splits what it casts, so one lance leaves it and three arrive, and two of the three aren't there in any sense you can test, except that standing in them hurts. Don't try to work out which is real while it's happening, because people have, and they were right, and they were still on the floor.",
        'Keep moving the whole time. Standing still is how the false lances find you.',
    ),
    'hg_heartgrown': (
        "The core of the Geode is the only generous room in it, and it's generous because it's the part the crystal hasn't finished eating. Something is growing in the middle of it that our own measurements put at a different size every quarter, always larger, and the quarter before last it grew a fist. It's entered in the Codex as the Heartgrown. Go to the core of the Hollow Geode, east of the Bastion, through the last throat, which is the tightest thing on the map and the way you'll have to come back out. It'll try to close the room while you're in it, so finish it quickly or don't start.",
        "Mark the throat on your way in. When the room starts closing, you'll want to find it without looking.",
    ),
    'db_portico': (
        "Go down the throat and into the first hall. You won't need telling when you're in it.\n\nWalk to the far end and then turn round and look at what you came through. The proportions are right. The columns are spaced right. It's never seen a building or a column, and the only stone it has to go on is what's in the Colonnade, and it's got it almost right. Almost is worse than wrong. I want you to feel that before you go any deeper.",
        'Touch one of the columns before you leave, and tell me what it felt like.',
    ),
    'db_thralls': (
        "Kill all of them, and work the galleries rather than the central hall. They're ranked along the shelving the way books are, and they didn't fall that way by accident.\n\nI'm going to ask you to do something and I'm not going to explain it. If any of them is wearing crimson, bring the clasp, just the clasp. I'll handle it from there, and I'd rather the Hall didn't.\n\nThe Deep Bloom is south-west of the Bastion, at the bottom of the Dim Reaches.",
        "Wrap the clasps in cloth before you bring them up. I don't want them seen on the way through the Bastion.",
    ),
    'db_index': (
        "Go to the Deep Bloom, in the south-west of the Underdark. Go up its central hall, past the shelf-ranks, to where the galleries meet.\n\nI want to be honest with you about why I'm sending you and not the Warden. Ysolde would burn it. I want it stopped, and I want it intact enough to read afterwards. Those instructions pull against each other, and you're the one who'll be standing there deciding which you were given.",
        "Whichever you choose, tell me honestly when you're back. I won't argue with it.",
    ),
    'db_grown_page': (
        "It's a page, with the weight of a page and the give of a page and a margin, and down the recto there's writing in close ranked lines. It wasn't written. The fibres run through the letters, and the marks are part of the sheet, grown in place the way a leaf grows its veins. It's warm, and it shouldn't be. The shelf-grown in the ranks of the Deep Bloom fling them, and Archivist Nessaly at the Bastion will want more, enough to lay side by side and see whether it's writing the same thing over and over or something different each time.",
        "You hold the page flat against your chest. It's still warm when you put it away.",
    ),
    'db_second_copy': (
        "Past the stacks the Bloom built a gallery it liked, and then it built the gallery again, eighteen paces further on, identically, without noticing it already had one. Where the two copies meet there's a seam, and in the seam something else is doubled, which the Codex has entered as the Second Copy. I've drawn both halls from the porters' accounts, and I can't find a single line that differs. You'll know the seam when you reach it in the Deep Bloom, south-west of the Bastion, because you'll be certain you've already walked this hall, and you'll be right. Whatever is in the join does everything twice, and the second time is worse, so don't wait to see the pattern, because the pattern is the weapon.",
        "Hit it hard the first time. A copy of a copy drifts, and you don't want to be there when it does.",
    ),
    'db_errata': (
        "There are two of them. The Scriptor is first. It's in the scriptorium, it's still working, and it'll transcribe the fight while it's having it.\n\nThen go down. What's below is entered as Errata. It's made of mistakes and it's larger than any one of them, and I want you to look at it and then come back and tell the Codex-Master to her face that this is a thing worth reading.\n\nThe Deep Bloom is south-west of the Bastion, at the bottom of the Dim Reaches.",
        "Don't let the Scriptor finish its page. I'd rather it never had an ending.",
    ),
    'db_what_it_learned': (
        "The Warden wants it burned. I've said no eleven times and I'll say no a twelfth, and then I'm sending you to end it, and I'm aware of how that looks.\n\nBurning destroys the record. Killing it doesn't. The stacks remain, the pages remain, and what it's written stays written. I want it stopped and I want it legible. If you think that's a distinction I've invented to let myself sleep, go down there and read one page, and then come back and tell me.\n\nThe Deep Bloom is in the south-west of the Underdark. It's at the bottom of everything it's written.",
        "Go down rested. The stacks are long, and I'd like you clear-headed when you reach the bottom.",
    ),
}
