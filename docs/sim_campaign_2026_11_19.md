# The levelling run, 19 Nov 2026

Kyle: "please do start a lvl 1 to 60 simulated run. As a tank, as a Healer, as a dps. See how it is to quest open world solo etc. I know we saw overtuned rares last night....so there are cracks." Tool: `tools/sim_campaign.py` (how it plays is in its docstring). Protection Warrior, Holy Priest and Fire Mage, solo, geared as a levelling player, seed 1.

```
=== warrior_protection (tank): reached level 60, 9 quests never done
levels | quests  failed dungeon | fights  win%  deaths  grind | hp left  turns | rests/fight | rares met (lost) | XP quests / kills / needed
 1- 5  |    20      0       0 |    132  97.7      3      0 |    0.86    3.1 |        0.06 |     2 (2) |    2450 /    3958 / 5854
 6-10  |    53      0       6 |    298  99.3      2      0 |    0.90    3.3 |        0.06 |     0 (0) |    9384 /   12993 / 21023
11-15  |    99      3       4 |    547  94.5     30      0 |    0.93    3.8 |        0.04 |     2 (1) |   22332 /   35430 / 40307
16-20  |    97      0       7 |    513 100.0      0      0 |    0.96    2.6 |        0.01 |     2 (0) |   25351 /   37377 / 62460
21-25  |   139      0       4 |    946  99.6      4      0 |    0.97    2.4 |        0.01 |     3 (0) |   38794 /   55526 / 86912
26-30  |   159      1      23 |    965 100.0      0      0 |    0.97    2.2 |        0.00 |     3 (0) |   57899 /   55425 / 113314
31-35  |   124      0      23 |    752 100.0      0      0 |    0.96    2.4 |        0.00 |     1 (0) |   59222 /   82259 / 141431
36-40  |   103      0      28 |    936 100.0      0      0 |    0.96    2.8 |        0.00 |     0 (0) |   52645 /  121519 / 174128
41-45  |   122      1      27 |   1084 100.0      0      0 |    0.96    2.4 |        0.00 |     1 (0) |   73023 /  162228 / 234933
46-50  |   109      0      18 |    950  99.9      1      0 |    0.92    2.7 |        0.00 |     1 (1) |  104216 /  271618 / 362764
51-55  |   169     10      16 |   1378  95.3     65      0 |    0.84    3.7 |        0.03 |     2 (2) |  274613 /  666475 / 604588
56-60  |   255     43      59 |   2609  89.7    270    653 |    0.75    4.4 |        0.12 |     7 (6) |  507199 / 1534648 / 770044
killed by: Kolkar Raider x8, Vor'alith the Turncloak x7, Old Darrowjaw x7, Gatekeeper Vorthas x7, The Fungal Mass x7, Captain Redpath's Shade x7, Meven Korgal x6, Matron Sowbelly x6, Stormhide Patriarch x6, The Keeper of the First Page x6, Old Mossback x6, Farmer Felstone x6
rares that killed it: Gaffer Thorne (L6, you L4), Broodmother Sarrix (L5, you L4), Warlord Krellian (L12, you L13), The Wide Sink Mother (L46, you L50), Thirstjaw (L47, you L51), The Gloomcap Elder (L52, you L55), Vor'alith the Turncloak (L55, you L56), Old Darrowjaw (L53, you L56), Gatekeeper Vorthas (L58, you L57), The Fungal Mass (L57, you L57), The Bone Colossus (L60, you L58), Captain Redpath's Shade (L58, you L58)
```

