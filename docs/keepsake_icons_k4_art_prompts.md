# Keepsake icons, sheet K4: Dawnhaven's three bears, Sheet 6's twelve and the Mural Shard

Written 21 Nov 2026. Fifteen recruits joined after K1 to K3 (20 Nov), and the Mural Shard came with the Crown cutscene,
so these sixteen still show stand-ins. Same rules as K1 to K3: small, worn real-world objects in the game's icon style.
The Mural Shard is the one exception, because it's a piece of the World Tree's mural and not something from Earth.
Attach `qi_journal.png`, `qi_horn.png` and `qi_signet.png` as the style reference.

## SHEET K4: sixteen keepsakes (paste this whole block)

```
Generate ONE image, 1024x1024, a grid of 4 columns x 4 rows = 16 separate square inventory icons, each about 256x256. Flat pure #FF00FF magenta background around each icon, with a wide margin, nothing touching the neighbours or the image edge. Each icon is ONE object, centred, filling about 75% of its cell, drawn as a classic WoW Classic inventory icon: painterly, rich colour, strong silhouette readable at 40 pixels, soft dark outline, lighting from the top-left, a slight 3/4 view. No frames, no borders, no text, no letters or numbers anywhere, no logos or brand marks, no magenta or pink inside the icons. Icons 1 to 15 are small, well-worn personal keepsakes from our own world, the kind of thing someone carried for years: scuffs, fading, polish from a hand. Where a description mentions writing, a name, a title or a label, draw it as blank or unreadable marks. Draw only the object, never a person or a hand.

Icons, row by row, left to right:
Row 1: 1 a Welsh scaffolder's podger spanner, a ring spanner at one end tapering to a long steel spike at the other, worn smooth, on a frayed cord loop; 2 a string of worn honey-amber worry beads on a dark silk cord with a tassel, the beads polished by thirty years of fingers; 3 a logger's diameter tape in a dented round steel case with a hook on the end of the yellow tape, a few scratched marks on the back; 4 a beekeeper's hive tool, a flat steel bar with one hooked end, the paint long worn off the grip and a little old wax on the blade.
Row 2: 5 a slim steel tree-core drill, a T-handle wrapped in faded tape on a long hollow bit, half out of a worn canvas sleeve; 6 a big oval silver rodeo belt buckle with a bull rider in relief and a raised rim, polished thin at the edges; 7 a brass notary's seal, a heavy round stamp with a turned wooden handle, its die worn soft, on a short brass chain; 8 a brass lobster gauge, a flat notched measuring bar for a lobster's shell, gone green at the edges, on a loop of tarred twine.
Row 3: 9 a marigold flower folded from bright orange paper, with a safety pin through the stem; 10 a red and white knitted winter toque with a pom-pom, stretched at the brim and darned over one side; 11 a slim silver medical pen-torch with a pocket clip bent out of shape, its little bulb glowing warm; 12 a jeweller's loupe, a small black cone with a bright brass rim, on a worn leather cord.
Row 4: 13 a red bandana with a faded paisley pattern, knotted into a loop as if tied round a wrist, faded at the folds; 14 a creased blood donor card, pale with a red drop symbol and rows of tiny blank date boxes filled edge to edge with handwritten marks; 15 a tiny blue glass fish, a little lopsided, with a glossy hand-blown look and a bubble trapped inside; 16 THIS ONE IS NOT FROM OUR WORLD: a jagged flake of ancient painted stone from a temple mural, pale plaster with old ochre and blue paint and a curve of bright gold sun across one corner, glowing faintly gold at the edges.
```

Sliced by `python3 tools/asset_pipeline/slice_collection_icons.py SHEET.png --cols=4 --ids=col_keepsake_rhodri,col_keepsake_yiannis,col_keepsake_leif,col_keepsake_alvaro,col_keepsake_clara,col_keepsake_raul,col_keepsake_federico,col_keepsake_connor,col_keepsake_mauricio,col_keepsake_etienne,col_keepsake_oliver,col_keepsake_facundo,col_keepsake_renata,col_keepsake_tariq,col_keepsake_isabela,col_keepsake_mural_shard`.
