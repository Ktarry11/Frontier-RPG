"""What an NPC builder may still change once a record exists (backlog, 14 Nov: "fix out of date scripts").

The town builders and syncs (tools/build_*_npcs.py, tools/sync_*_npcs.py, ...) were written to
create a town's people and stand them where the layout says. After they ran, later passes kept
working on the same records: the vendor stock overhaul re-levelled shops and swapped their stock,
the voice passes rewrote greetings, the art passes re-picked faces, the gear-sets pass added
Artifact Keepers, the secrets passes added hidden sellers, the quest-hub pass moved givers into
other towns. Re-running an old builder undid all of that, and the syncs that "prune ghosts"
deleted every hidden seller and Artifact Keeper standing in their town.

THE RULE NOW. A builder still CREATES a record it names and nobody has made yet, with every field
it knows. For a record that already exists it only moves the person: the layout owns where people
stand (x, y). Everything else - who they are, what they say, what they sell, what they look like -
belongs to the data once the record exists, and a builder never writes it again. A builder never
deletes anybody: a record in its town that its roster doesn't name is reported, not removed,
because the likeliest reason is that a later pass put it there on purpose.

To change a field on an existing person, edit the data (or the pass that owns that field), not the
builder.
"""

#: Fields a builder may write on a record that already exists.
LAYOUT_OWNS = ("x", "y")


def safe_update(rec, new):
    """Apply a builder's view of an existing record: positions only, plus any field the record
    doesn't have yet. Returns the number of fields changed."""
    n = 0
    for k, v in new.items():
        if (k in LAYOUT_OWNS or k not in rec) and rec.get(k) != v:
            rec[k] = v
            n += 1
    return n


def merge(existing, new):
    """{**existing, **new} with the same rule: the new record only adds missing fields and moves."""
    out = dict(existing)
    safe_update(out, new)
    return out


def may_write(rec, key):
    """True when a builder may set rec[key] on a record that already exists."""
    return key in LAYOUT_OWNS or key not in rec


def report_extras(extras, label):
    """A builder's town holds people its roster doesn't name. Say so; delete nobody."""
    if extras:
        print(f"{label}: {len(extras)} record(s) here that this roster doesn't name, left alone "
              f"(added by a later pass): {extras[:8]}{' ...' if len(extras) > 8 else ''}")
