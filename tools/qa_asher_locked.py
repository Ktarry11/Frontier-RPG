#!/usr/bin/env python3
"""Asher Coleman's player-facing text is FROZEN. This fails if a byte moves.

Kyle's standing rule has always been that Asher stays byte-identical. As of
2026-10-31 there is a reason that outranks "it is already good":

    Kyle: "Asher will be a raid later. He murdered his family right before the
    integration." And immediately after: "No, NO ONE knows that yet. So no
    hints of it in the lore until later."

His current text is built for that reveal precisely BECAUSE it hints at nothing.
Read cold it is warmth. Read again afterwards it is a man who cannot say one
thing about himself: no adjustment year when every other transplant can name
theirs, never a stated want in three years, tells you about the place and not
himself, turns every question back on the asker, and will not go home.

That only works if the text is left exactly alone. The risk is not malice, it
is helpfulness - some future pass "enriching" his background, or a sweep like
this session's own description rewrites catching him by accident. A hash is the
cheapest thing that notices.

If this check fails and the change was deliberate, update EXPECTED below in the
same commit and say in the message what moved and why.
"""
import sys, os, json, hashlib, pathlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Fields a player can actually read. Stats and placement are free to change;
#: the WORDS are what is frozen.
TEXT_FIELDS = ("name", "greeting", "backstory")

EXPECTED = "c1c4cc4d14c96e07dce147b78b55ac46b46e9670b8836a4aa3efc5c1e9e7a7e4"


def asher_text():
    doc = json.load(open(ROOT / "data/npcs/recruits.json"))
    rs = doc["recruits"] if isinstance(doc, dict) and "recruits" in doc else doc
    it = rs if isinstance(rs, list) else list(rs.values())
    for r in it:
        if r.get("recruit_id") == "asher_coleman":
            parts = [str(r.get(f, "")) for f in TEXT_FIELDS]
            secs = r.get("background_sections") or {}
            for k in sorted(secs):
                parts.append(f"{k}:{secs[k]}")
            return "\n".join(parts)
    return None


def main():
    text = asher_text()
    if text is None:
        print("  FAIL - asher_coleman is not in recruits.json at all")
        return 1
    got = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print(f"  asher_coleman text sha256: {got}")
    if EXPECTED == "SET_ON_FIRST_RUN":
        print("\n  EXPECTED is unset. Paste the hash above into EXPECTED and re-run.")
        return 1
    if got != EXPECTED:
        print(f"  expected:                  {EXPECTED}")
        print("\n  FAIL - Asher's player-facing text changed.")
        print("  His text is frozen because it is the setup for a later raid reveal that")
        print("  nothing in the game may hint at yet. If this was deliberate, update")
        print("  EXPECTED in this file in the same commit.")
        return 1
    print("\nPASS - unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
