"""What build this copy of the game is, and whether a newer one exists.

Kyle, 8 Nov 2026: "on the title page we have a box in the bottom right that
says 'Latest Version: Date' so we can quickly start up the game and see if we
have the latest version."

=============================================================================
THE DISTINCTION THAT MATTERS
=============================================================================

"What am I running" and "is it the latest" are two different questions, and
only the first can be answered offline:

    LOCAL STAMP   the commit this copy was built from, and its date. Always
                  available, instant, no network. Answers "what have I got".
    REMOTE CHECK  whether origin has moved on. Needs the network, so it can
                  be slow, can fail, and must never hold up the title screen.

A box showing only the local stamp does NOT tell you that you are behind -
it tells you what you have, and you would still have to know what the newest
one is to compare. So both are here, and the title screen shows the stamp
immediately and adds the verdict when (or if) it arrives.

=============================================================================
NOTHING HERE MAY BLOCK OR RAISE
=============================================================================

This runs on the path to a title screen that must appear instantly, on two
people's machines, one of which may be offline or have no git at all. Every
function returns a usable value whatever happens:

  - the local stamp falls back from `git log` to a BUILD.txt written at
    package time, then to the mtime of the game's own source, then to
    "unknown". A player who downloaded a zip still sees a date.
  - the remote check runs on a daemon thread with a hard timeout and never
    reports failure as "out of date" - not knowing and being behind are
    different answers, and showing "update available" to someone on a train
    would be worse than showing nothing.
"""
import os
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Hard ceiling on any git call. The title screen is behind this.
_GIT_TIMEOUT = 2.0
#: The remote check gets longer, because it is off-thread and nothing waits.
_FETCH_TIMEOUT = 8.0

_local = None
_remote_state = {"checked": False, "behind": None, "latest_date": None}


def _git(*args, timeout=_GIT_TIMEOUT):
    """Run a git command in the repo. Returns stripped stdout, or None."""
    try:
        out = subprocess.run(
            ("git",) + args, cwd=str(ROOT), timeout=timeout,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    except Exception:
        return None
    if out.returncode != 0:
        return None
    return (out.stdout or "").strip() or None


def local_build():
    """(short_hash, 'YYYY-MM-DD') for this copy. Cached. Never raises."""
    global _local
    if _local is not None:
        return _local

    # 1. a real git clone - the normal case for both of us
    stamp = _git("log", "-1", "--format=%h|%cd", "--date=format:%Y-%m-%d")
    if stamp and "|" in stamp:
        short, date = stamp.split("|", 1)
        _local = (short, date)
        return _local

    # 2. a BUILD.txt written when a copy was packaged, same format
    build_file = ROOT / "BUILD.txt"
    try:
        if build_file.exists():
            text = build_file.read_text().strip()
            if "|" in text:
                short, date = text.split("|", 1)
                _local = (short.strip(), date.strip())
                return _local
    except OSError:
        pass

    # 3. no git and no stamp - date the source itself, so a zip download
    #    still shows something true rather than "unknown"
    try:
        newest = max(p.stat().st_mtime for p in (ROOT / "world").glob("*.py"))
        _local = ("local", time.strftime("%Y-%m-%d", time.localtime(newest)))
    except (OSError, ValueError):
        _local = ("unknown", "unknown")
    return _local


def _check_remote():
    """Ask origin whether it has moved on. Off-thread; sets _remote_state."""
    try:
        # ls-remote rather than fetch: it touches nothing in the working
        # tree, needs no write access, and cannot leave the repo in a
        # half-fetched state if it is interrupted mid-flight.
        head = _git("rev-parse", "HEAD")
        branch = _git("rev-parse", "--abbrev-ref", "HEAD") or "main"
        remote = _git("ls-remote", "origin", branch, timeout=_FETCH_TIMEOUT)
        if not head or not remote:
            return  # stays "unknown", which is NOT "behind"
        remote_head = remote.split()[0]
        _remote_state["behind"] = (remote_head != head)
        _remote_state["latest_date"] = None
    except Exception:
        return
    finally:
        _remote_state["checked"] = True


def start_remote_check():
    """Kick the update check off in the background. Safe to call repeatedly."""
    if _remote_state["checked"] or _remote_state.get("_started"):
        return
    _remote_state["_started"] = True
    try:
        threading.Thread(target=_check_remote, daemon=True).start()
    except Exception:
        _remote_state["checked"] = True


def version_lines():
    """The one or two lines the title screen draws. Never raises.

    Returns (headline, status) where status may be None - and is None both
    while the check is in flight and if it failed, because "I do not know"
    must not read as "you are behind".
    """
    short, date = local_build()
    headline = f"Build {short} - {date}"
    behind = _remote_state.get("behind")
    if behind is True:
        return headline, "Update available"
    if behind is False:
        return headline, "Up to date"
    return headline, None
