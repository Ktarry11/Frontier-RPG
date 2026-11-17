# The Plaguelands' towns, as their own maps (plan, 16 Nov 2026)

Kyle: "The Bulwark, The Pale Watch need to be seperate zones and stand alone towns. Remove Sorrow Hill and Move these
people into the Bulwark. We don't need 2 flight paths in one zone wtf. Move Crown Guard into Lights Hope Chapel and
Make it as a seperate town (similar to everything else in the game) Bro you KNOW this - when a town is made it's
always a seperate map." Then: "Also fold Crown Guard Camp into Lights Hope".

## The Bulwark (its own map, off South WPL's west gate)
- The road from Eastern Tirisfal arrives at the Bulwark's west gate; its east gate opens onto South WPL where the
  Bulwark used to stand. You can't reach the Plaguelands from Tirisfal without walking through it.
- Two quarters, because the two sides don't love each other: the Forsaken's wall and works (Venn, Vesk, Rook,
  Vance, Grey, the apothecary vats, the barracks), and the Order of the Pale Flame's camp inside the walls (Rory,
  Kofi, Odile, Priya, Agata, Aldren, the Order's quartermaster), moved down from Sorrow Hill.
- One inn, one flight master (the bat handler; the Order's roost goes), one of each service.

## Sorrow Hill (stays a place, stops being a hub)
- Uther's Tomb and the hill stay on South WPL's map. The Order's keep, its people and its flight path go; the hill
  goes back to graves, the tomb and the old road.

## The Pale Watch (its own map, off North WPL)
- The Order's forward camp under Hearthglen, a small walled town with an inn and a flight master (North WPL has
  none). The seven people who stand there now move in.

## Light's Hope Chapel (its own map, off East EPL)
- The Argent Dawn's chapel town. Crown Guard Camp's people move in (the captain, corporal, outrider, widow,
  mycologist, gravewarden); one inn, one flight master. Crown Guard Tower stays on the map as a landmark, empty.

## Everything that follows from it
- portals both ways; the flight nodes (Sorrow Hill and Crown Guard removed, the Pale Watch added); the zone level
  table; the respawn towns; the quests' zones, explore points and "Sorrow Hill" in their text; the givers-in-hubs
  rule in build_plaguelands_quests; the faction "also" lists; secrets near the old hubs.

## Built (16 Nov 2026)
- **The Bulwark** (tools/handbuilt_bulwark.py, 104x80): west gate to Eastern Tirisfal, east gate to South WPL. The
  Forsaken north of the street, the Order south of it. Priya Raman cooks for the Order and Anders Holm's hawks carry
  its letters; neither is an inn or a flight point now (the Forsaken's are).
- **The Pale Watch** (tools/handbuilt_pale_watch.py, 88x72): its gate is off North WPL's King's Road at (80,112). A new
  innkeeper (Beatriz Couto) and roostkeeper (Liam Doherty), so the Order's people at the Bulwark kept their jobs there.
- **Light's Hope Chapel** (tools/handbuilt_lights_hope.py, 96x80): its gate is up a spur off East EPL's Tyr's Hand road
  at (128,72). Crown Guard's people live inside; Greta Lowe keeps the kitchen and Gwen Pike nurses the bats.
- Sorrow Hill is graves with skeletons on it; Crown Guard Tower stands empty. Flight points: the Bulwark, the Pale
  Watch, Light's Hope (Sorrow Hill and Crown Guard retired; a save that knew them forgets them).
- Every Plaguelands quest is in its giver's voice now (tools/plaguelands_quest_voice.py, Emerald Sanctuary's shape).
- Ten of the Order's, the Forsaken's and the Dawn's people wear Kyle's new art (assets/npcs/leaders/<id>/).
