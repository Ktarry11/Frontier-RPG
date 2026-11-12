"""
Party system. The player plus up to four recruited companions.

Design (per Kyle's direction):
  - **Max 5 in the active party**, player included, matching WoW's 5-man.
  - Companions are full `Character` objects - they gear up, level up, and use
    the exact same ability/resource/talent systems the player does. There is
    deliberately no parallel "companion" class to maintain.
  - The player controls every party member in combat, FF-style. There is NO
    companion AI: each member takes their own turn on the shared turn meter
    and the player chooses the action.
  - Companions are **spec-locked** - class and spec are fixed at recruitment
    and are their identity ("loved healing on Earth, now a Resto Druid").
    They still earn talent points, but spend them in their one tree. This
    also expresses the Players-vs-Natives lore: the player is malleable,
    everyone else has settled into who they are.
  - Recruits beyond the active five sit on the **bench**. Benched members
    gain reduced XP (BENCH_XP_RATIO) so they fall behind but never become
    unusable dead weight.

ROWS
Rows are **soft**: every ability stays usable from either row, and position
only applies damage modifiers. Back row takes less melee/physical damage and
more ranged/spell damage; front row is the reverse. This gives positioning
real weight without the fiddly "you can't reach from there" rules that make
strict-row systems annoying in a game where you control everyone.
"""

FRONT_ROW = "front"
BACK_ROW = "back"

#: Hard cap on the active party, player included.
MAX_PARTY_SIZE = 5

#: Share of XP a benched (recruited but not active) member earns.
BENCH_XP_RATIO = 0.5

#: A ROW IS A POSITION, NOT A MULTIPLIER. Kyle, 6 Nov: "We can remove the
#: things from front/back from our guys. The armor and resistances are baked
#: into the classes."
#:
#: This used to hold front 1.15 physical / 0.95 magic and back 0.70 / 1.05,
#: written when rows were soft and a back-row character could still be
#: reached by anything. combat/rows.py made rows a hard reach gate - melee
#: cannot touch the back row at all while the front row stands - so the 0.70
#: was protecting a character who was already unreachable, on top of the
#: lighter armour their class already gives them. It paid twice for one
#: decision.
#:
#: Kept as an empty mapping rather than deleted so row_damage_multiplier
#: keeps its shape for any caller that still asks.
ROW_DAMAGE_MODIFIERS = {}

#: Which row a class defaults to when recruited or created. Melee and tanks
#: hold the line; casters and ranged sit behind it. The player can move
#: anyone afterwards - this is only the sensible starting arrangement.
DEFAULT_ROW_BY_CLASS = {
    "Warrior": FRONT_ROW,
    "Paladin": FRONT_ROW,
    "Rogue": FRONT_ROW,
    "Druid": FRONT_ROW,
    "Shaman": FRONT_ROW,
    "Hunter": BACK_ROW,
    "Priest": BACK_ROW,
    "Mage": BACK_ROW,
    "Warlock": BACK_ROW,
    "Stormbringer": BACK_ROW,
    "Tinker": BACK_ROW,
    # Venomancer's default row is a compromise across 4 very different specs
    # (Fortitude=tank/front, Stalking=melee/front, Venom+Vizier=caster/back) -
    # front row picked since melee/tank specs benefit more from a wrong
    # DEFAULT than casters do (a caster in front just takes more damage; a
    # tank/melee character stuck in back can't do its job at all). Player
    # can always move a Venomancer to back row for Venom/Vizier specs.
    "Venomancer": FRONT_ROW,
    "Primalist": FRONT_ROW,
    # Runemaster's default row is a compromise across 3 specs: Engravement
    # and Riftblade are melee (2 of 3), Glyphic is ranged caster (1 of 3) -
    # front row picked since it's the majority case and matches Venomancer's
    # same logic (a caster in front just takes more damage; a melee
    # character stuck in back can't function at all).
    "Runemaster": FRONT_ROW,
    # Cultist's default row is a compromise across 4 specs: Godblade and
    # Dreadnought are melee/tank (2 of 4), Corruption is ranged caster,
    # Heretic is healer - front row picked since the melee/tank majority
    # benefits more from a wrong default than the ranged/healer specs do.
    "Cultist": FRONT_ROW,
    # Starcaller's default row is a compromise across 4 specs: Moon Guard
    # (tank) and Warden (melee) are front-line (2 of 4), Sentinel (ranged)
    # and Moon Priest (healer) are back-line - front row picked as the
    # majority-melee default, matching the same logic used for every other
    # mixed-role CoA class this session.
    "Starcaller": FRONT_ROW,
    # Sun Cleric's default row is a compromise across 4 specs: Valkyrie
    # (melee) and Seraphim (tank) are front-line (2 of 4), Piety (ranged)
    # and Blessings (healer) are back-line - front row picked as the
    # majority default, matching every other mixed-role CoA class tonight.
    "Sun Cleric": FRONT_ROW,
    # Guardian needs no compromise, unlike every mixed-role CoA class above:
    # all three specs fight in melee with a shield. Vanguard tanks,
    # Gladiator is melee DPS, and Inspiration is a support that CoA
    # describes as "literally standing in melee with a shield and a
    # block-rating stat".
    "Guardian": FRONT_ROW,
}