```
=== priest_holy (healer): reached level 60, 9 quests never done
levels | quests  failed dungeon | fights  win%  deaths  grind | hp left  turns | rests/fight | rares met (lost) | XP quests / kills / needed
 1- 5  |    26      2       0 |    196  91.8     16      0 |    0.84    5.6 |        0.05 |     1 (1) |    3470 /    6005 / 5854
 6-10  |    59      5       6 |    385  82.3     68      0 |    0.86    8.6 |        0.05 |     0 (0) |   14075 /   21140 / 21023
11-15  |    68      1       3 |    379  98.2      7      0 |    0.90    3.9 |        0.01 |     0 (0) |   15692 /   26150 / 40307
16-20  |   111      0       8 |    586  99.8      1      0 |    0.90    2.7 |        0.01 |     0 (0) |   27561 /   36915 / 62460
21-25  |   141      1       4 |    998  97.0     30      0 |    0.93    2.9 |        0.00 |     2 (0) |   39735 /   50925 / 86912
26-30  |   155      2      23 |    961  98.8     12      0 |    0.93    2.6 |        0.00 |     3 (0) |   56316 /   58774 / 113314
31-35  |   126      1      23 |    780  99.7      2      0 |    0.89    2.8 |        0.02 |     1 (0) |   60771 /   89571 / 141431
36-40  |   101      0      28 |    932 100.0      0      0 |    0.89    2.8 |        0.00 |     0 (0) |   52322 /  121785 / 174128
41-45  |   122      0      27 |   1085 100.0      0      0 |    0.93    2.2 |        0.00 |     1 (0) |   73357 /  161607 / 234933
46-50  |   124      1      24 |   1121  99.2      9      0 |    0.92    3.6 |        0.01 |     3 (3) |  125144 /  340147 / 362764
51-55  |   195     18      14 |   1599  93.2    108      0 |    0.86    4.9 |        0.04 |     1 (0) |  348766 /  862299 / 604588
56-60  |   215     33      55 |   2128  90.4    205    618 |    0.86    5.1 |        0.03 |     0 (0) |  440296 / 1294354 / 770044
killed by: Peat Shambler x30, Blighted Scarecrow x18, Kolkar Raider x17, Broodmother Sarrix x7, Bleak Worg x7, Old Tusk x6, Old Gulpjaw x6, Sandfang x6, Ressan the Needler x6, Matron Sowbelly x6, Amberheart, the Sap-Mother x6, The Root-Father x6
rares that killed it: Broodmother Sarrix (L5, you L5), Paneater (L40, you L46), Underlight (L47, you L50), Longcollapse (L47, you L50)
```

```
=== mage_fire (dps): reached level 60, 9 quests never done
levels | quests  failed dungeon | fights  win%  deaths  grind | hp left  turns | rests/fight | rares met (lost) | XP quests / kills / needed
 1- 5  |    23      1       0 |    177  92.7     13      0 |    0.71    2.9 |        0.21 |     0 (0) |    2897 /    5387 / 5854
 6-10  |    97     14       9 |    678  80.8    130      0 |    0.83    2.1 |        0.09 |     1 (1) |   24806 /   41937 / 21023
11-15  |    62      7       3 |    401  88.5     46      0 |    0.84    1.7 |        0.08 |     1 (1) |   22229 /   41351 / 40307
16-20  |    87      0       5 |    494  98.8      6      0 |    0.93    1.2 |        0.03 |     1 (0) |   27680 /   46061 / 62460
21-25  |   129      3       4 |    929  94.9     47      0 |    0.94    1.3 |        0.02 |     2 (0) |   41545 /   64788 / 86912
26-30  |   184      7      30 |   1195  95.8     50      0 |    0.92    1.6 |        0.02 |     3 (0) |   78810 /  103099 / 113314
31-35  |    89      1      17 |    615  99.5      3      0 |    0.89    1.7 |        0.04 |     0 (0) |   51520 /  102793 / 141431
36-40  |    98      0      30 |    874  99.9      1      0 |    0.86    2.1 |        0.03 |     0 (0) |   52745 /  124701 / 174128
41-45  |   118      1      24 |   1073 100.0      0      0 |    0.88    1.7 |        0.02 |     0 (0) |   71282 /  163230 / 234933
46-50  |   106      0      18 |    920 100.0      0      0 |    0.82    1.6 |        0.08 |     2 (0) |  100783 /  262088 / 362764
51-55  |   169      9      16 |   1363  95.1     67      0 |    0.68    2.1 |        0.29 |     1 (1) |  273226 /  659491 / 604588
56-60  |   263     39      59 |   6161  91.1    550   4039 |    0.53    2.3 |        0.52 |     3 (3) |  532090 / 3896100 / 770044
killed by: Peat Shambler x30, Kolkar Raider x29, Flicker Hound x27, Tumour Wolf x22, Forlorn Eredar x22, Legash Felhound x21, Fused Bat x21, Scoria Fire Elemental x20, Forlorn Doomguard x18, Stopped Volunteer x16, Forlorn Imp x12, Marris Ossuary Guard x12
rares that killed it: Captain Vachon (L11, you L9), Captain Vachon (L11, you L12), Hive Champion Khix'ar (L53, you L52), Sootwing (L55, you L57), Cartmaster Corin (L57, you L57), Captain Ssarith (L58, you L58)
```

