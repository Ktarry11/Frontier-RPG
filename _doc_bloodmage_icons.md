# Bloodmage icon sheets: 157 icons in FOUR images

Status: PROPOSED 2026-10-29, waiting for Kyle to generate the images.
Second of the thirteen CoA classes with no art of its own, and the largest
of them. Run `python3 tools/audit_icon_coverage.py --list bloodmage` for
the live gap.

**What is missing.** 92 talents across four trees, 55 abilities with no
icon, and 10 abilities sharing the generic `ability_melee` sword. Zero
PNG files in the repo start with "bloodmage". Nothing is mis-wired: the
renderer resolves `assets/icons/<abilities|talents>/<id>.png` and falls
back to the id when the JSON has no explicit `icon_id`, so the art starts
working the moment the files exist under the right names.

**Theme, and the reason it needs care.** Bloodmage is San'layn - the
Darkfallen, with Lana'thel, Valanar, Keleseth, Taldaram and Atherann named
throughout its talents - so the whole class is blood and Shadow, and
*everything* is red. That is the problem: four trees of 23 icons each in
one palette will read as one undifferentiated red smear on the talent
screen. The sheets below separate the trees by SUBJECT rather than colour:

- **Accursed** - feral and bestial. Fangs, claws, open veins, the body
  used as a weapon. Darkest red, nearly black, with bone white.
- **Eternal** - defensive and nocturnal. Hide, plate, blood worn as
  armour, night. Deep crimson with cold blue-grey night tones.
- **Fleshweaver** - the healer. Stitched flesh, organ orbs, surgery,
  mending. Warm red with bone and pale cloth.
- **Sanguine** - the caster. Bolts, chalices, sigils, floating spheres of
  blood. Bright arterial red with violet Shadow.

Keep those four palettes distinct and the class reads; let them blend and
the player cannot tell one tree from another.

---------------------------------------------------------------------
## SHEET 1 - Accursed and Eternal trees (48 icons)

PROMPT (paste this whole block):

Generate ONE sprite sheet image, 1536x1152, an 8 columns x 6 rows grid = 48
separate ability icons (each cell 192x192). Flat pure #FF00FF magenta
background everywhere. Each icon is centred in its own cell with a wide
margin, not touching or overlapping its neighbours or the image edge.
Painterly semi-realistic World of Warcraft Classic ability-icon style: one
bold symbolic composition per cell, strong readable silhouette, soft dark
outline, chunky simple shapes, soft lighting from the top-left, no text, no
letters, no labels, no grid lines, no frames or borders, no full human
figures and no faces except where a prompt asks for a skull or fangs.
Vampiric blood magic: dark arterial red, black, bone white, violet shadow.
Cells 1 to 23 are FERAL and bestial - fangs, claws, open veins, nearly
black reds. Cells 24 to 48 are DEFENSIVE and nocturnal - hide, plate, blood
worn as armour, deep crimson with cold blue-grey night tones. Avoid magenta
or pink inside any icon. Row by row, left to right:

Row 1:
1. a clenched fist with dark blood running between the knuckles, red haze
   around it
2. a torn forearm with the skin split lengthwise, blood welling out
3. a black spiked sigil floating above an open palm, violet light beneath
4. a single long curved fang with a bright gleam along its edge
5. a swirl of violet-black shadow curling around a drop of blood
6. two red-stained claw tips crossed over a small bright flash
7. a snarling fanged jaw half-wrapped in dark cloth, one eye glowing red
8. a bare chest with three deep parallel claw gouges, blood running

Row 2:
9. two bursting veins spraying dark blood outward in opposite arcs
10. a broken shackle with blood on the inside of the cuff
11. a fist-sized shard of hardened dark blood, faceted like glass
12. a fanged maw closing on empty air with a second ghosted maw behind it
13. a curved claw sweeping down with a trailing red afterimage
14. a long reaving claw with four thin red slashes behind it
15. a black rune burned into skin, blood beading along its lines
16. an open book bound in dark red leather, blood pooling in the gutter

Row 3:
17. a bare shoulder and arm with veins standing out black under the skin
18. an hourglass made of blood with the sand running upward
19. two long fangs side by side, both dripping, one longer than the other
20. a dark red waterskin squeezed until it splits
21. a nose and snarling upper lip scenting the air, red vapour drawn in
22. a black sigil with violet light detonating out of its centre
23. a pair of wide-open eyes with slit pupils, burning bright red, nothing
    else visible

