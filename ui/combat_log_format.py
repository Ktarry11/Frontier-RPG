"""How a combat-log message reads on screen (Kyle, 26 Nov 2026: "Can we make combat text easier to read").

The log used to colour a line by one test: green if it started with the hero's name, red if it started with the
FIRST enemy's name, white otherwise. So a recruit's heal, an add's bite, a DoT tick and "Targeting cancelled" all
came out the same white, and one area attack became a five-line red paragraph listing every name in full.

Now each message gets:
  - a colour for what it is: the party acting, a heal, an enemy acting, a death or the end of the fight, and the
    small stuff (ticks, fades, prompts) muted so the actions stand out;
  - its numbers drawn brighter than the words around them, so the eye lands on how much;
  - an area attack split into a header and a short list of who took what, by first name.

format_message() returns the message as lines of (text, colour) segments; the combat screen wraps and draws them.
Pure text in, segments out, so it can be checked without a screen.
"""
import re

# colours: words, then the brighter colour their numbers take
PARTY = ((225, 225, 215), (255, 214, 110))          # what the party does; numbers gold
HEAL = ((150, 225, 150), (190, 255, 170))           # healing, whoever casts it
ENEMY = ((236, 128, 116), (255, 190, 175))          # what enemies do to you
BIG = ((255, 170, 70), (255, 200, 120))             # someone falls, victory, defeat
MUTED = ((150, 150, 162), (190, 190, 200))          # ticks, fades, gains, prompts, system notes

NUMBER = re.compile(r"\d+")
AOE = re.compile(r"^(?P<who>.+?) uses (?P<what>.+?) on everyone \((?P<hits>.*)\)(?P<rest>.*)$")
AOE_HIT = re.compile(r"(?P<n>\d+) to (?P<name>[^,()]+)")

#: small stuff: the log keeps it, but it shouldn't compete with the actions
QUIET = re.compile(r"(fades from|suffers \d+ \w* ?damage from|gains |is afflicted|click (?:a|an) |cancelled|"
                   r"is empty|not your party's turn|waits\.|hesitates|is stunned and loses|Auto-slotted|"
                   r"Combat started|^Slot )")
ACTION = re.compile(r" (uses|casts|attacks|strikes|hits|shoots|bites|afflicts) ")
LOUD = re.compile(r"(has fallen|is laid to rest|Victory|Defeat|wiped out|is slain|dies\b)")


def _first(name):
    """First name for a crowded list: "Sebastian Cruz" -> "Sebastian", "Mechano-Bear" stays."""
    return name.split()[0] if " " in name.strip() else name.strip()


def kind_of(msg, allies=(), enemies=()):
    """Which palette a message takes."""
    if LOUD.search(msg):
        return BIG
    # an action is never small stuff, even when it also afflicts someone ("uses Nightmare Sleep ... is afflicted")
    if QUIET.search(msg) and not ACTION.search(msg):
        return MUTED
    low = msg.lower()
    if "heal" in low or "restores" in low:
        return HEAL
    for name in sorted(enemies, key=len, reverse=True):
        if name and msg.startswith(name):
            return ENEMY
    for name in sorted(allies, key=len, reverse=True):
        if name and msg.startswith(name):
            return PARTY
    return MUTED


def segments(text, palette):
    """Split one line into (text, colour) runs, numbers in the palette's bright colour."""
    words, bright = palette
    out, at = [], 0
    for m in NUMBER.finditer(text):
        if m.start() > at:
            out.append((text[at:m.start()], words))
        out.append((m.group(0), bright))
        at = m.end()
    if at < len(text):
        out.append((text[at:], words))
    return out or [("", words)]


def format_message(msg, allies=(), enemies=()):
    """-> (palette, [line text, ...]). An area attack becomes a header and a list of who took what."""
    palette = kind_of(msg, allies, enemies)
    m = AOE.match(msg)
    if m:
        hits = [(h.group("name").strip(), h.group("n")) for h in AOE_HIT.finditer(m.group("hits"))]
        if hits:
            lines = [f"{m.group('who')} uses {m.group('what')} on everyone:"]
            lines.append("    " + "  |  ".join(f"{_first(n)} {v}" for n, v in hits))
            rest = m.group("rest").strip(" !")
            if rest:
                lines.append("    " + rest)
            return palette, lines
    return palette, [msg]