def default_row_for(char_class):
    """Starting row for a class (front for melee, back for casters/ranged)."""
    # Keyed by display name ("Sun Cleric") while char_class is the id ("sun_cleric"), so a
    # plain .get() missed for EVERY class and silently put the whole roster in the front row -
    # the back-row casters included. Same family as the spellbook-tab and class-icon bugs; see
    # core/class_names.py.
    from core.class_names import lookup
    return lookup(DEFAULT_ROW_BY_CLASS, char_class, FRONT_ROW)


def row_damage_multiplier(row, damage_type="physical"):
    """Incoming-damage multiplier for a combatant standing in `row`."""
    if damage_type not in ("physical", "magic"):
        damage_type = "physical"
    return ROW_DAMAGE_MODIFIERS.get((row, damage_type), 1.0)


class Party:
    """
    The player's active party and bench.

    `members` is the active party in turn-display order, ALWAYS containing the
    player at index 0. `bench` holds recruited-but-inactive companions.
    """

    def __init__(self, player):
        self.player = player
        self.members = [player]
        self.bench = []
        if not getattr(player, "row", None):
            player.row = default_row_for(player.char_class)

        # Shared party purse (per Kyle's "shared money in party when
        # selling" direction). Currency used to live on Character.copper,
        # which worked by accident since only the player ever spent/earned
        # it - now that gear/consumables are per-character (each companion
        # is their "own real person" with their own stuff), money is the
        # one thing that stays pooled: the party splits a shared wallet,
        # not everyone's individual belongings. See add_currency/
        # remove_currency/get_currency_string below - these replace the
        # identically-named Character methods, which are now removed.
        self.copper = 0
        # Shared overflow storage, for the same reason the purse is shared - see entities/bank.py.
        from entities.bank import Bank
        self.bank = Bank()

    # ------------------------------------------------------------------
    # Roster management
    # ------------------------------------------------------------------

    def is_full(self):
        return len(self.members) >= MAX_PARTY_SIZE

    def all_recruits(self):
        """Every companion the player owns, active or benched (not the player)."""
        return [m for m in self.members if m is not self.player] + list(self.bench)

    def add_member(self, character):
        """
        Add a recruit. Goes into the active party if there's room, otherwise
        onto the bench. Returns the string "active" or "bench".
        """
        if not getattr(character, "row", None):
            character.row = default_row_for(character.char_class)

        if self.is_full():
            self.bench.append(character)
            return "bench"
        self.members.append(character)
        return "active"

    def remove_member(self, character):
        """Remove a companion entirely. The player can never be removed."""
        if character is self.player:
            return False
        if character in self.members:
            self.members.remove(character)
            return True
        if character in self.bench:
            self.bench.remove(character)
            return True
        return False

    def bench_member(self, character):
        """Move an active companion to the bench."""
        if character is self.player or character not in self.members:
            return False
        self.members.remove(character)
        self.bench.append(character)
        return True

    def activate_member(self, character):
        """Move a benched companion into the active party if there's room."""
        if character not in self.bench or self.is_full():
            return False
        self.bench.remove(character)
        self.members.append(character)
        return True

    def set_row(self, character, row):
        """Move a member between front and back row."""
        if row not in (FRONT_ROW, BACK_ROW):
            return False
        character.row = row
        return True

    # ------------------------------------------------------------------
    # Combat helpers
    # ------------------------------------------------------------------

    def living_members(self):
        return [m for m in self.members if m.is_alive()]

    def is_wiped(self):
        """True when every active member is down - this is a party defeat."""
        return not self.living_members()

    def front_line(self):
        return [m for m in self.members if getattr(m, "row", FRONT_ROW) == FRONT_ROW]

    def back_line(self):
        return [m for m in self.members if getattr(m, "row", FRONT_ROW) == BACK_ROW]

    #: What a wipe costs: this share of each member's progress through their current level.
    WIPE_XP_LOSS = 0.15

    def fallen_members(self):
        return [m for m in self.members if not m.is_alive()]

    def wipe_penalty(self):
        """The whole group is down. Everyone loses WIPE_XP_LOSS of their experience and gets
        back up. Returns [(member, xp_lost), ...].

        Kyle, 12 Nov 2026: "When people all die the entire group loses 15% of their EXP."
        `experience` is progress through the CURRENT level, so nobody loses a level over it -
        the bar slides back and that is all.
        """
        out = []
        for member in self.members:
            lost = int(round(max(0, getattr(member, "experience", 0)) * self.WIPE_XP_LOSS))
            member.experience = max(0, getattr(member, "experience", 0) - lost)
            member.current_health = member.health
            if hasattr(member, "current_mana"):
                member.current_mana = getattr(member, "mana", 0)
            if hasattr(member, "current_rage"):
                member.current_rage = 0
            if hasattr(member, "current_energy"):
                member.current_energy = 100
            out.append((member, lost))
        return out

    def restore_after_combat(self):
        """
        Strip everything that belonged to the fight off everyone once it ends - see
        StatusEffectMixin.clear_combat_effects for what goes and what stays. Long buffs on a
        real-time clock (Fortitude, Might, Mark of the Wild) are deliberately left running.

        Bench included: a member swapped out mid-dungeon must not carry a boss's debuff on the
        bench. And stats are recalculated, because the effects removed here now include ones
        with stat_mods - without it a cleared debuff's penalty would stay baked into the sheet.
        """
        for member in list(self.members) + list(getattr(self, "bench", []) or []):
            if hasattr(member, "clear_combat_effects"):
                member.clear_combat_effects()
                if hasattr(member, "_recalculate_derived_stats"):
                    member._recalculate_derived_stats()

    # ------------------------------------------------------------------
    # Progression
    # ------------------------------------------------------------------

    def award_experience(self, amount):
        """
        Give XP to the whole roster. Active members earn full value; benched
        members earn BENCH_XP_RATIO of it so they trail without rotting.

        Returns [(member, levels_gained), ...] for members who levelled, so
        the combat log can announce them.
        """
        levelled = []
        for member in self.members:
            # THE DEAD LEARN NOTHING. Kyle, 12 Nov 2026: "IF one character is alive after a
            # win, only that character gets exp for the kill." It also keeps a level-up's
            # full heal from being a free resurrection.
            if not member.is_alive():
                continue
            gained = member.gain_experience(amount)
            if gained:
                levelled.append((member, gained))

        bench_amount = int(amount * BENCH_XP_RATIO)
        if bench_amount > 0:
            for member in self.bench:
                if not member.is_alive():
                    continue
                gained = member.gain_experience(bench_amount)
                if gained:
                    levelled.append((member, gained))
        return levelled

    # ------------------------------------------------------------------
    # Shared currency
    # ------------------------------------------------------------------

    def add_currency(self, amount_copper):
        """Add copper to the party's shared purse."""
        self.copper += amount_copper
        return True

    def remove_currency(self, amount_copper):
        """Spend copper from the shared purse. Returns True if successful."""
        if self.copper >= amount_copper:
            self.copper -= amount_copper
            return True
        return False

    def get_currency_string(self):
        """'45g 30s 75c' - full width on purpose, so the HUD purse does not twitch as you spend."""
        from entities.coins import coins
        return coins(self.copper, full=True)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self):
        """
        Serialize companions only. The player is saved separately by
        SaveSystem and re-attached on load, so they're never stored twice.
        Currency IS stored here (not on the player) - it's the party's
        shared purse, not the player's personal money. Old saves (pre-purse)
        have no "copper" key at all; from_dict below migrates their
        player.copper into the new shared purse rather than losing it.
        """
        return {
            "members": [m.to_dict() for m in self.members if m is not self.player],
            "bench": [m.to_dict() for m in self.bench],
            "rows": {m.name: getattr(m, "row", FRONT_ROW)
                     for m in [self.player] + self.all_recruits()},
            "copper": self.copper,
            "bank": self.bank.to_dict(),
        }

    @classmethod
    def from_dict(cls, data, player):
        from entities.character import Character

        party = cls(player)
        for entry in data.get("members", []):
            party.members.append(Character.from_dict(entry))
        for entry in data.get("bench", []):
            party.bench.append(Character.from_dict(entry))

        # A save written before the bank existed simply has no "bank" key and gets a fresh empty one
        # with its single free tab - there is no migration to write.
        if "bank" in data:
            from entities.bank import Bank
            party.bank = Bank.from_dict(data["bank"])

        if "copper" in data:
            party.copper = data["copper"]
        else:
            # Pre-shared-purse save (currency used to live on
            # Character.copper). Migrate whatever the player was carrying
            # into the new shared purse instead of it just vanishing on
            # first load after this change. Companions never had their own
            # copper under the old model (only the player ever spent/
            # earned it), so there's nothing to collect from them.
            party.copper = getattr(player, "copper", 0)

        # Row now round-trips on the Character itself (save v6). The
        # name-keyed `rows` map is only consulted for v5 saves, where it was
        # the sole record - and it breaks if two members share a name, which
        # is exactly why the authoritative copy moved onto the Character.
        rows = data.get("rows", {})
        for member in [player] + party.all_recruits():
            if not getattr(member, "row", None):
                member.row = rows.get(
                    member.name, default_row_for(member.char_class))
        return party