Row 4:
24. a lowered shoulder braced sideways, blood-slick hide over it, cold
    moonlight
25. a dark red heart with a faint pulse of light inside, cradled in ribs
26. a crouched beast's legs mid-step, silent, pale moonlight behind
27. a thick matted pelt stretched over a curved iron plate
28. a broad ribcage seen head-on, thick and heavy, deep crimson
29. a figure dissolving into smoky black shadow at the edges, only the
    silhouette left
30. a corded forearm gripping a bone haft, muscle fibre visible
31. an iron shoulderplate with a blow glancing off it, sparks and a smear
    of blood
32. a full red moon low behind a bare black branch

Row 5:
33. an open wound knitting itself closed with threads of dark red
34. a crit-flash starburst in cold white over a deep crimson field
35. two curved iron claws, polished, with armour shavings curling off them
36. a round red brand burned into a shield face
37. a cracked crimson mask with a single eye behind the crack
38. a blurred pair of beast legs at a dead sprint, dust and night air
39. a wolf's throat thrown back mid-howl, black against a red moon
40. a tall gaunt silhouette standing upright with arms slightly spread,
    crimson aura

Row 6:
41. a dodging silhouette leaning hard aside with a claw passing through
    where it was
42. a wound tearing wider with a bright red rage-flare bursting from it
43. two long claws dripping thick dark blood from the tips
44. a pair of narrowed glowing red eyes in total blackness, seen in profile
45. a black iron gauntlet closing around a glowing red sphere
46. a cloaked back turned to the viewer, one red eye looking over the
    shoulder
47. a crimson cloak flaring outward as a blow is taken on the forearm
48. a tall black-and-crimson figure standing with the red moon directly
    behind its head

### SHEET 1 slicing map

All go to `assets/icons/talents/<name>.png`.

| # | File |
|---|---|
| 1 | bloodmage_accursed_rage |
| 2 | bloodmage_accursed_barely_human |
| 3 | bloodmage_accursed_forbidden_power |
| 4 | bloodmage_accursed_killer_instinct |
| 5 | bloodmage_accursed_dark_hunt |
| 6 | bloodmage_accursed_crimson_expedition |
| 7 | bloodmage_accursed_one_mans_curse |
| 8 | bloodmage_accursed_relentless |
| 9 | bloodmage_accursed_gore_barrage |
| 10 | bloodmage_accursed_unchained |
| 11 | bloodmage_accursed_blood_shards |
| 12 | bloodmage_accursed_cruel_intent |
| 13 | bloodmage_accursed_everlasting_hunt |
| 14 | bloodmage_accursed_fang_over_fang |
| 15 | bloodmage_accursed_dark_sigil |
| 16 | bloodmage_accursed_sanguine_scripture |
| 17 | bloodmage_accursed_battleweaver |
| 18 | bloodmage_accursed_crimson_feast |
| 19 | bloodmage_accursed_terrorizer |
| 20 | bloodmage_accursed_night_hunter |
| 21 | bloodmage_accursed_blood_scent |
| 22 | bloodmage_accursed_darkcasting |
| 23 | bloodmage_accursed_ultra_instinct |
| 24 | bloodmage_eternal_heightened_reflexes |
| 25 | bloodmage_eternal_eternal_hunt |
| 26 | bloodmage_eternal_uncanny_movement |
| 27 | bloodmage_eternal_thick_pelt |
| 28 | bloodmage_eternal_vitality |
| 29 | bloodmage_eternal_shadows_in_the_night |
| 30 | bloodmage_eternal_feral_strength |
| 31 | bloodmage_eternal_no_mercy |
| 32 | bloodmage_eternal_blood_moon |
| 33 | bloodmage_eternal_infection |
| 34 | bloodmage_eternal_appetite_for_blood |
| 35 | bloodmage_eternal_rejuvenating_shadows |
| 36 | bloodmage_eternal_grim_omen |
| 37 | bloodmage_eternal_iron_claws |
| 38 | bloodmage_eternal_blood_mark |
| 39 | bloodmage_eternal_dark_mark |
| 40 | bloodmage_eternal_uncanny_speed |
| 41 | bloodmage_eternal_rabid |
| 42 | bloodmage_eternal_eternal_presence |
| 43 | bloodmage_eternal_bloodmoon_power |
| 44 | bloodmage_eternal_enraging_wounds |
| 45 | bloodmage_eternal_bloody_claws |
| 46 | bloodmage_eternal_eyes_in_the_night |
| 47 | bloodmage_attack |
| 48 | bloodmage_lunge |

