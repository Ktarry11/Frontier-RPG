#!/usr/bin/env python3
"""Group lines (the interactive party): tools/group_lines/<recruit_id>.json -> data/npcs/group_lines.json, checked on the way.

    python3 tools/build_group_lines.py            check and write
    python3 tools/build_group_lines.py --check    check only (QA)

Each recruit file: {"voice": "<recruit_id>.voice.md", "arc": {"shape", "alt"} or {"anchor": true},
"lines": {key: str | [str, ...]}, "history": [conversation], "milestones": {kind: conversation}}.
Shared: tools/group_lines/_arguments.json (authored arguments between two recruits) and _orientation.json (from the recruit
profiles tracker, Kyle's cast of 19 Nov 2026; anyone not listed is straight).

The voice guard (claude/group_dynamics_plan.md, "113 people, not one writer in 113 hats"):
  every required key present; ASCII; no dashes; no one- or two-word sentences; at most 30% of a recruit's lines open
  with "I"; {name} only where a line is said to someone; a kill list of the writer's tics; and no 4-word run shared by
  three or more recruits. A voice sheet must exist before a recruit's lines count.
"""
import json
import re
import sys
from itertools import chain
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "group_lines"
OUT = ROOT / "data" / "npcs" / "group_lines.json"

KINDS = ("sharp", "kind", "funny", "brave", "steady", "clever", "honest", "quiet", "fierce", "warm")
REQUIRED = (
    # the group
    "g_roast", "g_fire_back", "g_pile_on", "g_peacemake", "g_take_side", "g_left_out", "g_include", "g_bad_plan",
    "g_plan_yes", "g_plan_no", "g_hype", "g_toast", "g_cheers", "g_quiet_line", "g_after_wipe", "g_crew",
    "g_exasperated",
    # love, hate, shades of grey
    *[f"g_love_{k}" for k in KINDS], "g_loved", *[f"g_hate_{k}" for k in KINDS], "g_respect",
    "g_call_out", "g_stung", "g_concede", "g_nod",
    # growth and the room
    "g_callback_save", "g_callback_clutch", "g_callback_callout", "g_former_rivals", "g_changed",
    "g_unguarded", "g_clipped", "g_noticed_open",
    # arguments with the player
    "arg_ask", "arg_backed_me", "arg_backed_them", "arg_stayed_out", "arg_always_their_side", "arg_wallflower",
    "arg_reject", "arg_grumble", "arg_settled",
    # reputation and delayed consequences
    "seen_listens", "seen_truth", "seen_jokes", "seen_stays_out", "seen_biased", "seen_harsh",
    "seed_right", "seed_remember", "seed_wrong",
    # talking to the player
    "talk_aftermath_near_death", "talk_aftermath_wipe", "talk_aftermath_blame_self", "talk_aftermath_first_clear",
    "talk_development",
    "talk_relationship_hard_on", "talk_relationship_likes_me", "talk_relationship_respect_hate",
    "talk_relationship_acting_off",
    "talk_confrontation_favour", "talk_confrontation_dislike", "talk_confrontation_risks",
    "talk_confrontation_wrong", "talk_confrontation_trust", "talk_confrontation_decided",
    *[f"talk_{f}_{k}" for f in ("lands", "shrug", "stings") for k in ("aftermath", "development", "relationship",
                                                                       "confrontation")],
    "talk_door_closed",
)
#: keys that need two or more lines, because they come up often
TWICE = ("g_roast", "g_fire_back", "g_pile_on", "g_loved", "g_unguarded", "arg_ask")
ARC_KEYS = ("arc_cracks", "arc_turn", "arc_become", "arc_failed")
#: the lines an arc's Become replaces: each arc recruit writes "<key>_after" for these
AFTER = ("g_roast", "g_after_wipe", "g_toast", "g_crew", "g_quiet_line", "g_loved")
#: keys said TO someone, so {name} is allowed
NAMED = re.compile(r"^(g_love_|g_hate_|g_respect|g_nod|g_call_out|g_stung|g_concede|g_callback_|g_former_rivals|"
                   r"g_admire|g_include|arg_|talk_relationship_|talk_confrontation_(favour|dislike|wrong|decided)|"
                   r"talk_aftermath_blame_self|talk_(lands|shrug|stings)_relationship|milestone|g_take_side)")
KILL = ("for what it's worth", "if i'm honest", "i'll hold you to it", "for the record", "here's the thing",
        "let's be real", "i'm not going to lie", "you know what", "honestly,", "at the end of the day",
        "to be fair", "not gonna lie", "i mean,")
STOP = {"the", "a", "an", "and", "of", "to", "in", "i", "you", "it", "is", "that", "my", "your", "me", "on", "for",
        "this", "with", "we", "be", "at", "if", "so", "but", "was", "are", "not", "just", "all", "do", "one"}
I_CAP = 0.30


def texts(v):
    return v if isinstance(v, list) else [v]


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.replace("{player}", "Kyle").replace("{name}", "Sam"))
            if s.strip()]