## The rare census

Every open-world subzone rare, five fights per spec at the rare's own level.

```
=== rare census: 248 subzone rares, 5 fights per spec at the rare's level
244 rares that a spec beats under 60% of the time:
  L59 Abbot Varenne                      warrior   0% 0.00  priest  20% 0.19  mage   0% 0.00
  L21 Ancient Curse-Beast                warrior 100% 0.33  priest  60% 0.25  mage   0% 0.00
  L37 Archivist Thelun, Unlisted         warrior   0% 0.00  priest  60% 0.41  mage   0% 0.00
  L45 Axleback                           warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L57 Azurewing                          warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L22 Baron Ashbury                      warrior 100% 0.44  priest  60% 0.46  mage   0% 0.00
  L19 Berard the Forgotten               warrior 100% 0.51  priest  80% 0.57  mage   0% 0.00
  L10 Bethor Iceshard                    warrior   0% 0.00  priest 100% 0.53  mage  40% 0.02
  L12 Bloodhoof the Lamed                warrior  20% 0.05  priest   0% 0.00  mage   0% 0.00
  L20 Bloodmaw the Alpha                 warrior 100% 0.53  priest   0% 0.00  mage   0% 0.00
  L54 Borrik the Unhoused                warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L30 Bristlehide the Wintered           warrior  80% 0.27  priest   0% 0.00  mage   0% 0.00
  L28 Broadpaw                           warrior 100% 0.45  priest 100% 0.59  mage   0% 0.00
  L24 Brontus                            warrior  60% 0.19  priest   0% 0.00  mage   0% 0.00
  L 5 Broodmother Sarrix                 warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L35 Capgorger                          warrior   0% 0.00  priest 100% 0.71  mage  20% 0.04
  L10 Captain Dargol                     warrior   0% 0.00  priest   0% 0.00  mage  20% 0.07
  L10 Captain Melrache                   warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L14 Captain Morrow                     warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L42 Captain Orlee Vantch               warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L42 Captain Orlee Vantch               warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L58 Captain Redpath's Shade            warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L17 Captain Saltspray                  warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L58 Captain Ssarith                    warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L11 Captain Vachon                     warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L22 Captain's Ghost                    warrior 100% 0.37  priest 100% 0.89  mage   0% 0.00
  L57 Cartmaster Corin                   warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L55 Chieftain Grimpelt                 warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L10 Crusader Brennic                   warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L18 Deathguard Captain                 warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L37 Drumhide                           warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L37 Drumhide                           warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L20 Dustmaw the Rift-Lurker            warrior 100% 0.64  priest  20% 0.19  mage   0% 0.00
  L15 Echo of the Fallen Warrior         warrior   0% 0.00  priest  40% 0.39  mage   0% 0.00
  L19 Engineer Whirleygig                warrior  80% 0.42  priest  80% 0.51  mage   0% 0.00
  L52 Farmer Felstone                    warrior   0% 0.00  priest   0% 0.00  mage   0% 0.00
  L23 Felstalker                         warrior  80% 0.18  priest   0% 0.00  mage   0% 0.00
  L24 Field Marshal Calder               warrior 100% 0.42  priest   0% 0.00  mage   0% 0.00
...
```