Cells 47-48 are ABILITIES and go to `assets/icons/abilities/` instead.
Cell 47 should read as a plain neutral weapon strike and cell 48 as a
lunging closing-the-distance attack - adjust those two cells in the prompt
if the generated sheet gives them talent-like sigils.

---------------------------------------------------------------------
## SHEET 2 - Fleshweaver and Sanguine trees (48 icons)

PROMPT (paste this whole block):

Generate ONE sprite sheet image, 1536x1152, an 8 columns x 6 rows grid = 48
separate ability icons (each cell 192x192). Flat pure #FF00FF magenta
background everywhere. Each icon is centred in its own cell with a wide
margin, not touching or overlapping its neighbours or the image edge.
Painterly semi-realistic World of Warcraft Classic ability-icon style: one
bold symbolic composition per cell, strong readable silhouette, soft dark
outline, chunky simple shapes, soft lighting from the top-left, no text, no
letters, no labels, no grid lines, no frames or borders, no full human
figures and no faces. Cells 1 to 23 are SURGICAL and restorative - stitched
flesh, organ orbs, needles, mending, warm red with bone white and pale
cloth. Cells 24 to 48 are ARCANE blood casting - bolts, chalices, floating
spheres, sigils, bright arterial red with violet shadow. Avoid magenta or
pink inside any icon. Row by row, left to right:

Row 1:
1. a pale cupped hand holding a small glowing red orb, thin light rising
2. three small dark red organ-orbs floating in a loose cluster
3. two red threads pulled tight and knotted together
4. a red droplet falling into an open palm and flaring on contact
5. an open book with a surgical needle laid across the page, red thread
   trailing
6. a torn piece of flesh being drawn closed by crossing threads
7. an hourglass of dark blood with a slow steady drip at its waist
8. two cupped hands passing a glowing red sphere between them

Row 2:
9. a dark heart with a bright red thread stitched through it
10. a glass vial of bright blood with a needle driven into the stopper
11. a wave of red spilling sideways out of a shallow bowl
12. a wide shallow bowl of bright blood with light rising from its surface
13. a black ritual knife laid across a folded cloth, one drop on the blade
14. an hourglass turned on its side with red sand pouring out freely
15. a leather pouch with a red glow leaking through its seams
16. a pale needle threaded with glowing red, pointing upward

Row 3:
17. a wide red splash spreading flat and reaching three directions
18. a ruptured heart with a bright crack across it, light inside
19. a steady hand holding a needle poised above an open wound
20. a bright white crit-flash over a small red sphere
21. a blurred pair of hands working fast, red threads trailing between them
22. a tall red flame burning with no wick, floating
23. a great anvil of dark red flesh with threads of light running through it

Row 4:
24. a bolt of bright arterial red shooting forward, trailing droplets
25. a dark chalice with blood swirling in it, violet shadow curling off
26. two blood bolts crossing in flight, one brighter than the other
27. a floating sphere of blood held between two curved bone hooks
28. a slow heavy orb of dark blood with a red moon reflected in it
29. a violet-black sigil with blood running down its lines
30. a wide red shockwave rolling outward in a flat ring
31. a scattering of tiny red mites swarming over a blood drop
32. a single long fang driven into a glowing red sphere, blood climbing it

Row 5:
33. an ornate silver goblet overflowing with bright blood
34. a dark red bubble around a shrinking black shape
35. a spreading red stain with violet veins creeping through it
36. two bone hooks pulling a strand of blood taut between them
37. a thin red thread running from a wound to a cupped hand
38. a heavy black crown resting in a pool of blood
39. a cloud of black flies rising off a red smear
40. a violet-black shadow-wreath around a single bright red point

Row 6:
41. a red bleeding gash with violet shadow leaking from it
42. a fang-pierced sphere with a thin stream of blood climbing back up the
    fang
43. a tall column of bright blood rising from a dark pool
44. a black sigil hanging above a full chalice, violet light between them
45. three bright red bolts fanning out from one point
46. a blood-red crown of thorns closed in a circle
47. a dark throne of bone with a single red sphere hovering above its seat
48. a towering figure of blood and violet shadow, crowned, arms lowered

### SHEET 2 slicing map

All go to `assets/icons/talents/<name>.png`.