def check_line(rid, key, t, bad):
    where = f"{rid} {key}"
    if not t or not t.strip():
        bad.append(f"{where}: empty")
        return
    try:
        t.encode("ascii")
    except UnicodeEncodeError:
        bad.append(f"{where}: not ASCII: {t[:60]}")
    if "—" in t or "–" in t or re.search(r"\w\s-\s\w", t) or "--" in t:
        bad.append(f"{where}: a dash: {t[:60]}")
    if "{name}" in t and not NAMED.match(key):
        bad.append(f"{where}: {{name}} in a line that isn't said to anyone")
    low = t.lower()
    for k in KILL:
        if k in low:
            bad.append(f"{where}: writer's tic '{k}'")
    for s in sentences(t):
        words = re.findall(r"[A-Za-z']+", s)
        if len(words) < 3:
            bad.append(f"{where}: a one- or two-word sentence '{s}'")


def conv_lines(conv):
    yield conv.get("open", "")
    for o in conv.get("options", []):
        yield o.get("reply", "")


def load():
    files = sorted(p for p in SRC.glob("*.json") if not p.name.startswith("_"))
    data = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in files}
    args = json.loads((SRC / "_arguments.json").read_text(encoding="utf-8")) if (SRC / "_arguments.json").exists() \
        else []
    orient = json.loads((SRC / "_orientation.json").read_text(encoding="utf-8")) \
        if (SRC / "_orientation.json").exists() else {}
    return data, args, orient


def check(data, args, orient):
    bad = []
    grams = {}
    for rid, d in data.items():
        if not (SRC / f"{rid}.voice.md").exists():
            bad.append(f"{rid}: no voice sheet ({rid}.voice.md) - write the voice before the lines")
        lines = d.get("lines") or {}
        arc = d.get("arc") or {}
        need = list(REQUIRED)
        if arc.get("anchor"):
            need.append("anchor_notice")
        elif arc:
            need += list(ARC_KEYS) + [f"{k}_after" for k in AFTER]
            if arc.get("alt"):
                need += ["alt_turn", "alt_become"]
        else:
            bad.append(f"{rid}: no arc (a shape, or anchor: true)")
        if orient.get(rid):
            need.append("g_admire")
        for k in need:
            if not lines.get(k):
                bad.append(f"{rid}: missing {k}")
        for k in TWICE:
            if lines.get(k) and len(texts(lines[k])) < 2:
                bad.append(f"{rid}: {k} needs two lines, it comes up often")
        all_texts = []
        for k, v in lines.items():
            for t in texts(v):
                check_line(rid, k, t, bad)
                all_texts.append(t)
        for conv in d.get("history") or []:
            for t in conv_lines(conv):
                check_line(rid, f"history {conv.get('id')}", t, bad)
                all_texts.append(t)
        for kind, conv in (d.get("milestones") or {}).items():
            for t in conv_lines(conv):
                check_line(rid, f"milestone {kind}", t, bad)
                all_texts.append(t)
        opens_i = sum(1 for t in all_texts if re.match(r"^I\b|^I'", t.strip()))
        if all_texts and opens_i / len(all_texts) > I_CAP:
            bad.append(f"{rid}: {opens_i} of {len(all_texts)} lines open with 'I' (cap {int(I_CAP * 100)}%)")
        seen = set()
        for t in all_texts:
            w = [x for x in re.findall(r"[a-z']+", t.lower())]
            for i in range(len(w) - 3):
                g = tuple(w[i:i + 4])
                if sum(1 for x in g if x not in STOP) >= 3:
                    seen.add(g)
        for g in seen:
            grams.setdefault(g, set()).add(rid)
    for g, who in grams.items():
        if len(who) >= 3:
            bad.append(f"shared phrasing across {len(who)} recruits: '{' '.join(g)}' ({', '.join(sorted(who))})")
    ids = set(data)
    for a in args:
        for rid in a.get("between", []):
            if rid not in ids:
                bad.append(f"argument {a.get('id')}: {rid} has no wave 4 file")
        for rid, t in a.get("lines", []):
            check_line(rid, f"argument {a.get('id')}", t, bad)
        if set(a.get("sides", {})) != set(a.get("between", [])):
            bad.append(f"argument {a.get('id')}: sides must name both people")
    return bad


def build(data, args, orient):
    return {"lines": {rid: d.get("lines") or {} for rid, d in data.items()},
            "arcs": {rid: d.get("arc") or {} for rid, d in data.items()},
            "orientation": {rid: o for rid, o in orient.items() if rid in data},
            "history": {rid: d.get("history") or [] for rid, d in data.items()},
            "milestones": {rid: d.get("milestones") or {} for rid, d in data.items()},
            "arguments": args}


def main():
    data, args, orient = load()
    bad = check(data, args, orient)
    for b in bad:
        print("  FAIL", b)
    n = sum(len(texts(v)) for d in data.values() for v in (d.get("lines") or {}).values())
    print(f"group lines: {len(data)} recruits, {n} lines, {len(args)} arguments; {'FAILED' if bad else 'ok'}")
    if bad:
        return 1
    if "--check" not in sys.argv:
        OUT.write_text(json.dumps(build(data, args, orient), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
