# The turn timeline: seeing turn order, and planning it by hovering a spell

Kyle, 20 Nov 2026: "I do want a turn indicator on the right side of combat. Basically a line that's divided into 4 (0,
.25, .5, .75, and 1) with smaller markings at the 1/8ths. Battle turn moves downwards. Allies on the right of the bar and
enemies on the left. And.... (this is a shaman example) if we hover over something like earth shock, we can see our
shamans movement barely goes down, still above enemy 2....but if we go to use lesser healing wave, it places us between
enemy 1 and enemy 2, so we still move before the second enemy....but if we use greater healing wave it pushes down to
last as it's a slow spell. This movement order would have to be visualized by hovering over spells rather than needing
to cast them so we can plan. It'll add another layer of tactics we lack in combat." And: "This let's us actually see
our haste working too."

## What the engine already does (so the bar shows the truth, not a guess)

- **Turns run on a meter**, not rounds (`combat/turn_meter.py`): everyone's meter fills at a rate set by Agility and
  Haste (`turn_speed`), and whoever crosses the threshold first acts.
- **Spells already cost different amounts of time** (`combat/abilities.CAST_SPEEDS`, 15 Nov 2026): a quick spell spends
  0.6 of a turn, a normal one 1.0, a slow one 1.5, and a slow cast can leave the meter below zero, so the slow caster
  waits longer for the next turn. The tooltip already says "Quick cast" or "Slow cast".
- **Haste is live**: buffs and debuffs change `turn_speed` every tick.

So where anyone's next turn falls is already computable: time to act = (threshold - meter) / fill rate. After a spell
with speed s, the caster's meter is (meter - threshold x s), and the same sum says where they land.

## The bar

Kyle, 20 Nov 2026: "the order flows down like water. Whoever is at the top is last, whoever is at the bottom is moving
next."

- A vertical line down the right side of the combat screen. **The bottom is now: whoever is lowest moves next.** Every
  marker drifts down as the meters fill, like water running down the bar, and acts when it reaches the bottom.
- **Acting sends you back up**: after your turn your marker rises to where your next turn falls, and the further away
  that turn is, the higher you go. The top is last.
- Marks at 0 (the bottom), 0.25, 0.5, 0.75 and 1 (the top), and smaller ticks at every eighth.
- **Allies' markers sit to the right of the line and enemies' to the left**, each a small portrait at the height of
  their next turn.
- **The scale:** 1 is one full turn at normal speed for the slowest living combatant, so the bar always shows at least
  everyone's next turn; anything later than 1 (a slow cast on a slow character) sits at the very top with an arrow,
  which is what "pushes down to last" looks like.
- Haste shows as speed: a hasted ally's marker falls faster than everyone else's.

## Hovering a spell

Hovering an ability on the action bar (or a target, for spells that need one) draws a **ghost** of the current actor's
marker where they'd land after casting it, with the other markers unmoved, so you can read off who you'd still beat.
In Kyle's example: Earth Shock (quick) sends the shaman only a little way up, still below enemy 2, so the shaman
moves before them; Lesser Healing Wave (normal) lands between enemy 1 and enemy 2; Greater Healing Wave (slow) sends
the shaman to the top, last. Nothing is spent until you cast.

What the ghost includes: the spell's cast speed, and any haste it changes on the caster (a self-haste buff moves the
ghost up). What it doesn't promise: enemy stuns, slows and haste that haven't happened yet. The bar shows the future as
it stands.

## What it needs

1. **A speed pass over every class.** Only hunters, priests and mages tag `cast_speed` today. For the bar to mean
   something every class's kit needs quick, normal and slow spells, the way Kyle's shaman example has them: instant
   shocks quick, the small heal normal, the big heal and long nukes slow. A rule per class, written into its data and
   checked by a QA.
2. **The preview maths** in `combat/turn_meter.py`: next-turn time for each combatant, and the same for the actor after
   a hypothetical spell (speed, plus any haste the spell grants the caster).
3. **The bar** in `ui/screens/combat_screen.py`, on the right edge, with the ghost on hover.
4. **Checks**: the bar's order matches the order turns actually happen in a simulated fight; the ghost's place matches
   where the actor really lands after casting.
5. **Tuning**: the sims (`tools/sim_viability.py`) re-run after the speed pass, since slow heals and quick shocks change
   how fights pace.

Kyle's call on the scale if he'd rather it be fixed (always one turn) than follow the slowest combatant.