| # | File |
|---|---|
| 1 | bloodmage_fleshweaver_gift_of_lanathel |
| 2 | bloodmage_fleshweaver_organ_orbs |
| 3 | bloodmage_fleshweaver_consolidation |
| 4 | bloodmage_fleshweaver_raging_hunger |
| 5 | bloodmage_fleshweaver_teachings_of_lanathel |
| 6 | bloodmage_fleshweaver_excess_blood |
| 7 | bloodmage_fleshweaver_spice_of_life |
| 8 | bloodmage_fleshweaver_blood_redistribution |
| 9 | bloodmage_fleshweaver_black_heart |
| 10 | bloodmage_fleshweaver_sanguine_scion |
| 11 | bloodmage_fleshweaver_waves_of_blood |
| 12 | bloodmage_fleshweaver_universal_donor |
| 13 | bloodmage_fleshweaver_gruesome_rituals |
| 14 | bloodmage_fleshweaver_dissipation |
| 15 | bloodmage_fleshweaver_crimson_scion |
| 16 | bloodmage_fleshweaver_vitality_for_later |
| 17 | bloodmage_fleshweaver_sovereignty |
| 18 | bloodmage_fleshweaver_heart_rupturer |
| 19 | bloodmage_fleshweaver_invigorated_flesh |
| 20 | bloodmage_fleshweaver_fleshbending |
| 21 | bloodmage_fleshweaver_red_thirst |
| 22 | bloodmage_fleshweaver_bloodcraft |
| 23 | bloodmage_fleshweaver_flesh_foundry |
| 24 | bloodmage_sanguine_atheranns_wickedness |
| 25 | bloodmage_sanguine_darkfallens_embrace |
| 26 | bloodmage_sanguine_blood_banquet |
| 27 | bloodmage_sanguine_cunning_of_atherann |
| 28 | bloodmage_sanguine_the_cup_runneth_over |
| 29 | bloodmage_sanguine_twisted_magic |
| 30 | bloodmage_sanguine_bloodwell_eruption |
| 31 | bloodmage_sanguine_blood_parasites |
| 32 | bloodmage_sanguine_lifedrinker |
| 33 | bloodmage_sanguine_enthraller |
| 34 | bloodmage_sanguine_hematoma |
| 35 | bloodmage_sanguine_dominion_of_blood |
| 36 | bloodmage_sanguine_agonizing_pain |
| 37 | bloodmage_sanguine_reckless_abandon |
| 38 | bloodmage_sanguine_essence_harvester |
| 39 | bloodmage_sanguine_the_council_assembled |
| 40 | bloodmage_sanguine_swarm_of_flies |
| 41 | bloodmage_sanguine_dark_presence |
| 42 | bloodmage_sanguine_crimson_curse |
| 43 | bloodmage_sanguine_torture |
| 44 | bloodmage_sanguine_thirst_for_blood |
| 45 | bloodmage_sanguine_blood_lord |
| 46 | bloodmage_sanguine_crimson_terror |
| 47 | bloodmage_reave |
| 48 | bloodmage_ravenous_strike |

Cells 47-48 are ABILITIES and go to `assets/icons/abilities/`.

---------------------------------------------------------------------
## SHEET 3 - the ability kit, part one (48 icons)

PROMPT (paste this whole block):

Generate ONE sprite sheet image, 1536x1152, an 8 columns x 6 rows grid = 48
separate ability icons (each cell 192x192). Flat pure #FF00FF magenta
background everywhere. Each icon is centred in its own cell with a wide
margin, not touching or overlapping its neighbours or the image edge.
Painterly semi-realistic World of Warcraft Classic ability-icon style: one
bold symbolic composition per cell, strong readable silhouette, soft dark
outline, chunky simple shapes, soft lighting from the top-left, no text, no
letters, no labels, no grid lines, no frames or borders, no full human
figures and no faces. Vampiric blood magic, arterial red and violet
Shadow. These are CAST abilities - they should read as actions and effects
rather than as objects. Avoid magenta or pink inside any icon. Row by row,
left to right:

Row 1:
1. a bolt of bright blood streaking forward with a trail of droplets
2. a heavier slower orb of dark blood with a red moon glow behind it
3. an opened wrist with blood running down into a red haze
4. two cupped hands closing a wound with red light between them
5. a blood-red handshake, two wrists cut and pressed together
6. a humanoid shape half-melted into a flat puddle of dark blood
7. an open howling mouth with a violet shadow-ring expanding from it
8. a hunched shape swelling larger with blood vessels standing out

Row 2:
9. a figure sealed inside a sphere of its own blood
10. torn skin peeled back showing dark red beneath, violet shadow curling
11. a blood transfusion line running from one arm to another
12. a thin film of blood stretched over a round shield shape
13. a body lying still with a red glow rekindling in the chest
14. a blood bolt striking home with a thin red thread returning from it
15. a whole room's worth of blood bending into a single curved wave
16. a dark red plague-bloom opening in cracked ground

Row 3:
17. the ground splitting open under a red burst and closing again
18. a slow deep wound with a thin steady red thread feeding back
19. a long bleeding gash that will not close, blood still running
20. a black spoken sigil hanging in the air with violet cracks spreading
    out
21. a single fang buried deep with blood climbing back up its length
22. a gaunt face-forward silhouette with its mouth open in pure want
23. a bright red rupture bursting behind a pair of eyes
24. a black ritual knife held point-down over an open palm

Row 4:
25. a cloaked figure letting dark blood run openly down both arms
26. a dark curse climbing a throat and stopping at the jaw
27. a hunched beast-shape rising out of a human silhouette, blood dripping
28. a vein found and widened, blood jetting out sideways
29. a body bursting outward in a flat ring of blood
30. a wave of red arriving over a shoulder before the shoulder moves
31. a human face going slack and dark as the last light leaves it
32. a figure standing with every blow landing on it and nothing moving

Row 5:
33. a crouched shape locked in place with a crimson shell around it
34. a curved claw leaving something black and rotting in the wound
35. a throat thrown back in a howl with red lines pulling inward from all
    sides
36. a bared set of fangs pointed at one single spot
37. a howl with the sound visible as grey rings sweeping low along the
    ground
38. a frenzied shape blurred with motion, emerging larger on one side
39. a blurred row of bites landing one after another with no gap
40. a drained grey figure with the red gone out of it entirely

Row 6:
41. two hands pressing a wound closed with warm red light spilling out
42. a heavy strike landing with a red thread arcing back to a second figure
43. a large globe of blood floating above three small shield shapes
44. a flat red tide rolling across the ground toward the viewer
45. an open book held up with red light rising off the page over a group
46. a still figure singing with red threads running out to and from it
47. a mouth bound shut with red cords
48. a sickness being drawn out of an arm as a dark ribbon and dropped

### SHEET 3 slicing map

All go to `assets/icons/abilities/<name>.png`.

| # | File |
|---|---|
| 1 | bloodmage_bloodbolt |
| 2 | bloodmage_bloodmoon_blast |
| 3 | bloodmage_blood_tap |
| 4 | bloodmage_fleshcraft |
| 5 | bloodmage_blood_pact |
| 6 | bloodmage_liquify |
| 7 | bloodmage_shadow_howl |
| 8 | bloodmage_wicked_howl |
| 9 | bloodmage_hemostasis |
| 10 | bloodmage_scarlet_delirium |
| 11 | bloodmage_transfusion |
| 12 | bloodmage_blood_veil |
| 13 | bloodmage_blood_rite |
| 14 | bloodmage_valanars_vengeance |
| 15 | bloodmage_keleseths_calamity |
| 16 | bloodmage_atheranns_anguish |
| 17 | bloodmage_sanguine_rupture |
| 18 | bloodmage_taldarams_torment |
| 19 | bloodmage_shadow_hemorrhage |
| 20 | bloodmage_malediction |
| 21 | bloodmage_vampiric_fang |
| 22 | bloodmage_blood_craving |
| 23 | bloodmage_aneurysm |
| 24 | bloodmage_sacrificial_rite |
| 25 | bloodmage_transgression |
| 26 | bloodmage_blood_curse |
| 27 | bloodmage_accursed_form |
| 28 | bloodmage_veinburst |
| 29 | bloodmage_hemoburst |
| 30 | bloodmage_bloodsurge |
| 31 | bloodmage_final_embrace |
| 32 | bloodmage_endure_the_curse |
| 33 | bloodmage_eternal_curse |
| 34 | bloodmage_rotclaw |
| 35 | bloodmage_blood_howl |
| 36 | bloodmage_bare_fangs |
| 37 | bloodmage_night_hunters_howl |
| 38 | bloodmage_eternal_resolve |
| 39 | bloodmage_monstrous_hunger |
| 40 | bloodmage_hypovolemic_shock |
| 41 | bloodmage_sanguine_mend |
| 42 | bloodmage_heartbreak |
| 43 | bloodmage_hemoglobe |
| 44 | bloodmage_crimson_tide |
| 45 | bloodmage_dark_liturgy |
| 46 | bloodmage_darkfallen_lament |
| 47 | bloodmage_arterial_bind |
| 48 | bloodmage_purify_blood |

---------------------------------------------------------------------
## SHEET 4 - the rest of the kit (13 icons)

PROMPT (paste this whole block):

Generate ONE sprite sheet image, 768x768, a 4 columns x 4 rows grid = 16
separate ability icons (each cell 192x192), of which the last three cells
(bottom right) are left as plain flat magenta with nothing in them. Flat
pure #FF00FF magenta background everywhere. Each icon is centred in its own
cell with a wide margin, not touching or overlapping its neighbours or the
image edge. Painterly semi-realistic World of Warcraft Classic ability-icon
style: one bold symbolic composition per cell, strong readable silhouette,
soft dark outline, chunky simple shapes, soft lighting from the top-left,
no text, no letters, no labels, no grid lines, no frames or borders, no full
human figures and no faces. Vampiric blood magic, arterial red and violet
Shadow. Cells 4 to 13 are melee ATTACKS and must read as distinct attacks
rather than distinct objects. Avoid magenta or pink inside any icon. Row by
row, left to right:

Row 1:
1. a black curse being cut out of a forearm with a knife and held in a fist
2. blood rising just under the surface of the skin in a faint red glow
3. a throat swallowing deeply with red light spilling from the mouth
4. two red puncture holes close together with a thin dark ribbon trailing
   between them

Row 2:
5. a glowing red charge being stored in a cupped hand and pushed outward
6. a film of dried dark blood coating a shoulderplate and a shield rim
7. black thorns pushing outward through pale skin, blood at each tip
8. a single long claw raking down in one straight heavy line

Row 3:
9. a curved claw opening a wound along an old scar line
10. a fanged bite closing with a red thread pulling back out of it
11. two claws punching two deep holes side by side
12. a dense blur of claws filling the cell with no single claw readable

Row 4:
13. a wide-open fanged maw arriving head-on, teeth first
14. nothing - leave this cell plain flat magenta
15. nothing - leave this cell plain flat magenta
16. nothing - leave this cell plain flat magenta

### SHEET 4 slicing map

All go to `assets/icons/abilities/<name>.png`.

| # | File |
|---|---|
| 1 | bloodmage_hemal_excision |
| 2 | bloodmage_sanguine_essence |
| 3 | bloodmage_gorge |
| 4 | bloodmage_vampyrs_kiss |
| 5 | bloodmage_infuse |
| 6 | bloodmage_blood_cursed_armor |
| 7 | bloodmage_bloodthorns |
| 8 | bloodmage_puncturing_fangs |
| 9 | bloodmage_aortic_assault |
| 10 | bloodmage_ravenous_bite |
| 11 | bloodmage_bloodfang_bite |
| 12 | bloodmage_claw_sweep |
| 13 | bloodmage_crimson_maw |
| 14 | (empty) |
| 15 | (empty) |
| 16 | (empty) |

---------------------------------------------------------------------
## The ten that need a generator change as well

These ten abilities carry an explicit `icon_id: "ability_melee"`, which
WINS over the filename fallback - so dropping `bloodmage_lunge.png` in
place changes nothing until that icon_id is gone:

bloodmage_attack, bloodmage_lunge, bloodmage_reave,
bloodmage_ravenous_strike, bloodmage_puncturing_fangs,
bloodmage_aortic_assault, bloodmage_crimson_maw, bloodmage_ravenous_bite,
bloodmage_bloodfang_bite, bloodmage_claw_sweep

Bloodmage HAS a generator, so the fix belongs in
`tools/build_bloodmage.py`, not the JSON: pass `icon=None` on those ten
`ability()` calls and re-run `python3 tools/build_bloodmage.py --apply`.
Editing the JSON directly gets reverted by the next regeneration, which is
why `tools/check_generator_drift.py` exists.

## After generating

Slice all four sheets, key out the magenta, and place the files using the
tables. Then confirm:

```
python3 tools/audit_icon_coverage.py --list bloodmage
```

It should report 0 blank and 0 shared. Anything still listed is a filename
that did not match - usually punctuation, since several display names carry
an apostrophe the id does not (`Valanar's Vengeance` is
`bloodmage_valanars_vengeance`, `One Man's Curse...` is
`bloodmage_accursed_one_mans_curse`).
